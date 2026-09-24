import re
from typing import Optional, Dict, Any

TIMER_PATTERN = re.compile(r"\b(?:\d{1,2}:\d{2}(?::\d{2})?)\b", re.IGNORECASE)
COUNTDOWN_TEXT_PATTERN = re.compile(
    r"(\d+)\s*(?:hours?|hrs?|mins?|minutes?|seconds?|secs?)\s*(?:left|remaining)",
    re.IGNORECASE
)
EXPIRATION_PATTERN = re.compile(
    r"(?:deal|sale|offer|cart|discount|price|reservation)\s+(?:ends|expires|clears|resets)\s+(?:in|soon)",
    re.IGNORECASE
)

URGENT_KEYWORDS = [
    "limited time",
    "hurry",
    "hurry up",
    "only today",
    "expires today",
    "act now",
    "last chance",
    "offer ends",
    "flash sale",
    "dont miss out",
    "don't miss out",
    "clock is ticking",
    "running out"
]

class UrgencyDetector:
    @staticmethod
    def detect(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        clean_text = text.strip()
        lower_text = clean_text.lower()
        
        has_timer = bool(TIMER_PATTERN.search(clean_text))
        has_countdown_text = bool(COUNTDOWN_TEXT_PATTERN.search(clean_text))
        has_expiry = bool(EXPIRATION_PATTERN.search(clean_text))
        
        matched_keyword = next((kw for kw in URGENT_KEYWORDS if kw in lower_text), None)
        
        # High confidence when timer or explicit countdown is combined with urgency cues
        if has_timer and (matched_keyword or has_expiry):
            return {
                "pattern_type": "Fake Urgency",
                "confidence": 0.94,
                "detected_text": clean_text,
                "explanation": "Countdown timer coupled with purchase urgency cues pressuring an immediate transaction.",
                "severity": "High"
            }
            
        if has_countdown_text and (matched_keyword or has_expiry):
            return {
                "pattern_type": "Fake Urgency",
                "confidence": 0.90,
                "detected_text": clean_text,
                "explanation": "Explicit expiring time limit warning used to prompt hasty consumer decisions.",
                "severity": "High"
            }
            
        if matched_keyword and has_expiry:
            return {
                "pattern_type": "Fake Urgency",
                "confidence": 0.85,
                "detected_text": clean_text,
                "explanation": "Urgency phrasing emphasizing imminent expiration.",
                "severity": "Medium"
            }
            
        if matched_keyword:
            # Check context: buttons or banners
            return {
                "pattern_type": "Fake Urgency",
                "confidence": 0.72,
                "detected_text": clean_text,
                "explanation": f"Contains high-pressure urgency trigger phrase ('{matched_keyword}').",
                "severity": "Medium"
            }
            
        return None
