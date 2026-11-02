"""
Flipkart India provider for Smart Buy.

Uses the Flipkart Affiliate API when credentials are configured.
Required environment variables:
  FLIPKART_AFFILIATE_ID     – Affiliate ID
  FLIPKART_AFFILIATE_TOKEN  – Affiliate API Token

Without credentials, the provider is marked unavailable.
"""
import os
import json
from typing import List

from backend.smart_buy.providers.base import BaseProvider

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


class FlipkartProvider(BaseProvider):
    platform_id = "flipkart"
    platform_name = "Flipkart"
    website_url = "https://www.flipkart.com"
    logo_emoji = "📦"

    _API_BASE = "https://affiliate-api.flipkart.net/affiliate"

    def __init__(self):
        self._affiliate_id = os.getenv("FLIPKART_AFFILIATE_ID", "").strip()
        self._token = os.getenv("FLIPKART_AFFILIATE_TOKEN", "").strip()

    def is_available(self) -> bool:
        return bool(self._affiliate_id and self._token and _HAS_REQUESTS)

    def availability_message(self) -> str:
        if not _HAS_REQUESTS:
            return "requests library not installed."
        missing = [v for v, k in [
            ("FLIPKART_AFFILIATE_ID", self._affiliate_id),
            ("FLIPKART_AFFILIATE_TOKEN", self._token),
        ] if not k]
        if missing:
            return f"Configure {', '.join(missing)} in Render environment variables to enable live Flipkart prices."
        return "Flipkart Affiliate API – ready."

    def search(self, query: str, **filters) -> List[dict]:
        if not self.is_available():
            return []

        import requests
        budget_max = filters.get("budget_max")
        headers = {
            "Fk-Affiliate-Id": self._affiliate_id,
            "Fk-Affiliate-Token": self._token,
        }

        try:
            # Flipkart Affiliate Search endpoint
            resp = requests.get(
                f"{self._API_BASE}/search/json",
                params={"query": query, "resultCount": 10},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        offers = []
        products = data.get("products", []) or data.get("productInfoList", [])
        for item in products:
            try:
                info = item.get("productBaseInfoV1") or item.get("productBaseInfo") or item
                title = info.get("title", "") or info.get("productDisplayName", "")
                product_url = info.get("productUrl", "") or info.get("flipkartProductUrl", "")
                image_url = (info.get("imageUrls") or {}).get("800x800", "") or ""
                if isinstance(image_url, dict):
                    image_url = list(image_url.values())[0] if image_url else ""

                price_info = info.get("flipkartSellingPrice") or info.get("maximumRetailPrice") or {}
                selling_price = float(price_info.get("amount", 0))
                mrp_info = info.get("maximumRetailPrice") or {}
                original_price = float(mrp_info.get("amount", selling_price))
                if not original_price or original_price < selling_price:
                    original_price = selling_price

                rating = float(info.get("overallRating", 0) or 0)
                reviews_count = int(info.get("ratingCount", 0) or 0)

                if budget_max and selling_price > budget_max:
                    continue

                offer = self.build_offer_dict(
                    product_title=title,
                    product_url=product_url,
                    original_price=original_price,
                    selling_price=selling_price,
                    image_url=image_url,
                    rating=rating,
                    reviews_count=reviews_count,
                    offer_details="Sold on Flipkart",
                )
                offers.append(offer)
            except Exception:
                continue

        return offers

