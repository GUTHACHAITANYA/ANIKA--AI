"""
Deterministic discount calculation and offer ranking for Smart Buy.
No AI arithmetic – all calculations are pure Python.
"""
from typing import List, Optional


def calculate_discount_pct(original_price: Optional[float], selling_price: float) -> float:
    """
    ((original - selling) / original) * 100  rounded to 2 dp.
    Returns 0.0 when original is None, zero, or <= selling.
    """
    if not original_price or original_price <= 0:
        return 0.0
    if selling_price >= original_price:
        return 0.0
    return round(((original_price - selling_price) / original_price) * 100, 2)


def calculate_final_payable(
    selling_price: float,
    delivery_fee: float = 0.0,
    coupon_discount: float = 0.0,
) -> float:
    """
    Final amount user must pay.
    Only guaranteed (unconditional) coupon discounts are subtracted.
    Cashback and bank offers are conditional and must NOT be subtracted here.
    """
    return round(max(selling_price - coupon_discount + delivery_fee, 0.0), 2)


def rank_offers(offers: List[dict], sort_by: str = "highest_discount") -> List[dict]:
    """
    Sort a list of offer dicts.

    sort_by options:
      'highest_discount'  – desc discount_percentage; tie → lower final_payable_price first
      'lowest_price'      – asc  final_payable_price
      'highest_rating'    – desc rating; tie → desc reviews_count
      'newest'            – desc last_checked (lexicographic ISO string is fine)

    Returns a new list (does not mutate input).
    """
    result = list(offers)

    if sort_by == "highest_discount":
        result.sort(
            key=lambda o: (-o.get("discount_percentage", 0.0), o.get("final_payable_price", 0.0))
        )
    elif sort_by == "lowest_price":
        result.sort(key=lambda o: o.get("final_payable_price", float("inf")))
    elif sort_by == "highest_rating":
        result.sort(
            key=lambda o: (-o.get("rating", 0.0), -o.get("reviews_count", 0))
        )
    elif sort_by == "newest":
        result.sort(key=lambda o: o.get("last_checked", ""), reverse=True)
    else:
        # Default fallback
        result.sort(
            key=lambda o: (-o.get("discount_percentage", 0.0), o.get("final_payable_price", 0.0))
        )

    return result


def tag_best_discount(offers: List[dict]) -> List[dict]:
    """
    Add 'is_best_discount': True to the first offer in the list (highest discount).
    All others get False.
    """
    for i, offer in enumerate(offers):
        offer["is_best_discount"] = i == 0
    return offers


def enrich_offers(offers: List[dict]) -> List[dict]:
    """
    Recalculate discount_percentage and final_payable_price from raw prices
    (in case a provider forgot to call build_offer_dict's helpers).
    """
    for offer in offers:
        offer["discount_percentage"] = calculate_discount_pct(
            offer.get("original_price"), offer.get("selling_price", 0)
        )
        offer["final_payable_price"] = calculate_final_payable(
            offer.get("selling_price", 0),
            offer.get("delivery_fee", 0),
            offer.get("coupon_discount", 0),
        )
    return offers

