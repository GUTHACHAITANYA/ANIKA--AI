from typing import Dict, Any
from backend.config import Config
from backend.utils.logger import logger

class SmartBuyEngine:
    """
    Intelligent product purchase affordability analyzer.
    Evaluates financial impact against real budget, current spend, and savings runway.
    """

    @staticmethod
    def evaluate_purchase(
        item_name: str,
        price: float,
        monthly_budget: float,
        current_month_spent: float,
        category: str = "Shopping"
    ) -> Dict[str, Any]:
        remaining_budget = max(0.0, monthly_budget - current_month_spent)
        budget_utilization_before = (current_month_spent / monthly_budget * 100) if monthly_budget > 0 else 0
        budget_utilization_after = ((current_month_spent + price) / monthly_budget * 100) if monthly_budget > 0 else 0

        # Affordability Score (0 to 100)
        # Higher is more affordable
        if price <= 0:
            score = 100
            verdict = "AFFORDABLE"
            risk_level = "low"
        elif price <= (remaining_budget * 0.35):
            score = 92
            verdict = "HIGHLY AFFORDABLE"
            risk_level = "low"
        elif price <= remaining_budget:
            score = 68
            verdict = "AFFORDABLE WITH CAUTION"
            risk_level = "medium"
        elif price <= (monthly_budget * 1.5):
            score = 38
            verdict = "STRETCH PURCHASE"
            risk_level = "high"
        else:
            score = 15
            verdict = "HIGH FINANCIAL RISK"
            risk_level = "critical"

        # Construct specific advice
        monthly_impact_pct = round((price / monthly_budget * 100) if monthly_budget > 0 else 0, 1)

        recommendations = []
        if risk_level == "low":
            recommendations.append(f"Purchase fits comfortably within your remaining monthly buffer of ₹{remaining_budget:,.2f}.")
            recommendations.append("Payment via UPI/Credit card with full settlement on statement date is recommended.")
        elif risk_level == "medium":
            recommendations.append(f"This purchase consumes {round(price / remaining_budget * 100, 1)}% of your remaining monthly allowance.")
            recommendations.append("Consider postponing non-essential discretionary expenses for the next 2 weeks.")
            recommendations.append("Look for festive/bank discounts or cashback offers of 5-10% to soften the blow.")
        elif risk_level == "high":
            recommendations.append(f"Exceeds your remaining budget by ₹{(price - remaining_budget):,.2f}.")
            recommendations.append(f"Alternative plan: Allocate ₹{round(price / 3, 2):,.2f}/month for 3 months to purchase debt-free.")
            recommendations.append("If urgent, consider a 0% interest EMI only if the monthly installment stays under 15% of your total budget.")
        else:
            recommendations.append(f"This single purchase is {monthly_impact_pct}% of your entire monthly budget.")
            recommendations.append("High risk of inducing debt or depleting emergency savings.")
            recommendations.append("Explore certified refurbished alternatives or lower-tier models to cut cost by 40-50%.")

        return {
            "item_name": item_name,
            "target_price": price,
            "monthly_budget": monthly_budget,
            "current_month_spent": current_month_spent,
            "remaining_budget": remaining_budget,
            "budget_utilization_before": round(budget_utilization_before, 1),
            "budget_utilization_after": round(budget_utilization_after, 1),
            "monthly_impact_percent": monthly_impact_pct,
            "affordability_score": score,
            "verdict": verdict,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "is_ai_generated": True
        }
