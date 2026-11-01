import json
from datetime import datetime
from flask import Blueprint, request
from backend.extensions import db
from backend.models.models import Budget, Expense, User
from backend.utils.helpers import success_response, error_response, log_user_activity
from backend.utils.auth_decorators import get_current_user

budget_bp = Blueprint('budget', __name__, url_prefix='/api/budget')

DEFAULT_CATEGORY_LIMITS = {
    "Food & Dining": 12000.0,
    "Groceries": 8000.0,
    "Shopping": 7000.0,
    "Transport": 4000.0,
    "Fuel": 3500.0,
    "Entertainment": 3500.0,
    "Utilities": 5000.0,
    "Healthcare": 3000.0
}

@budget_bp.route('', methods=['GET'])
def get_budget_status():
    """Returns current month's budget, category caps, spent amounts, and utilization alerts."""
    user = get_current_user()
    user_id = user.id if user else 1

    now = datetime.utcnow()
    month = now.month
    year = now.year

    budget_record = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
    total_budget = budget_record.total_budget if budget_record else (user.monthly_budget if user else 45000.0)

    cat_budgets = DEFAULT_CATEGORY_LIMITS.copy()
    if budget_record and budget_record.category_budgets_json:
        try:
            saved_cats = json.loads(budget_record.category_budgets_json)
            cat_budgets.update(saved_cats)
        except Exception:
            pass

    # Calculate actual spending this month
    month_start = datetime(year, month, 1)
    month_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.transaction_date >= month_start
    ).all()

    total_spent = sum(e.total_amount for e in month_expenses)
    remaining_total = max(0.0, total_budget - total_spent)
    overall_utilization = round((total_spent / total_budget * 100) if total_budget > 0 else 0, 1)

    # Category breakdowns
    cat_spent_map = {}
    for e in month_expenses:
        cat = e.category or "Other"
        cat_spent_map[cat] = cat_spent_map.get(cat, 0.0) + e.total_amount

    categories_detail = []
    for cat, allocated in cat_budgets.items():
        spent = cat_spent_map.get(cat, 0.0)
        rem = max(0.0, allocated - spent)
        pct = round((spent / allocated * 100) if allocated > 0 else 0, 1)
        
        status = "safe"
        if pct >= 100:
            status = "exceeded"
        elif pct >= 80:
            status = "warning"

        categories_detail.append({
            "category": cat,
            "allocated": round(allocated, 2),
            "spent": round(spent, 2),
            "remaining": round(rem, 2),
            "utilization_pct": pct,
            "status": status
        })

    return success_response({
        "month": month,
        "year": year,
        "total_budget": round(total_budget, 2),
        "total_spent": round(total_spent, 2),
        "remaining_budget": round(remaining_total, 2),
        "overall_utilization_pct": overall_utilization,
        "is_budget_exceeded": total_spent > total_budget,
        "categories": categories_detail
    })

@budget_bp.route('', methods=['POST'])
def update_budget():
    """Sets or updates monthly budget and category limits."""
    user = get_current_user()
    user_id = user.id if user else 1

    data = request.get_json() or {}
    total_budget = float(data.get('total_budget') or 45000.0)
    category_budgets = data.get('category_budgets') or DEFAULT_CATEGORY_LIMITS

    if total_budget <= 0:
        return error_response("Monthly budget must be greater than zero.", 400)

    now = datetime.utcnow()
    month = now.month
    year = now.year

    try:
        # Update user's default budget
        if user:
            user.monthly_budget = total_budget

        budget_rec = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
        if not budget_rec:
            budget_rec = Budget(
                user_id=user_id,
                month=month,
                year=year,
                total_budget=total_budget,
                category_budgets_json=json.dumps(category_budgets)
            )
            db.session.add(budget_rec)
        else:
            budget_rec.total_budget = total_budget
            budget_rec.category_budgets_json = json.dumps(category_budgets)

        db.session.commit()
        log_user_activity(
            user_id, "BUDGET_UPDATED",
            f"Updated monthly budget to ₹{total_budget:,.2f}",
            {"total_budget": total_budget}
        )

        return success_response(budget_rec.to_dict(), "Budget configuration saved successfully.")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update budget: {str(e)}", 500)
