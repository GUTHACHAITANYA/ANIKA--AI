from backend.routes.auth_routes import auth_bp
from backend.routes.ocr_routes import ocr_bp
from backend.routes.split_routes import split_bp
from backend.routes.settlement_routes import settlement_bp
from backend.routes.expense_routes import expense_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.budget_routes import budget_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.export_routes import export_bp

__all__ = [
    'auth_bp', 'ocr_bp', 'split_bp', 'settlement_bp',
    'expense_bp', 'dashboard_bp', 'analytics_bp',
    'budget_bp', 'ai_bp', 'export_bp'
]
