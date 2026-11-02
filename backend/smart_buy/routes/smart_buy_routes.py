"""
Smart Buy API Routes

GET  /api/smart-buy/search?q=...&sort=highest_discount&budget=60000&platform=amazon
GET  /api/smart-buy/providers
GET  /api/smart-buy/history
POST /api/smart-buy/compare
GET  /api/smart-buy/price-history/<int:product_id>
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user

from backend.smart_buy.services.search_service import search_products, get_providers_status
from backend.smart_buy.services.discount_calculator import rank_offers

smart_buy_bp = Blueprint("smart_buy", __name__, url_prefix="/api/smart-buy")


@smart_buy_bp.route("/search", methods=["GET"])
def search():
    """Search for products across all configured platforms."""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"success": False, "error": "Query parameter 'q' is required."}), 400

    sort_by = request.args.get("sort", "highest_discount")
    valid_sorts = {"highest_discount", "lowest_price", "highest_rating", "newest"}
    if sort_by not in valid_sorts:
        sort_by = "highest_discount"

    # Budget filter
    budget_raw = request.args.get("budget") or request.args.get("budget_max")
    budget_max = None
    if budget_raw:
        try:
            budget_max = float(budget_raw)
        except ValueError:
            pass

    # Platform filter (comma-separated)
    platform_raw = request.args.get("platform") or request.args.get("platforms")
    platforms = None
    if platform_raw:
        platforms = [p.strip() for p in platform_raw.split(",") if p.strip()]

    user_id = current_user.id if current_user.is_authenticated else None

    try:
        result = search_products(
            query=q,
            sort_by=sort_by,
            budget_max=budget_max,
            platforms=platforms,
            user_id=user_id,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@smart_buy_bp.route("/providers", methods=["GET"])
def providers():
    """Return status of all registered shopping platform providers."""
    try:
        statuses = get_providers_status()
        return jsonify({"success": True, "providers": statuses, "total": len(statuses)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@smart_buy_bp.route("/history", methods=["GET"])
def search_history():
    """Return recent search history for the current user (or all if anonymous)."""
    try:
        from backend.extensions import db
        from backend.smart_buy.models.smart_buy_models import SearchHistory

        limit = min(int(request.args.get("limit", 20)), 100)
        user_id = current_user.id if current_user.is_authenticated else None

        from backend.extensions import db as _db
        stmt = _db.select(SearchHistory).order_by(SearchHistory.created_at.desc())
        if user_id:
            stmt = stmt.where(SearchHistory.user_id == user_id)
        stmt = stmt.limit(limit)
        records = _db.session.execute(stmt).scalars().all()
        return jsonify({
            "success": True,
            "history": [r.to_dict() for r in records],
            "total": len(records),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@smart_buy_bp.route("/compare", methods=["POST"])
def compare():
    """
    Compare a specific list of offer dicts.
    Body: { "offers": [...], "sort_by": "highest_discount" }
    """
    try:
        data = request.get_json(silent=True) or {}
        offers = data.get("offers", [])
        sort_by = data.get("sort_by", "highest_discount")

        if not isinstance(offers, list):
            return jsonify({"success": False, "error": "'offers' must be a list."}), 400

        ranked = rank_offers(offers, sort_by)
        if ranked:
            ranked[0]["is_best_discount"] = True
            for o in ranked[1:]:
                o["is_best_discount"] = False

        return jsonify({"success": True, "offers": ranked, "total": len(ranked)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@smart_buy_bp.route("/price-history/<int:product_id>", methods=["GET"])
def price_history(product_id: int):
    """Return price history for a stored product."""
    try:
        from backend.smart_buy.models.smart_buy_models import PriceHistory

        records = (
            PriceHistory.query
            .filter_by(product_id=product_id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(90)
            .all()
        )
        if not records:
            return jsonify({
                "success": True,
                "product_id": product_id,
                "message": "No price history available yet. History is collected over time as searches are performed.",
                "history": [],
            })
        return jsonify({
            "success": True,
            "product_id": product_id,
            "history": [r.to_dict() for r in records],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
