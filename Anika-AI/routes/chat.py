from flask import Blueprint, render_template, request, jsonify
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from services.ai_service import session_chat_response
import traceback

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/', methods=['GET'])
@login_required
def index():
    from models.models import ChatMessage
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(50).all()
    return render_template('chat/index.html', history=history)

@chat_bp.route('/api/message', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json(silent=True)
        if not data or 'message' not in data:
            error_message = 'Invalid request payload: JSON with a "message" field is required.'
            print('CHAT ROUTE ERROR:', error_message)
            return jsonify({'error': error_message}), 400

        message = data.get('message', '')
        if not isinstance(message, str) or not message.strip():
            error_message = 'Message must be a non-empty string.'
            print('CHAT ROUTE ERROR:', error_message)
            return jsonify({'error': error_message}), 400

        print('CHAT ROUTE: Received message:', message)

        from models.models import ChatMessage
        from database.db import db

        user_msg = ChatMessage(user_id=current_user.id, role='user', content=message, message_type='neutral')
        db.session.add(user_msg)
        db.session.commit()

        history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(20).all()

        response_data = session_chat_response(message, current_user, history)
        print('CHAT ROUTE: AI response_data:', response_data)

        if not response_data or not isinstance(response_data, dict):
            response_data = {
                'text': 'Sorry, I am having trouble connecting to my neural network.',
                'type': 'neutral',
                'intent': 'general_chat'
            }

        ai_msg = ChatMessage(
            user_id=current_user.id,
            role='model',
            content=response_data.get('text', ''),
            message_type=response_data.get('type', 'neutral')
        )
        db.session.add(ai_msg)
        db.session.commit()

        if response_data.get('type') == 'budget_update':
            new_budget = response_data.get('new_budget')
            if new_budget is not None:
                try:
                    current_user.budget = float(new_budget)
                    db.session.commit()
                except Exception as e:
                    print('CHAT ROUTE ERROR when updating budget:', e)

        return jsonify(response_data)

    except Exception as e:
        print('CHAT ROUTE UNHANDLED ERROR:', str(e))
        traceback.print_exc()
        return jsonify({
            'text': 'Sorry, I’m temporarily unable to process that request. Please try again in a moment.',
            'type': 'neutral',
            'intent': 'general_chat',
            'error': str(e)
        }), 500
