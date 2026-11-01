import json
import os
import re
import time
import logging
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from openai import OpenAI
# pyrefly: ignore [missing-import]
import numpy as np
from sklearn.tree import DecisionTreeClassifier

load_dotenv()

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

RETRY_DELAY_SECONDS = 1
GEMINI_RETRY_ATTEMPTS = 2
OPENAI_RETRY_ATTEMPTS = 1
MAX_HISTORY_MESSAGES = 20
GEMINI_MODEL = 'gemini-1.5-flash'
OPENAI_MODEL = 'gpt-3.5-turbo'

# Initialize Mock Model for Standalone Product Analysis Route
def train_mock_model():
    X = np.array([
        [0.5, 2.0], [0.8, 1.0], [0.1, 4.5], [0.05, 5.0], [0.3, 3.5], [0.15, 4.0], [0.6, 3.0], [0.01, 4.8]
    ])
    y = np.array([0, 0, 2, 2, 1, 2, 0, 2])
    clf = DecisionTreeClassifier(max_depth=3)
    clf.fit(X, y)
    return clf

mock_clf = train_mock_model()


def analyze_product(price, rating, category, user_budget):
    """Standalone product evaluation form logic"""
    if user_budget <= 0:
        budget_ratio = 1.0
    else:
        budget_ratio = price / user_budget

    pred = mock_clf.predict([[budget_ratio, rating]])[0]
    score = (rating / 5.0) * 100 - (budget_ratio * 50)
    score = max(0, min(100, score))

    insights = []
    if budget_ratio > 0.2:
        insights.append(f"This item takes up {int(budget_ratio * 100)}% of your remaining budget. Consider cheaper alternatives.")
    if rating < 3.0:
        insights.append("Product has low ratings. Quality might be poor.")

    if pred == 0:
        return 'AVOID', round(score, 2), insights
    elif pred == 1:
        return 'WAIT', round(score, 2), insights
    else:
        insights.append("Good value for money. Fits well within budget.")
        return 'BUY', round(score, 2), insights


def _load_api_key(name):
    value = os.getenv(name, '').strip()
    if not value or value.lower().startswith('your_'):
        logger.warning('%s is missing, invalid, or still a placeholder.', name)
        return None
    logger.info('%s loaded successfully.', name)
    return value


def _safe_api_call(provider_name, fn, retries):
    last_error = None
    for attempt in range(1, retries + 1):
        logger.info('%s request attempt %s/%s', provider_name, attempt, retries)
        try:
            response = fn()
            logger.info('%s request completed successfully.', provider_name)
            return response
        except Exception as exc:
            last_error = exc
            logger.exception('%s attempt %s failed: %s', provider_name, attempt, exc)
            if attempt < retries:
                time.sleep(RETRY_DELAY_SECONDS)
    raise last_error


def _normalize_history(history):
    if not history:
        return []
    normalized = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        if item is None:
            continue
        if isinstance(item, dict):
            role = item.get('role', 'user')
            content = item.get('content', '')
        else:
            role = getattr(item, 'role', None) or getattr(item, 'message_type', None) or 'user'
            content = getattr(item, 'content', '')
        if role == 'model':
            role = 'assistant'
        if role not in {'system', 'user', 'assistant'}:
            role = 'user'
        normalized.append({'role': role, 'content': content})
    return normalized


def _build_messages(system_prompt, history, user_message):
    messages = [{'role': 'system', 'content': system_prompt or 'You are Anika AI, an intelligent assistant.'}]
    messages.extend(_normalize_history(history))
    messages.append({'role': 'user', 'content': user_message})
    return messages


