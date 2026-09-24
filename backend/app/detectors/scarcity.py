import re
from typing import Optional, Dict, Any

STOCK_COUNT_PATTERN = re.compile(
    r"\bonly\s+(\d+)\s+(?:items?|left|pieces?|units?|rooms?|seats?|tickets?|remaining|in stock)\b",
    re.IGNORECASE
)
ALMOST_GONE_PATTERN = re.compile(
    r"\b(?:almost sold out|few (?:items|pieces) left|low stock|selling fast)\b",
    re.IGNORECASE
)
SOCIAL_VIEW_PATTERN = re.compile(
    r"(\d+)\s+(?:people|shoppers|customers|guests)\s+(?:are )?(?:viewing|looking at|booked|have this in their cart)",
    re.IGNORECASE
)

class ScarcityDetector:
    @staticmethod
    def detect(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        clean_text = text.strip()
        lower_text = clean_text.lower()
        
        stock_match = STOCK_COUNT_PATTERN.search(clean_text)
        almost_gone = ALMOST_GONE_PATTERN.search(clean_text)
        social_match = SOCIAL_VIEW_PATTERN.search(clean_text)
        
        if stock_match:
            count = stock_match.group(1)
            return {
                "pattern_type": "Scarcity",
                "confidence": 0.91,
                "detected_text": clean_text,
                "explanation": f"Explicit low-stock claim ('only {count} left') stimulating fear of missing out.",
                "severity": "High"
            }
            
        if social_match:
            people = social_match.group(1)
            return {
                "pattern_type": "Social Proof Manipulation",
                "confidence": 0.88,
                "detected_text": clean_text,
                "explanation": f"Real-time viewer counter claim ('{people} people viewing') creating synthetic competition.",
                "severity": "Medium"
            }
            
        if almost_gone:
            return {
                "pattern_type": "Scarcity",
                "confidence": 0.82,
                "detected_text": clean_text,
                "explanation": "General scarcity phrasing ('almost sold out / low stock') to accelerate checkout.",
                "severity": "Medium"
            }
            
        return None
