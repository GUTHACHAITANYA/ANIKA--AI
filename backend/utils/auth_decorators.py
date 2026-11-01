from functools import wraps
from flask import request, jsonify, session
from flask_login import current_user
from backend.models.models import User
from backend.extensions import db
from backend.utils.logger import logger

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user and current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # Support user_id in header for API clients / token support
        user_id_header = request.headers.get('X-User-Id')
        if user_id_header:
            try:
                user = db.session.get(User, int(user_id_header))
                if user:
                    return f(*args, **kwargs)
            except Exception:
                pass

        # If user_id is in session
        if 'user_id' in session:
            try:
                user = db.session.get(User, int(session['user_id']))
                if user:
                    return f(*args, **kwargs)
            except Exception:
                pass

        return jsonify({
            'error': 'Unauthorized',
            'message': 'Please log in to access this resource.'
        }), 401
    return decorated_function

def get_current_user():
    """Helper to get current active User object from session, current_user, or X-User-Id."""
    try:
        if current_user and current_user.is_authenticated:
            return current_user
        
        user_id_header = request.headers.get('X-User-Id')
        if user_id_header:
            try:
                user = db.session.get(User, int(user_id_header))
                if user:
                    return user
            except Exception:
                pass

        if 'user_id' in session:
            try:
                user = db.session.get(User, int(session['user_id']))
                if user:
                    return user
            except Exception:
                pass
                
        # Default to first user or ensure demo user exists
        first_user = User.query.first()
        if not first_user:
            try:
                first_user = User(
                    username="chaitu",
                    email="chaitu@anika.ai",
                    full_name="Chaitanya (You)",
                    monthly_budget=45000.0
                )
                first_user.set_password("anika123")
                db.session.add(first_user)
                db.session.commit()
            except Exception:
                db.session.rollback()
                first_user = User.query.first()
        return first_user
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        return None
