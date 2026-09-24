import pytest
from backend.app.ml.preprocessing import clean_text, extract_candidate_snippets
from backend.app.ml.model import DarkPatternClassifier
from backend.app.ml.predict import predict_pattern

def test_preprocessing_clean_text():
    raw = "<b>HURRY!</b>  Only ₹999   left!   "
    cleaned = clean_text(raw)
    assert "<b>" not in cleaned
    assert "hurry" in cleaned
    assert "currency" in cleaned

def test_extract_candidate_snippets():
    text = "Hurry up and buy now! Don't miss this deal. Standard delivery is free."
    snippets = extract_candidate_snippets(text)
    assert len(snippets) >= 2

def test_ml_prediction_pipeline():
    clf = DarkPatternClassifier()
    assert clf.is_loaded
    pred = predict_pattern("Hurry! Sale ends in 05:00 minutes!")
    assert "pattern_type" in pred
    assert "confidence" in pred
    assert "severity" in pred
    assert "explanation" in pred

def test_ml_prediction_normal():
    pred = predict_pattern("Customer reviews: 4.5 out of 5 stars with 120 ratings.")
    assert pred["pattern_type"] == "Normal" or pred["confidence"] < 0.85
