"""
Core search orchestration service for Smart Buy.

Calls all configured providers in parallel (thread pool), aggregates results,
calculates discounts, ranks offers, saves search history to DB.
"""
import concurrent.futures
from datetime import datetime
from typing import List, Optional

from backend.smart_buy.providers import get_all_providers
from backend.smart_buy.services.discount_calculator import (
    enrich_offers, rank_offers, tag_best_discount
)
from backend.smart_buy.services.product_matcher import match_offers_to_groups
from backend.smart_buy.services.query_parser import parse_query


def _search_provider(provider, query: str, filters: dict) -> List[dict]:
    """Call a single provider safely; return [] on any error."""
    try:
        if not provider.is_available():
            return []
        return provider.search(query, **filters) or []
    except Exception:
        return []


def search_products(
    query: str,
    sort_by: str = "highest_discount",
    budget_max: Optional[float] = None,
    platforms: Optional[List[str]] = None,
    user_id: Optional[int] = None,
) -> dict:
    """
    Main entry point for a Smart Buy search.

    Args:
        query:      Raw user search string.
        sort_by:    One of highest_discount|lowest_price|highest_rating|newest.
        budget_max: Maximum price filter (INR).
        platforms:  List of platform_ids to include; None = all.
        user_id:    Authenticated user id for search history.

    Returns a dict:
        {
          "query": str,
          "parsed_intent": dict,
          "offers": List[dict],
          "providers_checked": List[dict],
          "total_offers": int,
          "search_id": int | None,
        }
    """
    # 1. Parse query
    parsed = parse_query(query)
    effective_budget = budget_max or parsed.get("budget_max")

    filters = {}
    if effective_budget:
        filters["budget_max"] = effective_budget
    if parsed.get("category"):
        filters["category"] = parsed["category"]

    # 2. Get providers
    all_providers = get_all_providers()
    if platforms:
        all_providers = [p for p in all_providers if p.platform_id in platforms]

    # 3. Search all providers in parallel
    offers: List[dict] = []
    provider_statuses = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_provider = {
            executor.submit(_search_provider, p, parsed.get("product_name", query), filters): p
            for p in all_providers
        }
        for future in concurrent.futures.as_completed(future_to_provider, timeout=15):
            p = future_to_provider[future]
            try:
                results = future.result()
                offers.extend(results)
                provider_statuses.append({
                    "platform_id": p.platform_id,
                    "platform_name": p.platform_name,
                    "logo": p.logo_emoji,
                    "available": p.is_available(),
                    "offers_found": len(results),
                    "message": p.availability_message(),
                })
            except Exception:
                provider_statuses.append({
                    "platform_id": p.platform_id,
                    "platform_name": p.platform_name,
                    "logo": p.logo_emoji,
                    "available": False,
                    "offers_found": 0,
                    "message": "Search timed out or failed.",
                })

    # 4. If no live results, generate demo offers (clearly labelled)
    if not offers:
        offers = _generate_demo_offers(parsed.get("product_name", query), parsed, effective_budget)

    # 5. Enrich, sort, tag
    offers = enrich_offers(offers)
    offers = rank_offers(offers, sort_by)
    offers = tag_best_discount(offers)
    offers = match_offers_to_groups(offers)

    # 6. Save search history to DB (best-effort)
    search_id = _save_search_history(
        query=query,
        parsed=parsed,
        offers=offers,
        user_id=user_id,
    )

    return {
        "query": query,
        "parsed_intent": parsed,
        "offers": offers,
        "providers_checked": provider_statuses,
        "total_offers": len(offers),
        "search_id": search_id,
    }


def get_providers_status() -> List[dict]:
    """Return status info for all registered providers."""
    return [
        {
            "platform_id": p.platform_id,
            "platform_name": p.platform_name,
            "logo": p.logo_emoji,
            "website_url": p.website_url,
            "available": p.is_available(),
            "message": p.availability_message(),
        }
        for p in get_all_providers()
    ]


# ── Demo offer generation (when no APIs are configured) ──────────────────────

