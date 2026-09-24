import re
from typing import Optional, Dict, Any

CONFIRMSHAMING_TRIGGERS = [
    "no thanks, i hate saving",
    "no, i prefer paying full price",
    "no, i don't like discounts",
    "no, i don't care about",
    "i would rather waste money",
    "no thanks, i dont want to save",
    "no, thanks, i like to spend more"
]

TRICK_CHECKBOX_TRIGGERS = [
    "uncheck if you do not wish to opt out",
    "uncheck to decline",
    "check here if you do not want",
    "leave unticked to reject",
    "do not uncheck this box"
]

PRESELECTED_TRIGGERS = [
    "sign me up for auto-renew",
    "automatically renew",
    "add protection plan",
    "include express priority",
    "join our vip membership"
]

class TrickQuestionDetector:
    @staticmethod
    def detect(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        clean_text = text.strip()
        lower_text = clean_text.lower()
        
        # 1. Confirmshaming Check
        for cs in CONFIRMSHAMING_TRIGGERS:
            if cs in lower_text:
                return {
                    "pattern_type": "Confirmshaming",
                    "confidence": 0.95,
                    "detected_text": clean_text,
                    "explanation": "Guilt-inducing decline option designed to shame or emotionally manipulate the user.",
                    "severity": "High"
                }
                
        # 2. Trick Double Negative Checkboxes
        for tc in TRICK_CHECKBOX_TRIGGERS:
            if tc in lower_text:
                return {
                    "pattern_type": "Trick Question",
                    "confidence": 0.92,
                    "detected_text": clean_text,
                    "explanation": "Confusing double-negative wording in opt-in/opt-out choice creating deceptive consent.",
                    "severity": "High"
                }
                
        # 3. Preselected recurring or paid option (if tag is checkbox or attribute checked)
        if context and context.get("checked") is True:
            for pt in PRESELECTED_TRIGGERS:
                if pt in lower_text:
                    return {
                        "pattern_type": "Preselected Option",
                        "confidence": 0.89,
                        "detected_text": clean_text,
                        "explanation": f"Pre-selected opt-in option ('{pt}') for additional fees or recurring subscriptions.",
                        "severity": "High"
                    }
                    
        return None
