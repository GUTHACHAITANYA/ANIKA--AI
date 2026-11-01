
import os
import sys
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# Load environment variables FIRST, before importing any internal modules
load_dotenv('Anika-AI/.env')

# Add Anika-AI to path for imports
sys.path.insert(0, 'Anika-AI')

from flask import Flask, render_template
from database.db import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.product_analysis import analysis_bp
from routes.chat import chat_bp
# pyrefly: ignore [missing-import]
from flask_login import LoginManager
from models.models import User
# pyrefly: ignore [missing-import]

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'anika-super-secret-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anika.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(chat_bp)

    @app.template_filter('inr')
    def inr_format(value) -> str:
        try:
            return "₹{:,.2f}".format(float(value))
        except (ValueError, TypeError):
            return "₹0.00"

    @app.route("/")
    def home() -> str:
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)