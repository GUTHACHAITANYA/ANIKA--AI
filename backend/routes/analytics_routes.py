from datetime import datetime, timedelta
from flask import Blueprint, request
from backend.models.models import Expense, Settlement, Budget
from backend.utils.helpers import success_response
from backend.utils.auth_decorators import get_current_user

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('', methods=['GET'])
def get_analytics():
    """Generates detailed multi-dimensional analytics for Recharts visualizations."""
    user = get_current_user()
    user_id = user.id if user else 1
    monthly_budget = user.monthly_budget if user else 45000.0

    now = datetime.utcnow()

    # Base query with filters
    query = Expense.query.filter_by(user_id=user_id)
    category_filter = request.args.get('category')
    if category_filter and category_filter != 'All':
        query = query.filter_by(category=category_filter)

    merchant_filter = request.args.get('merchant')
    if merchant_filter:
        query = query.filter(Expense.merchant_name.ilike(f"%{merchant_filter}%"))

    expenses = query.all()

    # 1. Category Distribution
    cat_distribution = {}
    for e in expenses:
        cat = e.category or "Other"
        cat_distribution[cat] = cat_distribution.get(cat, 0.0) + e.total_amount

    category_data = [
        {"name": cat, "value": round(amt, 2)}
        for cat, amt in sorted(cat_distribution.items(), key=lambda x: x[1], reverse=True)
    ]

    # 2. Monthly Trend (last 6 months)
    monthly_trend = []
    for m_offset in range(5, -1, -1):
        # Calculate month
        target_year = now.year
        target_month = now.month - m_offset
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        month_label = datetime(target_year, target_month, 1).strftime("%b %Y")
        next_month = target_month + 1
        next_year = target_year
        if next_month > 12:
            next_month = 1
            next_year += 1

        start_dt = datetime(target_year, target_month, 1)
        end_dt = datetime(next_year, next_month, 1)

        m_total = sum(
            e.total_amount for e in Expense.query.filter(
                Expense.user_id == user_id,
                Expense.transaction_date >= start_dt,
                Expense.transaction_date < end_dt
            ).all()
        )
        monthly_trend.append({
            "month": month_label,
            "spending": round(m_total, 2),
            "budget": monthly_budget
        })

    # 3. Daily Spending (last 14 days)
    daily_data = []
    for d in range(13, -1, -1):
        day = now - timedelta(days=d)
        d_start = datetime(day.year, day.month, day.day)
        d_end = d_start + timedelta(days=1)
        d_total = sum(
            e.total_amount for e in Expense.query.filter(
                Expense.user_id == user_id,
                Expense.transaction_date >= d_start,
                Expense.transaction_date < d_end
            ).all()
        )
        daily_data.append({
            "date": day.strftime("%d %b"),
            "amount": round(d_total, 2)
        })

    # 4. Budget Utilization by Category
    category_budgets = {
        "Food & Dining": 12000.0,
        "Groceries": 8000.0,
        "Shopping": 7000.0,
        "Transport": 4000.0,
        "Entertainment": 3500.0,
        "Utilities": 5000.0
    }
    budget_vs_actual = []
    for cat, cap in category_budgets.items():
        actual_spend = cat_distribution.get(cat, 0.0)
        budget_vs_actual.append({
            "category": cat,
            "spent": round(actual_spend, 2),
            "allocated": cap,
            "percentage": round((actual_spend / cap * 100) if cap > 0 else 0, 1)
        })

    # 5. Settlement Statuses
    settlements = Settlement.query.join(Expense).filter(Expense.user_id == user_id).all()
    settled_sum = sum(s.amount for s in settlements if s.is_paid)
    pending_sum = sum(s.amount for s in settlements if not s.is_paid)

    settlement_status = [
        {"name": "Settled", "amount": round(settled_sum, 2), "count": len([s for s in settlements if s.is_paid])},
        {"name": "Pending", "amount": round(pending_sum, 2), "count": len([s for s in settlements if not s.is_paid])}
    ]

    return success_response({
        "category_distribution": category_data,
        "monthly_trend": monthly_trend,
        "daily_spending": daily_data,
        "budget_vs_actual": budget_vs_actual,
        "settlement_status": settlement_status,
        "total_expenses_recorded": len(expenses)
    })
