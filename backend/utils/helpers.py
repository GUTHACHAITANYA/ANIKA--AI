import os
import json
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from flask import jsonify
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models.models import ActivityLog

def round_currency(val) -> float:
    """Deterministic rounding to 2 decimal places using Decimal to prevent floating point drift."""
    try:
        d = Decimal(str(val))
        return float(d.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
    except Exception:
        return 0.0

def format_inr(val) -> str:
    """Format float into Indian Rupee format ₹XX,XXX.XX"""
    try:
        val = round_currency(val)
        return f"₹{val:,.2f}"
    except Exception:
        return "₹0.00"

def success_response(data=None, message="Success", status_code=200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    payload = {"success": False, "error": message}
    if errors is not None:
        payload["details"] = errors
    return jsonify(payload), status_code

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_and_save_file(file, upload_folder: str) -> tuple[str, str, int]:
    """Saves uploaded file securely and returns (saved_path, original_filename, file_size)."""
    orig_name = secure_filename(file.filename) or "receipt"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{orig_name}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    return file_path, orig_name, file_size

def log_user_activity(user_id: int, action_type: str, description: str, metadata: dict = None):
    """Utility to record structured activity logs in database."""
    try:
        log_entry = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            description=description,
            metadata_json=json.dumps(metadata or {})
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
