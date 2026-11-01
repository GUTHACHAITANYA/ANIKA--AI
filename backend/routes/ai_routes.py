from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.models.models import Expense, Settlement, Budget, AIInsight
from backend.services.smart_buy_engine import SmartBuyEngine
from backend.utils.helpers import success_response, error_response, format_inr
from backend.utils.auth_decorators import get_current_user
from backend.utils.logger import logger

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def build_user_financial_context(user_id: int) -> dict:
    """Extracts structured summary metrics to ground AI responses in verified numbers."""
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.transaction_date >= month_start
    ).all()

    total_spent = sum(e.total_amount for e in expenses)

    cat_map = {}
    for e in expenses:
        cat = e.category or "Other"
        cat_map[cat] = cat_map.get(cat, 0.0) + e.total_amount

    # Settlements
    pending_settlements = Settlement.query.join(Expense).filter(
        Expense.user_id == user_id,
        Settlement.is_paid == False
    ).all()

    owed_to_user = []
    user_owes = []
    for s in pending_settlements:
        if s.to_participant_key in ('me', 'user', '1'):
            owed_to_user.append(f"{s.from_name} owes you ₹{s.amount:,.2f}")
        elif s.from_participant_key in ('me', 'user', '1'):
            user_owes.append(f"You owe {s.to_name} ₹{s.amount:,.2f}")
        else:
            owed_to_user.append(f"{s.from_name} owes {s.to_name} ₹{s.amount:,.2f}")

    recent = Expense.query.filter_by(user_id=user_id).order_by(Expense.transaction_date.desc()).limit(5).all()
    recent_summary = [f"{r.merchant_name} (₹{r.total_amount:,.2f} - {r.category})" for r in recent]

    return {
        "current_month": now.strftime("%B %Y"),
        "total_month_spending": total_spent,
        "category_breakdown": cat_map,
        "settlements_summary": owed_to_user + user_owes,
        "recent_transactions": recent_summary
    }

