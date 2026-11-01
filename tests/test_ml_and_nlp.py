import pytest
from backend.ml.predictor import predict_category
from backend.services.nlp_service import NLPExpenseExtractor

def test_ml_prediction_fuel():
    res = predict_category("Shell petrol station")
    assert res['category'] == "Fuel"
    assert res['confidence'] > 0.40

def test_ml_prediction_food_and_dining():
    res = predict_category("Pizza Hut dinner with friends")
    assert res['category'] == "Food & Dining"
    assert res['confidence'] > 0.40

def test_ml_prediction_shopping():
    res = predict_category("Amazon shoes and running sneakers")
    assert res['category'] == "Shopping"
    assert res['confidence'] > 0.40

def test_ml_prediction_healthcare():
    res = predict_category("Apollo pharmacy antibiotic prescription")
    assert res['category'] == "Healthcare"
    assert res['confidence'] > 0.40

def test_ml_prediction_entertainment():
    res = predict_category("Netflix streaming subscription renewal")
    assert res['category'] == "Entertainment"
    assert res['confidence'] > 0.40

def test_nlp_extraction_chaitu_dinner():
    text = "Chaitu paid 1200 for dinner"
    parsed = NLPExpenseExtractor.parse_expense_text(text)
    
    assert parsed['person'] == "Chaitu"
    assert parsed['amount'] == 1200.0
    assert parsed['category'] == "Food & Dining"

def test_nlp_extraction_with_merchant():
    text = "Ramu spent ₹450 at Starbucks for coffee"
    parsed = NLPExpenseExtractor.parse_expense_text(text)
    
    assert parsed['person'] == "Ramu"
    assert parsed['amount'] == 450.0
    assert "Starbucks" in parsed['merchant']
    assert parsed['category'] == "Food & Dining"
