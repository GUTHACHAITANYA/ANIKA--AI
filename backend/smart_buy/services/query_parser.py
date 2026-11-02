"""
Natural-language query parser for Smart Buy.

Uses Gemini AI to extract structured intent from user queries.
Falls back to simple keyword extraction when Gemini is unavailable.
"""
import os
import json
import re
from typing import Optional

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

# ── Gemini setup ─────────────────────────────────────────────────────────────
_GEMINI_MODEL = None

def _get_model():
    global _GEMINI_MODEL
    if _GEMINI_MODEL is None and _HAS_GENAI:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            _GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
    return _GEMINI_MODEL


_PARSE_PROMPT = """\
You are a shopping query parser. Extract structured intent from the user's product search query.
Return ONLY a valid JSON object with these fields (no markdown, no explanation):
{
  "product_name": "<concise product name>",
  "category": "<one of: smartphone, laptop, tablet, headphone, earphone, tv, washing_machine, refrigerator, camera, shoe, clothing, general>",
  "brand": "<brand if mentioned, else empty string>",
  "model": "<model if mentioned, else empty string>",
  "budget_max": <max budget in INR as integer, or null>,
  "specs": {
    "ram": "<e.g. 16GB or null>",
    "storage": "<e.g. 256GB or null>",
    "screen_size": "<e.g. 55 inch or null>",
    "color": "<color if mentioned or null>"
  },
  "sort": "highest_discount"
}

User query: """


def parse_query(query: str) -> dict:
    """
    Parse a natural-language shopping query into structured intent.

    Returns a dict with keys:
      product_name, category, brand, model, budget_max, specs, sort
    """
    model = _get_model()
    if model:
        try:
            response = model.generate_content(_PARSE_PROMPT + query)
            text = response.text.strip()
            # Strip markdown code fences if present
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            parsed = json.loads(text)
            # Ensure required keys exist
            parsed.setdefault("product_name", query)
            parsed.setdefault("category", "general")
            parsed.setdefault("brand", "")
            parsed.setdefault("model", "")
            parsed.setdefault("budget_max", None)
            parsed.setdefault("specs", {})
            parsed.setdefault("sort", "highest_discount")
            return parsed
        except Exception:
            pass

    # ── Fallback: simple keyword extraction ──────────────────────────────────
    return _fallback_parse(query)


def _fallback_parse(query: str) -> dict:
    """Simple regex-based extraction used when Gemini is unavailable."""
    q = query.lower()

    # Budget
    budget_max = None
    budget_match = re.search(r"under\s+[₹rs\.]*\s*([\d,]+)", q)
    if budget_match:
        budget_max = int(budget_match.group(1).replace(",", ""))

    # Category keywords
    category = "general"
    for cat, keywords in _CATEGORY_MAP.items():
        if any(kw in q for kw in keywords):
            category = cat
            break

    # Brand
    brand = ""
    for b in _KNOWN_BRANDS:
        if b in q:
            brand = b.title()
            break

    return {
        "product_name": query.strip(),
        "category": category,
        "brand": brand,
        "model": "",
        "budget_max": budget_max,
        "specs": {},
        "sort": "highest_discount",
    }


_CATEGORY_MAP = {
    "smartphone": ["phone", "smartphone", "mobile", "iphone", "galaxy", "pixel", "oneplus", "redmi", "realme", "poco"],
    "laptop": ["laptop", "notebook", "macbook", "chromebook", "ultrabook"],
    "tablet": ["tablet", "ipad", "tab"],
    "headphone": ["headphone", "headset", "over-ear", "on-ear"],
    "earphone": ["earphone", "earbuds", "tws", "airpods", "buds"],
    "tv": ["tv", "television", "smart tv", "oled", "qled", "4k tv"],
    "washing_machine": ["washing machine", "washer", "front load", "top load"],
    "refrigerator": ["refrigerator", "fridge", "freezer"],
    "camera": ["camera", "dslr", "mirrorless", "gopro", "action cam"],
    "shoe": ["shoes", "sneakers", "footwear", "boots", "sandals"],
    "clothing": ["shirt", "jeans", "dress", "clothing", "t-shirt", "kurta"],
}

_KNOWN_BRANDS = [
    "apple", "samsung", "oneplus", "xiaomi", "redmi", "realme", "poco", "oppo", "vivo",
    "sony", "lg", "hp", "dell", "lenovo", "asus", "acer", "msi", "microsoft",
    "boat", "jbl", "bose", "sennheiser", "skullcandy", "noise",
    "nike", "adidas", "puma", "reebok", "new balance",
    "whirlpool", "ifb", "bosch", "haier", "godrej",
]

