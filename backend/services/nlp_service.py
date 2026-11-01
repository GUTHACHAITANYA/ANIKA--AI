import re
from datetime import datetime
from typing import Dict, Any, Optional
from backend.ml.predictor import predict_category

class NLPExpenseExtractor:
    """
    Structured NLP & Regex parser for natural language expense statements.
    Extracts person, amount, category, merchant, and dates deterministically.
    """

    # Common amount patterns: ₹1200, 1200 INR, Rs 1200, Rs. 1200, $50, 1200.50
    AMOUNT_REGEX = re.compile(r'(?:₹|rs\.?|inr|\$)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s*(?:₹|rs\.?|inr|\$)?', re.IGNORECASE)
    
    # Common verbs: paid, spent, gave, bill was, transferred
    PAYER_VERB_REGEX = re.compile(r'([A-Za-z]+)\s+(?:paid|spent|gave|cleared|transferred)\s+(?:₹|rs\.?|inr|\$)?\s*([0-9]+(?:\.[0-9]{1,2})?)', re.IGNORECASE)
    
    # Merchant indicators: at / for / from / to
    AT_MERCHANT_REGEX = re.compile(r'\b(?:at|from)\s+([A-Za-z0-9\s\'&]+?)(?:\s+(?:for|on|with|dated|yesterday|today)|\s*$)', re.IGNORECASE)
    FOR_DESC_REGEX = re.compile(r'\b(?:for|on)\s+([A-Za-z0-9\s\'&]+?)(?:\s+(?:at|from|with|dated|yesterday|today)|\s*$)', re.IGNORECASE)
    
    # Date indicators
    DATE_REGEX = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')

    @classmethod
    def parse_expense_text(cls, text: str) -> Dict[str, Any]:
        """
        Parses text like 'Chaitu paid 1200 for dinner at Pizza Hut' into structured expense dict.
        """
        if not text or not text.strip():
            return {
                "person": "Me",
                "amount": 0.0,
                "category": "Other",
                "merchant": "General Merchant",
                "description": "",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "confidence": 0.0
            }

        cleaned_text = text.strip()
        person = "Me"
        amount = 0.0
        merchant = ""
        description = ""
        date_str = datetime.now().strftime("%Y-%m-%d")
        confidence = 0.85

        # 1. Check payer + amount pattern: "Chaitu paid 1200"
        payer_match = cls.PAYER_VERB_REGEX.search(cleaned_text)
        if payer_match:
            person = payer_match.group(1).capitalize()
            try:
                amount = float(payer_match.group(2).replace(',', ''))
            except ValueError:
                amount = 0.0
        else:
            # Standalone amount
            all_amounts = cls.AMOUNT_REGEX.findall(cleaned_text)
            if all_amounts:
                # Pick the largest or first valid amount
                for a_str in all_amounts:
                    clean_a = a_str.replace(',', '').strip()
                    if clean_a:
                        try:
                            val = float(clean_a)
                            if val > 0:
                                amount = val
                                break
                        except ValueError:
                            pass

        # 2. Extract merchant
        merchant_match = cls.AT_MERCHANT_REGEX.search(cleaned_text)
        if merchant_match:
            merchant = merchant_match.group(1).strip()
        
        # 3. Extract description
        for_match = cls.FOR_DESC_REGEX.search(cleaned_text)
        if for_match:
            description = for_match.group(1).strip()
        else:
            description = cleaned_text

        # 4. Extract date
        date_match = cls.DATE_REGEX.search(cleaned_text)
        if date_match:
            date_str = date_match.group(1)

        # 5. Predict Category using trained ML model
        ml_result = predict_category(text=description or cleaned_text, merchant=merchant, amount=amount)
        category = ml_result.get("category", "Other")

        if not merchant:
            merchant = f"{category} Store"

        return {
            "person": person,
            "amount": amount,
            "category": category,
            "merchant": merchant,
            "description": description or f"{category} expense",
            "date": date_str,
            "confidence": ml_result.get("confidence", confidence),
            "ml_info": ml_result
        }
