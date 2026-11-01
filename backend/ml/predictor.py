import os
import re
from pathlib import Path
import joblib
import numpy as np
from backend.config import Config
from backend.utils.logger import logger

_MODEL_CACHE = None

DEFAULT_FALLBACK_RULES = [
    (r"(petrol|diesel|fuel|cng|shell|hpcl|bpcl|nayara|indian oil)", "Fuel"),
    (r"(swiggy|zomato|mcdonald|pizza|burger|starbucks|kfc|restaurant|cafe|dinner|lunch|breakfast)", "Food & Dining"),
    (r"(blinkit|zepto|instamart|bigbasket|dmart|grocery|kirana|milk|vegetable|fruit|supermarket)", "Groceries"),
    (r"(amazon|flipkart|myntra|zara|h&m|ajio|shopping|shirt|shoes|electronics|apparel)", "Shopping"),
    (r"(uber|ola|rapido|metro|auto|taxi|cab|ride|transit)", "Transport"),
    (r"(apollo|pharmacy|medplus|1mg|doctor|clinic|hospital|medicine|dental|pathlabs)", "Healthcare"),
    (r"(netflix|spotify|bookmyshow|pvr|cinema|movie|hotstar|prime|game|steam|playstation)", "Entertainment"),
    (r"(electricity|power|bescom|tata power|gas bill|water bill|wifi|broadband|airtel xstream|jiofiber)", "Utilities"),
    (r"(makemytrip|irctc|indigo|flight|hotel|airbnb|travel|train ticket|resort)", "Travel"),
    (r"(coursera|udemy|tuition|books|college|exam|certification|school|course)", "Education"),
    (r"(recharge|postpaid|airtel|jio|credit card|lic|insurance|premium|statement)", "Bills")
]

def load_category_model():
    """Load serialized category classifier bundle with memory caching."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model_path = Config.CATEGORY_MODEL_PATH
    if os.path.exists(model_path):
        try:
            bundle = joblib.load(model_path)
            _MODEL_CACHE = bundle
            logger.info(f"Loaded category ML model from {model_path}")
            return _MODEL_CACHE
        except Exception as e:
            logger.error(f"Failed loading ML model from {model_path}: {e}")

    return None

def fallback_rule_classifier(text: str) -> tuple[str, float]:
    """Resilient regex fallback when ML model is initializing or unavailable."""
    text_lower = text.lower()
    for pattern, category in DEFAULT_FALLBACK_RULES:
        if re.search(pattern, text_lower):
            return category, 0.85
    return "Other", 0.50

def predict_category(text: str, merchant: str = "", amount: float = 0.0) -> dict:
    """
    Predicts expense category using trained scikit-learn model with confidence.
    Gracefully falls back to heuristic patterns if needed.
    """
    combined_text = f"{merchant} {text}".strip()
    if not combined_text:
        return {
            "category": "Other",
            "confidence": 0.50,
            "top_predictions": [{"category": "Other", "confidence": 0.50}],
            "model_used": "fallback_empty"
        }

    bundle = load_category_model()

    if bundle and 'pipeline' in bundle:
        try:
            pipeline = bundle['pipeline']
            probs = pipeline.predict_proba([combined_text])[0]
            classes = pipeline.classes_

            top_indices = np.argsort(probs)[::-1][:3]
            top_predictions = [
                {"category": classes[i], "confidence": round(float(probs[i]), 4)}
                for i in top_indices
            ]

            best_cat = classes[top_indices[0]]
            best_conf = round(float(probs[top_indices[0]]), 4)

            logger.info(f"ML Prediction: '{combined_text}' -> {best_cat} ({best_conf * 100:.1f}%)")
            return {
                "category": best_cat,
                "confidence": best_conf,
                "top_predictions": top_predictions,
                "model_used": "scikit_learn_tfidf_logistic_regression"
            }
        except Exception as e:
            logger.warning(f"Error during ML inference: {e}. Using fallback classifier.")

    # Rule-based fallback
    cat, conf = fallback_rule_classifier(combined_text)
    return {
        "category": cat,
        "confidence": conf,
        "top_predictions": [{"category": cat, "confidence": conf}],
        "model_used": "rule_based_fallback"
    }
