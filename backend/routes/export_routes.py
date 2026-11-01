import csv
import io
from flask import Blueprint, Response, jsonify
from backend.models.models import Expense
from backend.utils.helpers import success_response, error_response, format_inr
from backend.utils.auth_decorators import get_current_user

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

@export_bp.route('/expense/<int:expense_id>/txt', methods=['GET'])
def export_expense_txt(expense_id: int):
    """Exports structured plain-text settlement sheet suitable for sharing."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return error_response("Expense record not found.", 404)

    lines = [
        "============================================================",
        "          ANIKA-AI | EXPENSE & SETTLEMENT REPORT            ",
        "============================================================",
        f"Title / Merchant : {expense.title} ({expense.merchant_name})",
        f"Transaction Date : {expense.transaction_date.strftime('%Y-%m-%d %H:%M') if expense.transaction_date else 'N/A'}",
        f"Split Strategy   : {expense.split_strategy.title()}",
        f"Primary Payer    : {expense.payer_name}",
        f"Category         : {expense.category}",
        f"Total Amount     : ₹{expense.total_amount:,.2f}",
        "------------------------------------------------------------",
        "PARTICIPANT ALLOCATIONS & SHARES:",
    ]

    for sp in expense.splits:
        lines.append(f"  • {sp.participant_name:<16} : ₹{sp.share_amount:>8,.2f} ({sp.share_percentage:.1f}%)")

    lines.append("------------------------------------------------------------")
    lines.append("OPTIMIZED SETTLEMENT TRANSACTIONS (WHO OWES WHOM):")

    if expense.settlements:
        for st in expense.settlements:
            status_tag = "[PAID]" if st.is_paid else "[PENDING]"
            lines.append(f"  • {status_tag:<9} {st.from_name} owes {st.to_name}: ₹{st.amount:,.2f}")
    else:
        lines.append("  • No outstanding settlements. Bill is fully settled.")

    lines.append("============================================================")
    lines.append("Generated with ANIKA-AI Financial Intelligence Platform")
    lines.append("============================================================")

    content = "\n".join(lines)
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=settlement_expense_{expense_id}.txt"}
    )

@export_bp.route('/expenses/csv', methods=['GET'])
def export_expenses_csv():
    """Exports all user expenses as CSV."""
    user = get_current_user()
    user_id = user.id if user else 1

    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.transaction_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Expense ID", "Date", "Title", "Merchant", "Category",
        "Total Amount (INR)", "Split Strategy", "Payer",
        "Participants Count", "Settlement Count", "Status"
    ])

    for e in expenses:
        writer.writerow([
            e.id,
            e.transaction_date.strftime("%Y-%m-%d") if e.transaction_date else "",
            e.title,
            e.merchant_name,
            e.category,
            f"{e.total_amount:.2f}",
            e.split_strategy,
            e.payer_name,
            len(e.participants),
            len(e.settlements),
            e.status
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=anika_expenses_export.csv"}
    )

@export_bp.route('/expense/<int:expense_id>/pdf-data', methods=['GET'])
def get_pdf_data(expense_id: int):
    """Provides structured data for client-side PDF document generation."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return error_response("Expense not found.", 404)
    return success_response(expense.to_dict())