def _cleanup_text(raw_text):
    if raw_text is None:
        return ''
    text = str(raw_text).strip()
    text = re.sub(r'```json\s*([\s\S]*?)```', lambda m: m.group(1).strip(), text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*([\s\S]*?)```', lambda m: m.group(1).strip(), text, flags=re.IGNORECASE)
    return text


def _parse_gemini_response(response):
    if response is None:
        raise ValueError('Gemini returned no response object.')
    raw_text = getattr(response, 'text', None)
    if raw_text is None and isinstance(response, dict):
        raw_text = response.get('text') or response.get('output')
    raw_text = _cleanup_text(raw_text)
    if not raw_text:
        raise ValueError('Gemini returned an empty response.')
    return raw_text


def _parse_openai_response(response):
    if response is None:
        raise ValueError('OpenAI returned no response object.')
    if hasattr(response, 'choices'):
        if not response.choices:
            raise ValueError('OpenAI response included no choices.')
        first_choice = response.choices[0]
        message = getattr(first_choice, 'message', None)
        if message is None and isinstance(first_choice, dict):
            message = first_choice.get('message') or first_choice.get('delta')
        if message is None:
            content = getattr(first_choice, 'text', None)
        else:
            content = getattr(message, 'content', None) if hasattr(message, 'content') else message.get('content') if isinstance(message, dict) else None
        if not content and isinstance(first_choice, dict):
            content = first_choice.get('text')
        if not content:
            raise ValueError('OpenAI response choice contained no content.')
        return _cleanup_text(content)
    if isinstance(response, dict):
        choices = response.get('choices') or []
        if not choices:
            raise ValueError('OpenAI response included no choices.')
        first_choice = choices[0]
        content = None
        if isinstance(first_choice.get('message'), dict):
            content = first_choice['message'].get('content')
        if not content:
            content = first_choice.get('text')
        if not content:
            raise ValueError('OpenAI response did not return text content.')
        return _cleanup_text(content)
    raise ValueError('Unsupported OpenAI response format.')


def _build_response(text, provider):
    return {
        'provider': provider,
        'text': text,
        'type': 'general_chat',
        'intent': 'general_chat'
    }


def call_gemini(user_message, system_prompt, chat_history=None):
    gemini_key = _load_api_key('GEMINI_API_KEY')
    if not gemini_key:
        raise EnvironmentError('Gemini API key missing or invalid. Set GEMINI_API_KEY in .env without quotes or spaces.')
    genai.configure(api_key=gemini_key)
    messages = _build_messages(system_prompt, chat_history, user_message)

    def request():
        logger.info('Gemini request start: model=%s', GEMINI_MODEL)
        response = genai.chat.completions.create(
            model=GEMINI_MODEL,
            messages=messages,
            temperature=0.7,
            max_output_tokens=1024
        )
        logger.debug('Gemini raw response: %s', response)
        return response

    response = _safe_api_call('Gemini', request, GEMINI_RETRY_ATTEMPTS)
    text = _parse_gemini_response(response)
    return _build_response(text, 'Gemini')


def call_openai(user_message, system_prompt, chat_history=None):
    openai_key = _load_api_key('OPENAI_API_KEY')
    if not openai_key:
        raise EnvironmentError('OpenAI API key missing or invalid. Set OPENAI_API_KEY in .env without quotes or spaces.')
    client = OpenAI(api_key=openai_key)
    messages = _build_messages(system_prompt, chat_history, user_message)

    def request():
        logger.info('OpenAI fallback request start: model=%s', OPENAI_MODEL)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        logger.debug('OpenAI raw response: %s', response)
        return response

    response = _safe_api_call('OpenAI', request, OPENAI_RETRY_ATTEMPTS)
    text = _parse_openai_response(response)
    return _build_response(text, 'OpenAI')


def ask_ai(user_message, chat_history=None, system_prompt=None):
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError('User message must be a non-empty string.')

    gemini_error = None
    try:
        return call_gemini(user_message, system_prompt, chat_history)
    except Exception as exc:
        gemini_error = exc
        logger.exception('Gemini failed; falling back to OpenAI.')

    try:
        return call_openai(user_message, system_prompt, chat_history)
    except Exception as openai_exc:
        logger.exception('OpenAI fallback failed.')
        raise RuntimeError(f'AI backend failed. Gemini error: {gemini_error} | OpenAI error: {openai_exc}')


def session_chat_response(user_message, current_user, chat_history=None):
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'system_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            system_prompt = file.read().replace('{budget}', str(getattr(current_user, 'budget', 0.0)))
    except FileNotFoundError:
        system_prompt = f'You are Anika AI, a helpful assistant. The user budget is ₹{getattr(current_user, "budget", 0.0)}.'

    return ask_ai(user_message, chat_history=chat_history, system_prompt=system_prompt)
