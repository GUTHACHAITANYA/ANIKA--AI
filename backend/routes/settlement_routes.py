from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.models import Settlement
from backend.services.settlement_engine import SettlementEngine
from backend.utils.helpers import success_response, error_response, log_user_activity
from backend.utils.auth_decorators import get_current_user
from backend.utils.logger import logger

settlement_bp = Blueprint('settlements', __name__, url_prefix='/api/settlements')

@settlement_bp.route('/calculate', methods=['POST'])
def calculate_settlements():
    """
    Computes deterministic debt-minimized settlement transactions.
    """
    data = request.get_json() or {}
    participants = data.get('participants') or []
    payer_id = data.get('payer_id') or 'me'
    total_amount = float(data.get('total_amount') or 0.0)
    splits = data.get('splits') or []

    if not participants:
        return error_response("Participants are required for settlement calculation.", 400)
    if total_amount <= 0:
        return error_response("Total amount must be greater than zero.", 400)
    if not splits:
        return error_response("Split allocations are required.", 400)

    try:
        settlement_result = SettlementEngine.calculate_settlements(
            participants=participants,
            payer_id=payer_id,
            total_amount=total_amount,
            splits=splits
        )
        return success_response(settlement_result, "Settlement calculated successfully.")
    except Exception as e:
        logger.error(f"Settlement calculation error: {e}")
        return error_response(f"Settlement calculation error: {str(e)}", 400)

@settlement_bp.route('/<int:settlement_id>/paid', methods=['POST'])
def mark_settlement_paid(settlement_id: int):
    """
    Marks a recorded settlement transaction as settled/paid.
    """
    settlement = Settlement.query.get(settlement_id)
    if not settlement:
        return error_response("Settlement record not found.", 404)

    data = request.get_json() or {}
    payment_reference = data.get('payment_reference', 'Direct UPI / Cash Settlement')

    settlement.is_paid = True
    settlement.paid_at = datetime.utcnow()
    settlement.payment_reference = payment_reference

    user = get_current_user()
    user_id = user.id if user else 1

    try:
        db.session.commit()
        log_user_activity(
            user_id,
            "SETTLEMENT_PAID",
            f"Settlement marked paid: {settlement.from_name} paid ₹{settlement.amount:,.2f} to {settlement.to_name}",
            {"settlement_id": settlement.id, "amount": settlement.amount}
        )
        return success_response(settlement.to_dict(), "Settlement marked as paid successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update settlement: {e}")
        return error_response("Failed to update settlement status.", 500)
