from functools import wraps
from flask import request, jsonify, session
from flask_login import current_user
from backend.models.models import User

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user and current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # Support user_id in header for API clients / token support
        user_id_header = request.headers.get('X-User-Id')
        if user_id_header:
            try:
                user = User.query.get(int(user_id_header))
                if user:
                    return f(*args, **kwargs)
            except (ValueError, TypeError):
                pass

        # If user_id is in session
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                return f(*args, **kwargs)

        return jsonify({
            'error': 'Unauthorized',
            'message': 'Please log in to access this resource.'
        }), 401
    return decorated_function

def get_current_user():
    """Helper to get current active User object from session, current_user, or X-User-Id."""
    if current_user and current_user.is_authenticated:
        return current_user
    
    user_id_header = request.headers.get('X-User-Id')
    if user_id_header:
        try:
            user = User.query.get(int(user_id_header))
            if user:
                return user
        except (ValueError, TypeError):
            pass

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return user
            
    # Default to first user or create a default demo user if in local dev
    first_user = User.query.first()
    return first_user
