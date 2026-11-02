"""
Smart Buy tests – covers all 10 required test cases plus extras.
"""
import json
import pytest

# ── Discount Calculator Tests ────────────────────────────────────────────────
from backend.smart_buy.services.discount_calculator import (
    calculate_discount_pct,
    calculate_final_payable,
    rank_offers,
    enrich_offers,
    tag_best_discount,
)
from backend.smart_buy.services.product_matcher import (
    extract_variant_attributes,
    variants_are_compatible,
)


class TestDiscountCalculation:
    def test_discount_calculation_basic(self):
        """((80000-48000)/80000)*100 == 40.0"""
        assert calculate_discount_pct(80000, 48000) == 40.0

    def test_discount_35_percent(self):
        assert calculate_discount_pct(80000, 52000) == 35.0

    def test_discount_25_percent(self):
        assert calculate_discount_pct(80000, 60000) == 25.0

    def test_discount_missing_original_returns_zero(self):
        """When original price is None, return 0.0 (not 'unavailable')."""
        assert calculate_discount_pct(None, 5000) == 0.0

    def test_discount_zero_original_returns_zero(self):
        assert calculate_discount_pct(0, 5000) == 0.0

    def test_discount_selling_equals_original(self):
        assert calculate_discount_pct(10000, 10000) == 0.0

    def test_discount_selling_above_original(self):
        assert calculate_discount_pct(5000, 6000) == 0.0


class TestFinalPayable:
    def test_final_payable_no_extras(self):
        assert calculate_final_payable(48000) == 48000.0

    def test_final_payable_with_delivery(self):
        assert calculate_final_payable(48000, delivery_fee=99) == 48099.0

    def test_final_payable_with_coupon(self):
        assert calculate_final_payable(48000, coupon_discount=1000) == 47000.0

    def test_cashback_not_in_final_payable(self):
        """Cashback is conditional – must NOT reduce final_payable."""
        # calculate_final_payable has no cashback parameter by design
        fp = calculate_final_payable(48000, delivery_fee=0, coupon_discount=0)
        assert fp == 48000.0  # cashback (2000) stays separate


class TestRankOffers:
    def _make_offers(self):
        return [
            {"platform_name": "Croma",    "discount_percentage": 25.0, "final_payable_price": 60000, "rating": 4.0, "reviews_count": 100, "last_checked": "2026-01-01T10:00:00Z"},
            {"platform_name": "Amazon",   "discount_percentage": 35.0, "final_payable_price": 52000, "rating": 4.5, "reviews_count": 5000, "last_checked": "2026-01-01T12:00:00Z"},
            {"platform_name": "Flipkart", "discount_percentage": 40.0, "final_payable_price": 48000, "rating": 4.2, "reviews_count": 3000, "last_checked": "2026-01-01T11:00:00Z"},
        ]

    def test_highest_discount_sort(self):
        """Flipkart 40% > Amazon 35% > Croma 25%"""
        sorted_offers = rank_offers(self._make_offers(), "highest_discount")
        names = [o["platform_name"] for o in sorted_offers]
        assert names == ["Flipkart", "Amazon", "Croma"]

    def test_tiebreaker_lower_price_wins(self):
        """Equal discount → lower final_payable first."""
        offers = [
            {"platform_name": "B", "discount_percentage": 30.0, "final_payable_price": 56000, "rating": 4.0, "reviews_count": 100, "last_checked": ""},
            {"platform_name": "A", "discount_percentage": 30.0, "final_payable_price": 54000, "rating": 4.0, "reviews_count": 100, "last_checked": ""},
        ]
        result = rank_offers(offers, "highest_discount")
        assert result[0]["platform_name"] == "A"

    def test_lowest_price_sort(self):
        sorted_offers = rank_offers(self._make_offers(), "lowest_price")
        prices = [o["final_payable_price"] for o in sorted_offers]
        assert prices == sorted(prices)

    def test_highest_rating_sort(self):
        sorted_offers = rank_offers(self._make_offers(), "highest_rating")
        assert sorted_offers[0]["platform_name"] == "Amazon"

    def test_tag_best_discount(self):
        offers = rank_offers(self._make_offers(), "highest_discount")
        tagged = tag_best_discount(offers)
        assert tagged[0]["is_best_discount"] is True
        assert all(not o["is_best_discount"] for o in tagged[1:])


