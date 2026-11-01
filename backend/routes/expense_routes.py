import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.models import (
    Expense, ExpenseItem, Participant, Split, Settlement, ActivityLog
)
from backend.services.settlement_engine import SettlementEngine
from backend.utils.helpers import success_response, error_response, log_user_activity
from backend.utils.auth_decorators import get_current_user
from backend.utils.logger import logger

expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

@expense_bp.route('', methods=['POST'])
def save_expense():
    """
    Step 4: Final Save Workflow
    Validates all data and atomically saves Expense, Items, Participants, Splits, and Settlements.
    """
    user = get_current_user()
    user_id = user.id if user else 1

    data = request.get_json() or {}
    title = (data.get('title') or data.get('merchant_name') or 'Expense').strip()
    merchant_name = (data.get('merchant_name') or 'General Merchant').strip()
    total_amount = float(data.get('total_amount') or data.get('total') or 0.0)
    currency = (data.get('currency') or 'INR').upper()
    category = data.get('category') or 'Other'
    split_strategy = data.get('split_strategy') or 'equal'
    payer_id = str(data.get('payer_id') or 'me')
    payer_name = str(data.get('payer_name') or 'Me')
    notes = data.get('notes') or ''

    # Validation
    if total_amount <= 0:
        return error_response("Total amount must be greater than zero.", 400)

    participants_data = data.get('participants') or []
    if not participants_data:
        return error_response("At least one participant is required.", 400)

    # Validate payer is in active participants
    p_ids = [str(p.get('id')) for p in participants_data]
    if payer_id not in p_ids and len(p_ids) > 0:
        payer_id = p_ids[0]
        payer_name = participants_data[0].get('name', 'Payer')

    # Parse date
    tx_date = datetime.utcnow()
    if data.get('transaction_date'):
        try:
            tx_date = datetime.fromisoformat(data['transaction_date'].replace('Z', ''))
        except Exception:
            pass

    try:
        # Create Expense
        expense = Expense(
            user_id=user_id,
            title=title,
            merchant_name=merchant_name,
            transaction_date=tx_date,
            currency=currency,
            subtotal=float(data.get('subtotal') or total_amount),
            tax=float(data.get('tax') or 0.0),
            gst=float(data.get('gst') or 0.0),
            total_amount=total_amount,
            category=category,
            payment_method=data.get('payment_method', 'UPI / Card'),
            split_strategy=split_strategy,
            payer_id=payer_id,
            payer_name=payer_name,
            notes=notes,
            status='saved'
        )
        db.session.add(expense)
        db.session.flush() # obtain expense.id

        # Save Participants
        for p in participants_data:
            pid = str(p.get('id'))
            participant_rec = Participant(
                expense_id=expense.id,
                participant_key=pid,
                name=p.get('name', pid),
                email=p.get('email', ''),
                phone=p.get('phone', ''),
                is_payer=(pid == payer_id)
            )
            db.session.add(participant_rec)

        # Save Items
        items_data = data.get('items') or []
        for itm in items_data:
            qty = float(itm.get('quantity', 1.0))
            u_price = float(itm.get('unit_price', 0.0))
            t_price = float(itm.get('total_price', qty * u_price))
            assigned = itm.get('assigned_participants', [])
            item_rec = ExpenseItem(
                expense_id=expense.id,
                name=itm.get('name', 'Item'),
                quantity=qty,
                unit_price=u_price,
                total_price=t_price,
                category=itm.get('category', category),
                assigned_participants=json.dumps(assigned)
            )
            db.session.add(item_rec)

        # Save Splits
        splits_data = data.get('splits') or []
        for sp in splits_data:
            pid = str(sp.get('participant_id', ''))
            pname = sp.get('participant_name', pid)
            share_amt = float(sp.get('amount', 0.0))
            pct = float(sp.get('percentage', 0.0))
            split_rec = Split(
                expense_id=expense.id,
                participant_key=pid,
                participant_name=pname,
                share_amount=share_amt,
                share_percentage=pct,
                item_ids_json=json.dumps(sp.get('items', []))
            )
            db.session.add(split_rec)

        # Calculate & Save Settlement Transactions
        settlements_data = data.get('settlements')
        if not settlements_data:
            calc_res = SettlementEngine.calculate_settlements(
                participants=participants_data,
                payer_id=payer_id,
                total_amount=total_amount,
                splits=splits_data
            )
            settlements_data = calc_res.get('transactions', [])

        for st in settlements_data:
            settlement_rec = Settlement(
                expense_id=expense.id,
                from_participant_key=str(st.get('from_id')),
                from_name=st.get('from_name', ''),
                to_participant_key=str(st.get('to_id')),
                to_name=st.get('to_name', ''),
                amount=float(st.get('amount', 0.0)),
                is_paid=False
            )
            db.session.add(settlement_rec)

        db.session.commit()

        log_user_activity(
            user_id,
            "EXPENSE_SAVED",
            f"Saved bill '{merchant_name}' of ₹{total_amount:,.2f} split via {split_strategy.title()}",
            {"expense_id": expense.id, "total_amount": total_amount, "payer": payer_name}
        )
        logger.info(f"Expense saved: ID={expense.id}, Total=₹{total_amount:,.2f}, Payer={payer_name}")

        return success_response(expense.to_dict(), "Expense saved successfully.", 201)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save expense: {e}")
        return error_response(f"Failed to save expense: {str(e)}", 500)

@expense_bp.route('', methods=['GET'])
def get_expenses():
    """Returns list of expenses for the current user with optional filters."""
    user = get_current_user()
    user_id = user.id if user else 1

    query = Expense.query.filter_by(user_id=user_id)

    # Filters
    category = request.args.get('category')
    if category and category != 'All':
        query = query.filter_by(category=category)

    search = request.args.get('search')
    if search:
        query = query.filter(
            (Expense.title.ilike(f"%{search}%")) |
            (Expense.merchant_name.ilike(f"%{search}%"))
        )

    expenses = query.order_by(Expense.transaction_date.desc()).all()
    return success_response([e.to_dict() for e in expenses])

@expense_bp.route('/<int:expense_id>', methods=['GET'])
def get_expense_details(expense_id: int):
    """Retrieves full details of a specific expense."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return error_response("Expense not found.", 404)
    return success_response(expense.to_dict())

@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id: int):
    """Deletes an expense and its associated items/splits/settlements."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return error_response("Expense not found.", 404)

    user = get_current_user()
    user_id = user.id if user else 1

    try:
        title = expense.title
        total = expense.total_amount
        db.session.delete(expense)
        db.session.commit()

        log_user_activity(user_id, "EXPENSE_DELETED", f"Deleted expense '{title}' (₹{total:,.2f})")
        return success_response(None, "Expense deleted successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting expense: {e}")
        return error_response("Failed to delete expense.", 500)
