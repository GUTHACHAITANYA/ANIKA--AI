from flask import Blueprint, request, session, jsonify
from flask_login import login_user, logout_user, current_user
from backend.extensions import db
from backend.models.models import User, ActivityLog
from backend.utils.helpers import success_response, error_response, log_user_activity
from backend.utils.logger import logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or username).strip()

    if not username or not email or not password:
        return error_response("Username, email, and password are required.", 400)

    if len(password) < 6:
        return error_response("Password must be at least 6 characters long.", 400)

    if User.query.filter_by(username=username).first():
        return error_response("Username is already taken.", 409)

    if User.query.filter_by(email=email).first():
        return error_response("Email is already registered.", 409)

    try:
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            currency="INR",
            monthly_budget=30000.0
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        session['user_id'] = user.id

        log_user_activity(user.id, "USER_REGISTER", f"Account created for {username}")
        logger.info(f"New user registered: {username} ({email})")

        return success_response(user.to_dict(), "Registration successful!", 201)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return error_response("An unexpected error occurred during registration. Please try again.", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        identifier = (data.get('username') or data.get('identifier') or '').strip()
        password = data.get('password') or ''

        if not identifier or not password:
            return error_response("Please enter your username/email and password.", 400)

        # Ensure database tables exist
        try:
            db.create_all()
        except Exception:
            pass

        # Allow login with either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        # If user not found and logging in as default demo user, auto-seed
        if not user and (identifier.lower() in ("chaitu", "chaitu@anika.ai")):
            try:
                user = User(
                    username="chaitu",
                    email="chaitu@anika.ai",
                    full_name="Chaitanya (You)",
                    monthly_budget=45000.0
                )
                user.set_password("anika123")
                db.session.add(user)
                db.session.commit()
                logger.info("Auto-seeded default user 'chaitu' on login attempt.")
            except Exception as seed_err:
                db.session.rollback()
                logger.warning(f"Auto-seed error on login: {seed_err}")

        if not user or not user.check_password(password):
            return error_response("Invalid credentials. Please verify your username and password.", 401)

        login_user(user, remember=True)
        session['user_id'] = user.id

        log_user_activity(user.id, "USER_LOGIN", f"User {user.username} logged in")
        logger.info(f"User logged in: {user.username}")

        return success_response(user.to_dict(), "Login successful!")
    except Exception as e:
        import traceback
        logger.error(f"Login unexpected exception: {e}\n{traceback.format_exc()}")
        return error_response(f"Login failed due to a system error: {str(e)}", 500)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    uid = current_user.id if current_user.is_authenticated else session.get('user_id')
    if uid:
        log_user_activity(uid, "USER_LOGOUT", "User logged out")
    logout_user()
    session.pop('user_id', None)
    return success_response(None, "Logged out successfully.")

@auth_bp.route('/me', methods=['GET'])
def get_current_user_profile():
    if current_user and current_user.is_authenticated:
        return success_response(current_user.to_dict())
    
    # Check X-User-Id header or session
    user_id = request.headers.get('X-User-Id') or session.get('user_id')
    if user_id:
        try:
            user = User.query.get(int(user_id))
            if user:
                return success_response(user.to_dict())
        except (ValueError, TypeError):
            pass

    # In local development if no user exists, create a default demo user
    user = User.query.first()
    if not user:
        user = User(
            username="chaitu",
            email="chaitu@example.com",
            full_name="Chaitanya (You)",
            monthly_budget=45000.0
        )
        user.set_password("anika123")
        db.session.add(user)
        db.session.commit()
    
    return success_response(user.to_dict())
