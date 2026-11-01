import os
import json
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.extensions import db
from backend.models.models import Receipt, User
from backend.services.gemini_service import gemini_ocr_service
from backend.services.ocr_parser import aggregate_multi_bills
from backend.services.nlp_service import NLPExpenseExtractor
from backend.ocr.processor import preprocess_receipt_image
from backend.utils.helpers import (
    allowed_file, sanitize_and_save_file, success_response,
    error_response, log_user_activity
)
from backend.utils.auth_decorators import get_current_user
from backend.utils.logger import logger

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

@ocr_bp.route('/upload', methods=['POST'])
def upload_and_process():
    """
    Handles single and multi-receipt uploads.
    Validates file formats, sizes, extracts structured data via Gemini OCR,
    and returns both individual receipt structures and combined totals.
    """
    user = get_current_user()
    user_id = user.id if user else 1

    # Check for files
    if 'files' not in request.files and 'file' not in request.files:
        return error_response("No files were provided for upload.", 400)

    uploaded_files = request.files.getlist('files')
    if not uploaded_files and 'file' in request.files:
        uploaded_files = [request.files['file']]

    if not uploaded_files or uploaded_files[0].filename == '':
        return error_response("Please select at least one valid receipt or bill file.", 400)

    results = []
    errors = []

    for file in uploaded_files:
        if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
            errors.append(f"File '{file.filename}' has an unsupported extension. Allowed: JPG, JPEG, PNG, WEBP, PDF.")
            continue

        try:
            # 1. Save file securely
            saved_path, orig_name, file_size = sanitize_and_save_file(file, Config.UPLOAD_FOLDER)
            
            # 2. Check file size limit
            if file_size > Config.MAX_CONTENT_LENGTH:
                errors.append(f"File '{orig_name}' exceeds maximum allowed size of 16MB.")
                continue

            # 3. Preprocess if image
            if not saved_path.lower().endswith('.pdf'):
                preprocess_receipt_image(saved_path)

            # 4. Extract structured data via OCR
            ocr_result = gemini_ocr_service.extract_from_image(saved_path)
            extracted_data = ocr_result.get("data", {})

            # 5. Save Receipt record in DB
            receipt_record = Receipt(
                user_id=user_id,
                file_path=saved_path,
                original_filename=orig_name,
                mime_type=file.content_type or 'application/octet-stream',
                file_size=file_size,
                raw_extracted_json=json.dumps(extracted_data),
                ocr_confidence=float(extracted_data.get('confidence', 0.95))
            )
            db.session.add(receipt_record)
            db.session.commit()

            results.append({
                "receipt_id": receipt_record.id,
                "original_filename": orig_name,
                "file_path": saved_path,
                "engine": ocr_result.get("engine", "gemini"),
                "data": extracted_data
            })

            log_user_activity(
                user_id, "OCR_UPLOAD",
                f"Processed receipt '{orig_name}' (Total: ₹{extracted_data.get('total', 0.0):,.2f})",
                {"receipt_id": receipt_record.id, "total": extracted_data.get('total')}
            )

        except Exception as e:
            logger.error(f"Error processing upload '{file.filename}': {e}")
            errors.append(f"Unable to process '{file.filename}'. Please try a clearer image.")

    if not results and errors:
        return error_response("Failed to process uploaded receipts.", 400, errors=errors)

    # Multi-bill aggregation
    summary = aggregate_multi_bills(results)
    
    return success_response({
        "summary": summary,
        "processed_count": len(results),
        "receipts": results,
        "warnings": errors
    }, f"Successfully analyzed {len(results)} receipt(s).")

@ocr_bp.route('/analyze', methods=['POST'])
def analyze_text():
    """
    Parses a natural language expense note (e.g. 'Chaitu paid 1200 for dinner at Pizza Hut')
    using deterministic NLP & ML category classifier.
    """
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        return error_response("Text description is required for analysis.", 400)

    parsed = NLPExpenseExtractor.parse_expense_text(text)
    return success_response(parsed, "Expense text analyzed successfully.")

@ocr_bp.route('/history', methods=['GET'])
def get_receipt_history():
    """Returns past scanned receipts for current user."""
    user = get_current_user()
    user_id = user.id if user else 1

    receipts = Receipt.query.filter_by(user_id=user_id).order_by(Receipt.upload_date.desc()).limit(20).all()
    return success_response([r.to_dict() for r in receipts])
