from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from backend.extensions import db
from backend.models.models import Expense, Settlement, Budget, AIInsight
from backend.utils.helpers import success_response, format_inr
from backend.utils.auth_decorators import get_current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('', methods=['GET'])
def get_dashboard_summary():
    """Aggregates all key KPIs and summary metrics for the main executive dashboard."""
    user = get_current_user()
    user_id = user.id if user else 1
    monthly_budget = user.monthly_budget if user else 45000.0

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)

    # 1. Today's Spending
    today_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.transaction_date >= today_start
    ).all()
    today_spending = sum(e.total_amount for e in today_expenses)

    # 2. Monthly Spending
    month_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.transaction_date >= month_start
    ).all()
    monthly_spending = sum(e.total_amount for e in month_expenses)

    # 3. Pending Settlements
    pending_settlements = Settlement.query.join(Expense).filter(
        Expense.user_id == user_id,
        Settlement.is_paid == False
    ).all()
    pending_amount = sum(s.amount for s in pending_settlements)

    # 4. Remaining Budget & Utilization
    remaining_budget = max(0.0, monthly_budget - monthly_spending)
    budget_utilization_pct = round((monthly_spending / monthly_budget * 100) if monthly_budget > 0 else 0, 1)

    # 5. Top Spending Category
    cat_totals = {}
    for exp in month_expenses:
        cat = exp.category or "Other"
        cat_totals[cat] = cat_totals.get(cat, 0.0) + exp.total_amount
    
    top_category = "None"
    top_category_amount = 0.0
    if cat_totals:
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        top_category, top_category_amount = sorted_cats[0]

    # 6. Recent Transactions (last 6)
    recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.transaction_date.desc()).limit(6).all()

    # 7. Spending Trends (last 7 days)
    daily_trends = []
    for i in range(6, -1, -1):
        day_date = now - timedelta(days=i)
        day_start = datetime(day_date.year, day_date.month, day_date.day)
        day_end = day_start + timedelta(days=1)
        day_total = sum(
            e.total_amount for e in Expense.query.filter(
                Expense.user_id == user_id,
                Expense.transaction_date >= day_start,
                Expense.transaction_date < day_end
            ).all()
        )
        daily_trends.append({
            "day": day_date.strftime("%a"),
            "date": day_date.strftime("%b %d"),
            "amount": round(day_total, 2)
        })

    # 8. AI Insights
    insights = AIInsight.query.filter_by(user_id=user_id).order_by(AIInsight.created_at.desc()).limit(3).all()
    insights_list = [i.to_dict() for i in insights]
    if not insights_list:
        insights_list = [
            {
                "id": 1,
                "insight_type": "budget_health",
                "content": f"You have utilized {budget_utilization_pct}% of your ₹{monthly_budget:,.2f} monthly budget. Remaining buffer is ₹{remaining_budget:,.2f}.",
                "recommendations": ["Keep discretionary dining spending under check this week."]
            },
            {
                "id": 2,
                "insight_type": "settlement_alert",
                "content": f"You have {len(pending_settlements)} pending settlement(s) totaling ₹{pending_amount:,.2f}.",
                "recommendations": ["Send polite reminders to settle shared bill shares."]
            }
        ]

    return success_response({
        "stats": {
            "today_spending": round(today_spending, 2),
            "monthly_spending": round(monthly_spending, 2),
            "pending_settlements": round(pending_amount, 2),
            "pending_settlements_count": len(pending_settlements),
            "remaining_budget": round(remaining_budget, 2),
            "monthly_budget": round(monthly_budget, 2),
            "budget_utilization_pct": budget_utilization_pct,
            "top_category": top_category,
            "top_category_amount": round(top_category_amount, 2)
        },
        "recent_transactions": [e.to_dict() for e in recent_expenses],
        "daily_trends": daily_trends,
        "ai_insights": insights_list
    })