@ai_bp.route('/chat', methods=['POST'])
def chat_assistant():
    """
    Financial AI Assistant answering natural language inquiries grounded in real database figures.
    """
    user = get_current_user()
    user_id = user.id if user else 1
    monthly_budget = user.monthly_budget if user else 45000.0

    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return error_response("Message cannot be empty.", 400)

    # 1. Grounding context
    ctx = build_user_financial_context(user_id)
    total_spent = ctx["total_month_spending"]
    cat_map = ctx["category_breakdown"]
    remaining_budget = max(0.0, monthly_budget - total_spent)

    top_cat = "None"
    top_cat_amt = 0.0
    if cat_map:
        sorted_c = sorted(cat_map.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_cat_amt = sorted_c[0]

    # Deterministic answer templates for standard queries
    msg_lower = message.lower()
    
    if "how much did i spend" in msg_lower or "total spend" in msg_lower or "spending this month" in msg_lower:
        response_text = f"You have spent **₹{total_spent:,.2f}** so far in {ctx['current_month']}. Your monthly budget is **₹{monthly_budget:,.2f}**, leaving **₹{remaining_budget:,.2f}** remaining buffer."
        return success_response({"reply": response_text, "grounded": True})

    if "highest spending" in msg_lower or "top category" in msg_lower:
        if top_cat != "None":
            pct = (top_cat_amt / total_spent * 100) if total_spent > 0 else 0
            response_text = f"Your highest spending category this month is **{top_cat}** at **₹{top_cat_amt:,.2f}** ({pct:.1f}% of all expenses)."
        else:
            response_text = "You haven't recorded any expenses for this month yet."
        return success_response({"reply": response_text, "grounded": True})

    if "owe" in msg_lower:
        if ctx["settlements_summary"]:
            details = "\n- ".join(ctx["settlements_summary"])
            response_text = f"Here is the status of your pending settlements:\n- {details}"
        else:
            response_text = "All settlements are currently clear! Nobody owes you, and you have no pending debts."
        return success_response({"reply": response_text, "grounded": True})

    if "reduce spending" in msg_lower or "save money" in msg_lower or "suggest a budget" in msg_lower:
        response_text = f"Based on your {ctx['current_month']} activity:\n\n" \
                        f"1. **Primary Driver**: Your largest outlay is in **{top_cat}** (₹{top_cat_amt:,.2f}). Trimming non-essential discretionary orders by 15% would save approx ₹{top_cat_amt * 0.15:,.2f}.\n" \
                        f"2. **Budget Status**: You are at **{round(total_spent/monthly_budget*100, 1)}%** of your monthly limit.\n" \
                        f"3. **Pending Collections**: Settle your outstanding debts (totaling ₹{sum(s.amount for s in Settlement.query.join(Expense).filter(Expense.user_id==user_id, Settlement.is_paid==False).all()):,.2f}) to replenish your cash buffer."
        return success_response({"reply": response_text, "grounded": True})

    # If Gemini API Key is configured and initialized, call Gemini for rich conversation
    if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "your_actual_gemini_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
You are ANIKA-AI, an expert fintech financial advisor.
Below is the user's verified financial data:
- Current Month: {ctx['current_month']}
- Monthly Budget: ₹{monthly_budget:,.2f}
- Total Spent: ₹{total_spent:,.2f}
- Remaining Budget: ₹{remaining_budget:,.2f}
- Spending by Category: {cat_map}
- Pending Settlements: {ctx['settlements_summary']}
- Recent Transactions: {ctx['recent_transactions']}

User Question: {message}

Instructions:
1. Answer concisely, professionally, and politely.
2. Rely strictly on the numbers given above. NEVER invent or hallucinate new transactions or amounts.
3. Provide actionable financial tips where appropriate.
"""
            res = model.generate_content(prompt)
            return success_response({"reply": res.text.strip(), "grounded": True, "engine": "gemini"})
        except Exception as e:
            logger.warning(f"Gemini chat API call failed: {e}. Utilizing grounded fallback.")

    # Graceful intelligent fallback
    response_text = f"Based on your financial records for {ctx['current_month']}:\n\n" \
                    f"- **Total Spent**: ₹{total_spent:,.2f} of ₹{monthly_budget:,.2f} budget.\n" \
                    f"- **Remaining Buffer**: ₹{remaining_budget:,.2f}.\n" \
                    f"- **Top Outlay**: {top_cat} (₹{top_cat_amt:,.2f}).\n\n" \
                    f"To make the most of your finances, prioritize clearing pending settlements and keep your daily spend pace below ₹{max(0.0, remaining_budget / 15):,.2f} for the next two weeks."
    return success_response({"reply": response_text, "grounded": True, "engine": "local_grounded"})

@ai_bp.route('/smartbuy', methods=['POST'])
def analyze_smart_buy():
    """
    Evaluates purchase affordability using SmartBuyEngine against live budget and spending.
    """
    user = get_current_user()
    user_id = user.id if user else 1
    monthly_budget = user.monthly_budget if user else 45000.0

    data = request.get_json() or {}
    item_name = (data.get('item_name') or 'Target Item').strip()
    price = float(data.get('price') or 0.0)
    category = data.get('category') or 'Shopping'

    if price <= 0:
        return error_response("Please enter a valid purchase price greater than zero.", 400)

    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    month_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.transaction_date >= month_start
    ).all()
    current_month_spent = sum(e.total_amount for e in month_expenses)

    analysis = SmartBuyEngine.evaluate_purchase(
        item_name=item_name,
        price=price,
        monthly_budget=monthly_budget,
        current_month_spent=current_month_spent,
        category=category
    )

    return success_response(analysis, "Smart Buy analysis generated successfully.")

@ai_bp.route('/insights', methods=['GET'])
def get_insights():
    """Returns AI-generated proactive insights."""
    user = get_current_user()
    user_id = user.id if user else 1

    insights = AIInsight.query.filter_by(user_id=user_id).order_by(AIInsight.created_at.desc()).limit(5).all()
    return success_response([i.to_dict() for i in insights])
