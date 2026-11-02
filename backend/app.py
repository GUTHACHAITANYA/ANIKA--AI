import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask, jsonify, send_from_directory
from backend.config import Config
from backend.extensions import db, login_manager, cors
from backend.models.models import User
from backend.routes import (
    auth_bp, ocr_bp, split_bp, settlement_bp,
    expense_bp, dashboard_bp, analytics_bp,
    budget_bp, ai_bp, export_bp
)
from backend.smart_buy.routes.smart_buy_routes import smart_buy_bp
from backend.smart_buy.models.smart_buy_models import (  # noqa: F401 – registers models with SQLAlchemy
    Product, ProductOffer, SearchHistory as SmartBuySearchHistory,
    PriceHistory, ShoppingProvider
)
from backend.utils.logger import logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(split_bp)
    app.register_blueprint(settlement_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(smart_buy_bp)

    # Global error handlers (no raw tracebacks shown to user)
    @app.errorhandler(400)
    def bad_request_handler(e):
        return jsonify({
            "success": False,
            "error": "Bad request. Please verify the submitted data.",
            "status_code": 400
        }), 400

    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({
            "success": False,
            "error": "Resource not found.",
            "status_code": 404
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({
            "success": False,
            "error": "File size exceeds the 16MB upload limit. Please upload a smaller file.",
            "status_code": 413
        }), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Internal Server Error: {e}\n{tb}")
        err_msg = str(getattr(e, 'description', e))
        return jsonify({
            "success": False,
            "error": "A system error occurred while processing your request.",
            "details": err_msg,
            "status_code": 500
        }), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = "connected"
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        return jsonify({
            "status": "healthy",
            "platform": "ANIKA-AI",
            "version": "1.0.0",
            "database": db_status
        })

    # Production Single-Page App (SPA) static files & frontend routing
    dist_dir = BASE_DIR / "dist"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Prevent API routes from accidentally serving index.html
        if path.startswith("api/") or path == "api":
            return jsonify({
                "success": False,
                "error": "API endpoint not found.",
                "status_code": 404
            }), 404

        if dist_dir.exists():
            target_file = dist_dir / path
            if path != "" and target_file.exists() and target_file.is_file():
                return send_from_directory(str(dist_dir), path)
            index_file = dist_dir / "index.html"
            if index_file.exists():
                return send_from_directory(str(dist_dir), "index.html")

        return jsonify({
            "status": "online",
            "platform": "ANIKA-AI",
            "message": "Backend API is online. Run 'npm run build' to generate frontend production bundle."
        })

    with app.app_context():
        try:
            db.create_all()
            # Seed initial demo user if database is empty
            if not User.query.first():
                demo_user = User(
                    username="chaitu",
                    email="chaitu@anika.ai",
                    full_name="Chaitanya (You)",
                    monthly_budget=45000.0
                )
                demo_user.set_password("anika123")
                db.session.add(demo_user)
                db.session.commit()
                logger.info("Initialized default demo user 'chaitu' with budget INR 45,000.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            db.session.rollback()

    return app

# Expose WSGI application instance for Gunicorn / Render / Railway
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    logger.info(f"Starting ANIKA-AI Backend API on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
