"""
Abstract base class for all Smart Buy shopping platform providers.
Each provider must implement the `search` method.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional


class BaseProvider(ABC):
    """
    All shopping platform providers inherit from this base class.
    The `search` method must return a list of offer dicts in the
    standardised format defined by `build_offer_dict`.
    """

    # ── Override in every subclass ──────────────────────────────────────────
    platform_id: str = "base"
    platform_name: str = "Unknown"
    website_url: str = "https://example.com"
    logo_emoji: str = "🛒"

    # ── Availability ────────────────────────────────────────────────────────
    def is_available(self) -> bool:
        """Return True when the provider's API credentials are configured."""
        return False

    def availability_message(self) -> str:
        """Human-readable status shown in the /providers endpoint."""
        return "Provider available – no API credentials required."

    # ── Core method (must override) ─────────────────────────────────────────
    @abstractmethod
    def search(self, query: str, **filters) -> List[dict]:
        """
        Search for products on this platform.

        Args:
            query: Product name / natural-language shopping query.
            **filters: Optional keys: budget_max (float), category (str),
                       sort (str: 'highest_discount'|'lowest_price'|'highest_rating').

        Returns:
            List of offer dicts (see build_offer_dict).
        """

    # ── Helpers (shared by all providers) ───────────────────────────────────
    @staticmethod
    def calculate_discount(original_price: float, selling_price: float) -> float:
        """
        Deterministic discount calculation.
        ((original - selling) / original) * 100, rounded to 2 dp.
        Returns 0.0 if original_price is None / zero.
        """
        if not original_price or original_price <= 0:
            return 0.0
        if selling_price >= original_price:
            return 0.0
        pct = ((original_price - selling_price) / original_price) * 100
        return round(pct, 2)

    @staticmethod
    def calculate_final_payable(
        selling_price: float,
        delivery_fee: float = 0.0,
        guaranteed_discount: float = 0.0,
    ) -> float:
        """
        Final amount the user must pay (guaranteed savings only).
        Cashback / conditional bank offers are NOT subtracted here.
        """
        final = selling_price - guaranteed_discount + delivery_fee
        return round(max(final, 0.0), 2)

    def build_offer_dict(
        self,
        product_title: str,
        product_url: str,
        original_price: float,
        selling_price: float,
        *,
        image_url: str = "",
        brand: str = "",
        model_name: str = "",
        category: str = "General",
        coupon_discount: float = 0.0,
        bank_discount: float = 0.0,
        cashback: float = 0.0,
        delivery_fee: float = 0.0,
        rating: float = 0.0,
        reviews_count: int = 0,
        availability: str = "in_stock",
        offer_details: str = "",
        variant_attributes: Optional[dict] = None,
        is_demo: bool = False,
        seller_name: str = "Authorized Seller",
    ) -> dict:
        """
        Build a standardised offer dict.

        Guaranteed savings = coupon_discount (only when unconditional).
        Conditional savings (cashback, bank_discount) shown separately.
        """
        discount_pct = self.calculate_discount(original_price, selling_price)
        final_payable = self.calculate_final_payable(
            selling_price, delivery_fee, coupon_discount
        )

        return {
            # Platform
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "platform_logo": self.logo_emoji,
            "website_url": self.website_url,
            # Product
            "product_title": product_title,
            "product_url": product_url,
            "image_url": image_url,
            "brand": brand,
            "model_name": model_name,
            "category": category,
            "seller_name": seller_name,
            # Pricing (all in INR)
            "original_price": original_price,
            "selling_price": selling_price,
            "discount_percentage": discount_pct,
            # Guaranteed savings
            "coupon_discount": coupon_discount,
            # Conditional savings (not subtracted from final_payable)
            "bank_discount": bank_discount,
            "cashback": cashback,
            # Delivery & final
            "delivery_fee": delivery_fee,
            "final_payable_price": final_payable,
            # Quality signals
            "rating": rating,
            "reviews_count": reviews_count,
            "availability": availability,
            "offer_details": offer_details,
            # Variant matching attributes
            "variant_attributes": variant_attributes or {},
            # Metadata
            "is_verified": not is_demo,
            "is_demo": is_demo,
            "last_checked": datetime.utcnow().isoformat() + "Z",
        }

    def unavailable_response(self) -> dict:
        """Standard response dict when the provider has no API credentials."""
        return {
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "platform_logo": self.logo_emoji,
            "website_url": self.website_url,
            "available": False,
            "message": self.availability_message(),
            "offers": [],
        }

