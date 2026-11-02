"""
Amazon India provider for Smart Buy.

Uses the Amazon Product Advertising API v5 (PAAPI5) when credentials are
configured. Requires three environment variables:
  AMAZON_ACCESS_KEY      – PAAPI access key
  AMAZON_SECRET_KEY      – PAAPI secret key
  AMAZON_PARTNER_TAG     – Amazon Associates partner tag (e.g. "mysite-21")

Without credentials, the provider is marked unavailable.
"""
import os
import json
import hashlib
import hmac
import datetime as dt
from typing import List
from urllib.parse import quote

from backend.smart_buy.providers.base import BaseProvider

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


class AmazonProvider(BaseProvider):
    platform_id = "amazon"
    platform_name = "Amazon India"
    website_url = "https://www.amazon.in"
    logo_emoji = "🛍️"

    _PAAPI_HOST = "webservices.amazon.in"
    _PAAPI_REGION = "eu-west-1"
    _PAAPI_URI = "/paapi5/searchitems"

    def __init__(self):
        self._access_key = os.getenv("AMAZON_ACCESS_KEY", "").strip()
        self._secret_key = os.getenv("AMAZON_SECRET_KEY", "").strip()
        self._partner_tag = os.getenv("AMAZON_PARTNER_TAG", "").strip()

    def is_available(self) -> bool:
        return bool(self._access_key and self._secret_key and self._partner_tag and _HAS_REQUESTS)

    def availability_message(self) -> str:
        if not _HAS_REQUESTS:
            return "requests library not installed."
        missing = [v for v, k in [
            ("AMAZON_ACCESS_KEY", self._access_key),
            ("AMAZON_SECRET_KEY", self._secret_key),
            ("AMAZON_PARTNER_TAG", self._partner_tag),
        ] if not k]
        if missing:
            return f"Configure {', '.join(missing)} in Render environment variables to enable live Amazon prices."
        return "Amazon PAAPI5 – ready."

    # ── AWS Signature v4 helpers ────────────────────────────────────────────
    def _sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), "sha256").digest()

    def _get_signature_key(self, date_stamp: str) -> bytes:
        k_date = self._sign(("AWS4" + self._secret_key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, self._PAAPI_REGION)
        k_service = self._sign(k_region, "ProductAdvertisingAPI")
        return self._sign(k_service, "aws4_request")

    def _call_paapi(self, payload: dict) -> dict:
        """Make a signed PAAPI5 POST request and return the parsed JSON."""
        import hashlib, hmac, base64
        import requests

        now = dt.datetime.utcnow()
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        body = json.dumps(payload)
        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

        headers_to_sign = {
            "content-encoding": "amz-1.0",
            "content-type": "application/json; charset=utf-8",
            "host": self._PAAPI_HOST,
            "x-amz-date": amz_date,
            "x-amz-target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
        }
        signed_headers = ";".join(sorted(headers_to_sign.keys()))
        canonical_headers = "\n".join(
            f"{k}:{v}" for k, v in sorted(headers_to_sign.items())
        ) + "\n"
        canonical_request = "\n".join([
            "POST", self._PAAPI_URI, "",
            canonical_headers, signed_headers, content_hash,
        ])
        credential_scope = f"{date_stamp}/{self._PAAPI_REGION}/ProductAdvertisingAPI/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256", amz_date, credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])
        signing_key = self._get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), "sha256").hexdigest()
        auth_header = (
            f"AWS4-HMAC-SHA256 Credential={self._access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        request_headers = {**headers_to_sign, "Authorization": auth_header}
        url = f"https://{self._PAAPI_HOST}{self._PAAPI_URI}"
        resp = requests.post(url, headers=request_headers, data=body, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def search(self, query: str, **filters) -> List[dict]:
        if not self.is_available():
            return []

        budget_max = filters.get("budget_max")
        payload = {
            "Keywords": query,
            "PartnerTag": self._partner_tag,
            "PartnerType": "Associates",
            "Marketplace": "www.amazon.in",
            "Resources": [
                "Images.Primary.Large",
                "ItemInfo.Title",
                "ItemInfo.Features",
                "ItemInfo.ByLineInfo",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.Condition",
                "Offers.Listings.DeliveryInfo.IsFreeShippingEligible",
                "CustomerReviews.StarRating",
                "CustomerReviews.Count",
            ],
            "ItemCount": 8,
        }

        try:
            data = self._call_paapi(payload)
        except Exception:
            return []

        offers = []
        items = data.get("SearchResult", {}).get("Items", [])
        for item in items:
            try:
                title = item["ItemInfo"]["Title"]["DisplayValue"]
                asin = item["ASIN"]
                product_url = f"https://www.amazon.in/dp/{asin}?tag={self._partner_tag}"
                image_url = item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL", "")

                listing = (item.get("Offers", {}).get("Listings") or [{}])[0]
                price_info = listing.get("Price", {})
                selling_price = price_info.get("Amount", 0.0)
                basis_info = listing.get("SavingBasis", {})
                original_price = basis_info.get("Amount", selling_price)
                if not original_price or original_price < selling_price:
                    original_price = selling_price

                delivery_fee = 0.0
                is_free_ship = listing.get("DeliveryInfo", {}).get("IsFreeShippingEligible", True)
                if not is_free_ship and selling_price < 499:
                    delivery_fee = 40.0

                rating = item.get("CustomerReviews", {}).get("StarRating", {}).get("Value", 0.0) or 0.0
                reviews_count = item.get("CustomerReviews", {}).get("Count", {}).get("Value", 0) or 0

                if budget_max and selling_price > budget_max:
                    continue

                offer = self.build_offer_dict(
                    product_title=title,
                    product_url=product_url,
                    original_price=float(original_price),
                    selling_price=float(selling_price),
                    image_url=image_url,
                    delivery_fee=delivery_fee,
                    rating=float(rating),
                    reviews_count=int(reviews_count),
                    offer_details="Ships & sold by Amazon.in",
                )
                offers.append(offer)
            except Exception:
                continue

        return offers

