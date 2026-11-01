from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from services.ai_service import session_chat_response
from models.models import ChatMessage
from database.db import db
import traceback

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/', methods=['GET'])
@login_required
def index():
    """Render the chat interface page"""
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(50).all()
    return render_template('chat/index.html', history=history)

@chat_bp.route('/', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json(silent=True)
        if not data or 'message' not in data:
            return jsonify({'error': 'Request JSON must include "message" field.'}), 400

        message = str(data.get('message', '')).strip()
        if not message:
            return jsonify({'error': 'Message must be a non-empty string.'}), 400

        user_message = message
        print('CHAT ROUTE: received message:', user_message)

        # Maintain conversation context in session memory
        chat_history = session.get('chat_history', [])

        # Save the user message to the database as well
        user_msg = ChatMessage(
            user_id=current_user.id,
            role='user',
            content=user_message,
            message_type='neutral'
        )
        db.session.add(user_msg)
        db.session.commit()

        ai_response = session_chat_response(user_message, current_user, chat_history=chat_history)
        print('CHAT ROUTE: AI response from service:', ai_response)

        text = ai_response.get('text') if isinstance(ai_response, dict) else str(ai_response)
        response_payload = {
            'provider': ai_response.get('provider', 'unknown') if isinstance(ai_response, dict) else 'unknown',
            'text': text,
            'type': ai_response.get('type', 'general_chat') if isinstance(ai_response, dict) else 'general_chat',
            'intent': ai_response.get('intent', 'general_chat') if isinstance(ai_response, dict) else 'general_chat'
        }

        assistant_msg = ChatMessage(
            user_id=current_user.id,
            role='model',
            content=response_payload['text'],
            message_type=response_payload['type']
        )
        db.session.add(assistant_msg)
        db.session.commit()

        chat_history.append({'role': 'user', 'content': user_message})
        chat_history.append({'role': 'assistant', 'content': response_payload['text']})
        session['chat_history'] = chat_history[-40:]
        session.modified = True

        return jsonify(response_payload)
    except Exception as exc:
        error_text = str(exc) or 'Unknown AI backend error.'
        print('CHAT ROUTE ERROR:', error_text)
        traceback.print_exc()
        return jsonify({
            'error': error_text,
            'text': f'AI backend failure: {error_text}',
            'type': 'error'
        }), 500