class TestVariantMatching:
    def test_extract_storage(self):
        attrs = extract_variant_attributes("Samsung Galaxy S24 256GB Phantom Black")
        assert attrs.get("storage") == "256GB"

    def test_extract_color(self):
        attrs = extract_variant_attributes("iPhone 16 Pro Titanium")
        assert attrs.get("color") == "Titanium"

    def test_variant_mismatch_flagged(self):
        """128GB and 256GB are different variants – must be flagged."""
        attrs_a = {"storage": "128GB"}
        attrs_b = {"storage": "256GB"}
        compatible, mismatches = variants_are_compatible(attrs_a, attrs_b)
        assert not compatible
        assert "storage" in mismatches

    def test_variant_match_passes(self):
        attrs_a = {"storage": "256GB", "color": "Black"}
        attrs_b = {"storage": "256GB", "color": "Black"}
        compatible, mismatches = variants_are_compatible(attrs_a, attrs_b)
        assert compatible
        assert mismatches == []

    def test_missing_key_ignored(self):
        """If one dict is missing a key, treat as compatible (ambiguous)."""
        attrs_a = {"storage": "256GB"}
        attrs_b = {}  # storage unknown
        compatible, _ = variants_are_compatible(attrs_a, attrs_b)
        assert compatible


# ── Flask API Tests ───────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestProviderEndpoint:
    def test_providers_endpoint_returns_list(self, client):
        resp = client.get("/api/smart-buy/providers")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert isinstance(data["providers"], list)
        assert data["total"] == 6

    def test_provider_unavailable_has_status(self, client):
        resp = client.get("/api/smart-buy/providers")
        data = resp.get_json()
        for p in data["providers"]:
            assert "available" in p
            assert "message" in p

    def test_provider_amazon_unavailable_without_creds(self, client):
        """Without env vars, Amazon should show available=False."""
        resp = client.get("/api/smart-buy/providers")
        data = resp.get_json()
        amazon = next((p for p in data["providers"] if p["platform_id"] == "amazon"), None)
        assert amazon is not None
        assert amazon["available"] is False


class TestSearchEndpoint:
    def test_search_no_query_returns_400(self, client):
        resp = client.get("/api/smart-buy/search")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_search_returns_demo_offers(self, client):
        """Without API keys, should return demo offers with is_demo=True."""
        resp = client.get("/api/smart-buy/search?q=iPhone+16")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["total_offers"] > 0
        for offer in data["offers"]:
            assert offer["is_demo"] is True

    def test_search_sorted_highest_discount(self, client):
        resp = client.get("/api/smart-buy/search?q=Samsung+Galaxy+S24&sort=highest_discount")
        data = resp.get_json()
        offers = data["offers"]
        discounts = [o["discount_percentage"] for o in offers]
        assert discounts == sorted(discounts, reverse=True)

    def test_search_history_saved(self, client):
        """After a search, a history record should exist."""
        client.get("/api/smart-buy/search?q=test+product+history+check")
        resp = client.get("/api/smart-buy/history")
        data = resp.get_json()
        assert resp.status_code == 200
        queries = [h["query"] for h in data["history"]]
        assert "test product history check" in queries

    def test_cashback_not_in_guaranteed_savings(self, client):
        """Cashback must appear in cashback field, not reduce final_payable via coupon."""
        resp = client.get("/api/smart-buy/search?q=boAt+headphones")
        data = resp.get_json()
        for offer in data["offers"]:
            # final_payable = selling - coupon + delivery (no cashback subtracted)
            expected = offer["selling_price"] - offer["coupon_discount"] + offer["delivery_fee"]
            assert abs(offer["final_payable_price"] - expected) < 1.0


class TestCompareEndpoint:
    def test_compare_ranks_correctly(self, client):
        offers = [
            {"platform_name": "Croma", "discount_percentage": 10.0, "final_payable_price": 45000,
             "rating": 4.0, "reviews_count": 100, "last_checked": ""},
            {"platform_name": "Flipkart", "discount_percentage": 30.0, "final_payable_price": 35000,
             "rating": 4.2, "reviews_count": 2000, "last_checked": ""},
        ]
        resp = client.post("/api/smart-buy/compare",
                           data=json.dumps({"offers": offers, "sort_by": "highest_discount"}),
                           content_type="application/json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["offers"][0]["platform_name"] == "Flipkart"
        assert data["offers"][0]["is_best_discount"] is True


class TestPriceHistoryEndpoint:
    def test_price_history_no_data(self, client):
        resp = client.get("/api/smart-buy/price-history/99999")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["history"] == []

