from typing import List, Dict, Any, Optional
from backend.app.detectors.urgency import UrgencyDetector
from backend.app.detectors.scarcity import ScarcityDetector
from backend.app.detectors.hidden_cost import HiddenCostDetector
from backend.app.detectors.trick_question import TrickQuestionDetector

class RuleEngine:
    def __init__(self):
        self.detectors = [
            UrgencyDetector(),
            ScarcityDetector(),
            HiddenCostDetector(),
            TrickQuestionDetector()
        ]

    def analyze_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        if not text or len(text.strip()) < 3:
            return results

        for detector in self.detectors:
            try:
                detection = detector.detect(text, context)
                if detection:
                    results.append(detection)
            except Exception as e:
                # Rule detector safeguard
                continue
                
        return results

    def analyze_element(self, text: str, tag: Optional[str] = None, selector: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        context = {
            "tag": tag,
            "selector": selector,
            "checked": attributes.get("checked", False) if attributes else False
        }
        detections = self.analyze_text(text, context)
        for d in detections:
            if selector and not d.get("html_selector"):
                d["html_selector"] = selector
        return detections
