from typing import Dict, Any, Optional
from backend.app.ml.model import DarkPatternClassifier
from backend.app.config import settings

# Global singleton classifier instance
_classifier: Optional[DarkPatternClassifier] = None

def get_classifier() -> DarkPatternClassifier:
    global _classifier
    if _classifier is None:
        _classifier = DarkPatternClassifier()
    return _classifier

EXPLANATIONS = {
    "Fake Urgency": "The text employs artificial urgency or countdown phrasing to pressure an expedited decision.",
    "Scarcity": "The text creates synthetic scarcity (low stock or viewer counts) prompting Fear Of Missing Out.",
    "Hidden Cost": "The text conceals or downplays additional transaction, booking, or handling surcharges.",
    "Trick Question": "The text uses confusing double negatives or reverse checkboxes to mislead user intent.",
    "Confirmshaming": "The text uses guilt or derogatory language in rejection choices to manipulate choice.",
    "Sneak Into Basket": "An additional product, warranty, or donation is slipped into the checkout without explicit consent.",
    "Forced Continuity": "A recurring subscription renewal is hidden behind a complimentary or low-cost initial trial.",
    "Disguised Advertisement": "Sponsored or advertising content styled identically to regular editorial or search results.",
    "Social Proof Manipulation": "Artificially generated or unverified peer activity claims inducing social pressure.",
    "Preselected Option": "A paid add-on, insurance, or marketing permission is pre-selected by default.",
    "Misleading Information": "Misleading crossed-out baseline pricing or fabricated original discount claims."
}

def predict_pattern(text: str) -> Dict[str, Any]:
    clf = get_classifier()
    pattern_type, confidence = clf.predict(text)

    # Determine confidence bracket
    if confidence >= settings.HIGH_CONFIDENCE_THRESHOLD:
        severity = "High"
    elif confidence >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
        severity = "Medium"
    else:
        severity = "Low"

    explanation = EXPLANATIONS.get(
        pattern_type,
        f"Language patterns characteristic of {pattern_type} detected."
    )

    return {
        "pattern_type": pattern_type,
        "confidence": round(confidence, 2),
        "severity": severity,
        "explanation": explanation,
        "is_dark_pattern": pattern_type != "Normal" and confidence >= settings.MEDIUM_CONFIDENCE_THRESHOLD
    }
