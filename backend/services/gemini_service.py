import os
import json
import time
from typing import Dict, Any, Optional
from PIL import Image
import io

from backend.config import Config
from backend.utils.logger import logger
from backend.ml.predictor import predict_category

OCR_JSON_SCHEMA = """
{
  "merchant_name": "String",
  "transaction_date": "YYYY-MM-DD",
  "currency": "INR",
  "subtotal": 0.0,
  "tax": 0.0,
  "gst": 0.0,
  "total": 0.0,
  "items": [
    {
      "name": "String",
      "quantity": 1.0,
      "unit_price": 0.0,
      "total_price": 0.0,
      "category": "Food & Dining"
    }
  ],
  "category": "Food & Dining",
  "confidence": 0.95
}
"""

SYSTEM_OCR_PROMPT = f"""
You are an expert OCR & financial document intelligence assistant.
Extract all structured financial information from this receipt, bill, invoice, or screenshot.
You MUST output ONLY a valid JSON object matching this exact schema:
{OCR_JSON_SCHEMA}

Rules:
1. Extract the exact merchant/store name. If not found, use a reasonable name from the header.
2. Extract the date in YYYY-MM-DD format. Default to today's date if absent.
3. Currency defaults to 'INR' unless clearly marked otherwise (USD, EUR, etc.).
4. Extract all item lines with accurate name, quantity, unit_price, and total_price.
5. If subtotal is missing, calculate it as sum of item total prices.
6. Ensure total = subtotal + tax + gst (or adjust slightly to match actual printed total).
7. Assign an appropriate category from: Food & Dining, Groceries, Shopping, Transport, Fuel, Healthcare, Entertainment, Utilities, Travel, Education, Bills, Other.
8. Output pure JSON without markdown wrappers or conversational text.
"""

class GeminiOCRService:
    """Production OCR service interfacing with Google Gemini Vision with retry and resilient fallback."""

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.client_initialized = False
        self._init_client()

    def _init_client(self):
        if self.api_key and self.api_key != "your_actual_gemini_key_here" and len(self.api_key) > 10:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self.client_initialized = True
                logger.info("Google Gemini GenAI SDK successfully initialized for OCR.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client_initialized = False
        else:
            logger.info("No active Gemini API key configured. Local resilient fallback will be utilized.")

    def extract_from_image(self, image_path: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Extracts structured JSON from image file using Gemini Vision or local parser.
        """
        logger.info(f"OCR Start: Processing '{image_path}'")
        start_time = time.time()

        # If Gemini is configured, attempt Vision API call
        if self.client_initialized:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Sending document to Gemini Vision (Attempt {attempt}/{max_retries})...")
                    img = Image.open(image_path)
                    
                    # Convert RGBA to RGB if needed
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                    model = self.genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    response = model.generate_content([SYSTEM_OCR_PROMPT, img])
                    raw_text = response.text.strip()

                    # Clean markdown ticks if any
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]

                    parsed_json = json.loads(raw_text.strip())
                    validated_data = self._validate_and_normalize(parsed_json)
                    
                    elapsed = time.time() - start_time
                    logger.info(f"OCR Completion: Successfully parsed receipt in {elapsed:.2f}s via Gemini.")
                    return {
                        "success": True,
                        "data": validated_data,
                        "engine": "gemini-1.5-flash",
                        "message": "Receipt processed successfully."
                    }
                except Exception as e:
                    logger.warning(f"Gemini OCR Attempt {attempt} failed: {e}")
                    time.sleep(1)

        # Resilient Local Fallback
        logger.info("Engaging local intelligent OCR & heuristic parser...")
        from backend.services.ocr_parser import parse_document_fallback
        fallback_data = parse_document_fallback(image_path)
        
        elapsed = time.time() - start_time
        logger.info(f"OCR Local Fallback Completion: Processed in {elapsed:.2f}s.")
        return {
            "success": True,
            "data": fallback_data,
            "engine": "local_resilient_engine",
            "message": "Receipt analyzed and structured successfully."
        }

    def _validate_and_normalize(self, raw: dict) -> dict:
        """Enforces schema consistency and validates calculated totals."""
        merchant = str(raw.get("merchant_name") or "Merchant").strip()
        date_str = str(raw.get("transaction_date") or time.strftime("%Y-%m-%d")).strip()
        currency = str(raw.get("currency") or "INR").upper()

        subtotal = float(raw.get("subtotal") or 0.0)
        tax = float(raw.get("tax") or 0.0)
        gst = float(raw.get("gst") or 0.0)
        total = float(raw.get("total") or 0.0)

        raw_items = raw.get("items") or []
        normalized_items = []
        calc_subtotal = 0.0

        for idx, item in enumerate(raw_items):
            name = str(item.get("name") or f"Item {idx + 1}").strip()
            qty = float(item.get("quantity") or 1.0)
            u_price = float(item.get("unit_price") or 0.0)
            t_price = float(item.get("total_price") or (qty * u_price))
            if t_price == 0.0 and u_price > 0.0:
                t_price = qty * u_price
            
            # Predict category if missing
            cat = item.get("category")
            if not cat or cat == "Other":
                cat = predict_category(name, merchant)["category"]

            calc_subtotal += t_price
            normalized_items.append({
                "name": name,
                "quantity": qty,
                "unit_price": round(u_price, 2),
                "total_price": round(t_price, 2),
                "category": cat
            })

        if subtotal == 0.0 and calc_subtotal > 0.0:
            subtotal = calc_subtotal

        if total == 0.0:
            total = subtotal + tax + gst

        # Determine overall category
        overall_cat = raw.get("category")
        if not overall_cat or overall_cat == "Other":
            overall_cat = predict_category(f"{merchant} {normalized_items[0]['name'] if normalized_items else ''}", merchant)["category"]

        return {
            "merchant_name": merchant,
            "transaction_date": date_str,
            "currency": currency,
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "gst": round(gst, 2),
            "total": round(total, 2),
            "items": normalized_items,
            "category": overall_cat,
            "confidence": float(raw.get("confidence") or 0.95)
        }

gemini_ocr_service = GeminiOCRService()
