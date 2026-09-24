import pytest
from backend.app.detectors.urgency import UrgencyDetector
from backend.app.detectors.scarcity import ScarcityDetector
from backend.app.detectors.hidden_cost import HiddenCostDetector
from backend.app.detectors.trick_question import TrickQuestionDetector
from backend.app.detectors.rule_engine import RuleEngine

def test_urgency_detector_positive():
    res = UrgencyDetector.detect("Hurry! Deal expires in 05:00 minutes!")
    assert res is not None
    assert res["pattern_type"] == "Fake Urgency"
    assert res["confidence"] >= 0.85
    assert res["severity"] == "High"

def test_urgency_detector_negative():
    res = UrgencyDetector.detect("Standard delivery takes 3 to 5 business days.")
    assert res is None

def test_scarcity_detector():
    res = ScarcityDetector.detect("Only 2 items left in stock - order soon!")
    assert res is not None
    assert res["pattern_type"] == "Scarcity"
    assert res["confidence"] >= 0.80

def test_social_proof_scarcity():
    res = ScarcityDetector.detect("24 people are viewing this product right now!")
    assert res is not None
    assert res["pattern_type"] == "Social Proof Manipulation"

def test_hidden_cost_detector():
    res = HiddenCostDetector.detect("Mandatory order processing fee of ₹149 added at payment")
    assert res is not None
    assert res["pattern_type"] == "Hidden Cost"

def test_confirmshaming_detector():
    res = TrickQuestionDetector.detect("No thanks, I hate saving money and prefer paying full price")
    assert res is not None
    assert res["pattern_type"] == "Confirmshaming"

def test_rule_engine_integration():
    engine = RuleEngine()
    hits = engine.analyze_text("Hurry! Only 1 item left in stock!")
    assert len(hits) >= 1
    types = [h["pattern_type"] for h in hits]
    assert "Scarcity" in types or "Fake Urgency" in types