_DEMO_PLATFORMS = [
    {
        "platform_id": "amazon_demo",
        "platform_name": "Amazon India",
        "logo": "🛍️",
        "url_base": "https://www.amazon.in/s?k=",
        "mrp_multiplier": 1.00,
        "discount_pct": 18,
        "delivery_fee": 0,
        "rating": 4.3,
        "reviews": 12480,
    },
    {
        "platform_id": "flipkart_demo",
        "platform_name": "Flipkart",
        "logo": "📦",
        "url_base": "https://www.flipkart.com/search?q=",
        "mrp_multiplier": 1.00,
        "discount_pct": 22,
        "delivery_fee": 0,
        "rating": 4.1,
        "reviews": 8920,
    },
    {
        "platform_id": "croma_demo",
        "platform_name": "Croma",
        "logo": "🔵",
        "url_base": "https://www.croma.com/searchB?q=",
        "mrp_multiplier": 1.00,
        "discount_pct": 12,
        "delivery_fee": 99,
        "rating": 4.0,
        "reviews": 3240,
    },
    {
        "platform_id": "reliance_demo",
        "platform_name": "Reliance Digital",
        "logo": "🔴",
        "url_base": "https://www.reliancedigital.in/search?q=",
        "mrp_multiplier": 1.00,
        "discount_pct": 8,
        "delivery_fee": 0,
        "rating": 3.9,
        "reviews": 1870,
    },
]


def _generate_demo_offers(product_name: str, parsed: dict, budget_max: Optional[float]) -> List[dict]:
    """
    Generate clearly-labelled DEMO offers when no real provider APIs are configured.
    Base MRP is estimated from category; actual prices will differ.
    """
    base_mrp = _estimate_mrp(parsed.get("category", "general"), budget_max)
    from urllib.parse import quote
    encoded = quote(product_name)

    offers = []
    for plat in _DEMO_PLATFORMS:
        selling = round(base_mrp * (1 - plat["discount_pct"] / 100), -1)  # round to nearest 10
        offers.append({
            "platform_id": plat["platform_id"],
            "platform_name": plat["platform_name"],
            "platform_logo": plat["logo"],
            "website_url": plat["url_base"] + encoded,
            "product_title": f"{product_name} (Demo Result – Connect API for live price)",
            "product_url": plat["url_base"] + encoded,
            "image_url": "",
            "brand": parsed.get("brand", ""),
            "model_name": parsed.get("model", ""),
            "category": parsed.get("category", "general"),
            "seller_name": "Authorized Seller",
            "original_price": base_mrp,
            "selling_price": selling,
            "discount_percentage": plat["discount_pct"],
            "coupon_discount": 0.0,
            "bank_discount": 0.0,
            "cashback": 0.0,
            "delivery_fee": float(plat["delivery_fee"]),
            "final_payable_price": selling + plat["delivery_fee"],
            "rating": plat["rating"],
            "reviews_count": plat["reviews"],
            "availability": "in_stock",
            "offer_details": "⚠️ DEMO DATA – prices are illustrative only. Connect provider APIs for live verified prices.",
            "variant_attributes": {},
            "is_verified": False,
            "is_demo": True,
            "last_checked": datetime.utcnow().isoformat() + "Z",
            "is_best_discount": False,
            "variant_warning": [],
        })

    return offers


def _estimate_mrp(category: str, budget_max: Optional[float]) -> float:
    """Estimate a realistic MRP for demo purposes."""
    if budget_max:
        return budget_max * 1.15

    defaults = {
        "smartphone": 35000,
        "laptop": 65000,
        "tablet": 45000,
        "headphone": 8000,
        "earphone": 5000,
        "tv": 55000,
        "washing_machine": 35000,
        "refrigerator": 40000,
        "camera": 50000,
        "shoe": 8000,
        "clothing": 3000,
        "general": 20000,
    }
    return defaults.get(category, 20000)


def _save_search_history(
    query: str, parsed: dict, offers: List[dict], user_id: Optional[int]
) -> Optional[int]:
    """Save search to DB; return search_history id or None on failure."""
    try:
        from backend.extensions import db
        from backend.smart_buy.models.smart_buy_models import SearchHistory
        import json

        top_offer = offers[0] if offers else {}
        record = SearchHistory(
            user_id=user_id,
            query=query,
            category=parsed.get("category", "All"),
            filters_json=json.dumps({
                "budget_max": parsed.get("budget_max"),
                "sort": parsed.get("sort", "highest_discount"),
            }),
            results_count=len(offers),
            top_platform=top_offer.get("platform_name", ""),
            top_discount_pct=top_offer.get("discount_percentage", 0.0),
        )
        db.session.add(record)
        db.session.commit()
        return record.id
    except Exception:
        try:
            from backend.extensions import db
            db.session.rollback()
        except Exception:
            pass
        return None

