import re
from typing import Optional, Dict, Any

HIDDEN_COST_KEYWORDS = [
    "mandatory fee",
    "mandatory handling",
    "convenience fee",
    "service fee added",
    "platform fee",
    "administrative surcharge",
    "handling charge",
    "checkout fee",
    "booking fee added",
    "drip fee",
    "order processing fee"
]

class HiddenCostDetector:
    @staticmethod
    def detect(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        clean_text = text.strip()
        lower_text = clean_text.lower()
        
        matched_cost = next((kw for kw in HIDDEN_COST_KEYWORDS if kw in lower_text), None)
        
        if matched_cost:
            return {
                "pattern_type": "Hidden Cost",
                "confidence": 0.86,
                "detected_text": clean_text,
                "explanation": f"Potential drip pricing fee detected ('{matched_cost}') that may not be shown on product pages.",
                "severity": "High"
            }
            
        # Check context for fee discrepancies
        if context and "base_price" in context and "final_price" in context:
            base = float(context.get("base_price", 0))
            final = float(context.get("final_price", 0))
            if base > 0 and final > base * 1.25: # More than 25% discrepancy without user selection
                return {
                    "pattern_type": "Hidden Cost",
                    "confidence": 0.88,
                    "detected_text": f"Base: {base}, Final: {final}",
                    "explanation": "Noticeable price inflation between base listing and payment step without clear add-ons.",
                    "severity": "High"
                }
                
        return None
