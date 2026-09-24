import re
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.detectors.rule_engine import RuleEngine
from backend.app.ml.predict import predict_pattern
from backend.app.database.schemas import ScanRequest, ScanResponse, DetectionItem

# Heuristic weights for overall risk score
PATTERN_RISK_WEIGHTS = {
    "Fake Urgency": 30.0,
    "Hidden Cost": 30.0,
    "Trick Question": 20.0,
    "Confirmshaming": 20.0,
    "Scarcity": 10.0,
    "Sneak Into Basket": 20.0,
    "Forced Continuity": 25.0,
    "Social Proof Manipulation": 15.0,
    "Preselected Option": 15.0,
    "Disguised Advertisement": 10.0,
    "Misleading Information": 15.0
}

class ScannerService:
    def __init__(self):
        self.rule_engine = RuleEngine()

    def calculate_risk(self, detections: List[Dict[str, Any]]) -> (float, str):
        if not detections:
            return 0.0, "Low"

        total_weight = 0.0
        for d in detections:
            ptype = d["pattern_type"]
            conf = d["confidence"]
            weight = PATTERN_RISK_WEIGHTS.get(ptype, 10.0)
            total_weight += (weight * conf)

        # Normalize score to 0 - 100 range
        risk_score = min(100.0, round(total_weight, 1))

        if risk_score >= 60.0:
            level = "High"
        elif risk_score >= 30.0:
            level = "Medium"
        else:
            level = "Low"

        return risk_score, level

    def scan_page(self, req: ScanRequest) -> Dict[str, Any]:
        raw_detections: List[Dict[str, Any]] = []

        # 1. Analyze targeted DOM elements passed from extension
        if req.elements:
            for el in req.elements:
                if not el.text or len(el.text.strip()) < 3:
                    continue
                
                # Run Rule Engine
                rule_hits = self.rule_engine.analyze_element(
                    text=el.text,
                    tag=el.tag,
                    selector=el.selector,
                    attributes=el.attributes
                )
                
                # Run ML Classifier
                ml_res = predict_pattern(el.text)
                
                if rule_hits:
                    for rh in rule_hits:
                        # Prediction fusion: 0.6 ML + 0.4 Rule if same category
                        if ml_res["is_dark_pattern"] and ml_res["pattern_type"] == rh["pattern_type"]:
                            combined_conf = round(
                                (settings.ML_WEIGHT * ml_res["confidence"]) + 
                                (settings.RULE_WEIGHT * rh["confidence"]), 2
                            )
                            rh["confidence"] = combined_conf
                        rh["html_selector"] = el.selector
                        raw_detections.append(rh)
                elif ml_res["is_dark_pattern"]:
                    raw_detections.append({
                        "pattern_type": ml_res["pattern_type"],
                        "confidence": ml_res["confidence"],
                        "detected_text": el.text.strip(),
                        "explanation": ml_res["explanation"],
                        "severity": ml_res["severity"],
                        "html_selector": el.selector
                    })

        # 2. Analyze general raw text or body text snippets if elements empty
        if not req.elements and req.text:
            from backend.app.ml.preprocessing import extract_candidate_snippets
            snippets = extract_candidate_snippets(req.text)
            for snippet in snippets:
                rule_hits = self.rule_engine.analyze_text(snippet)
                ml_res = predict_pattern(snippet)
                if rule_hits:
                    raw_detections.extend(rule_hits)
                elif ml_res["is_dark_pattern"]:
                    raw_detections.append({
                        "pattern_type": ml_res["pattern_type"],
                        "confidence": ml_res["confidence"],
                        "detected_text": snippet,
                        "explanation": ml_res["explanation"],
                        "severity": ml_res["severity"],
                        "html_selector": None
                    })

        # 3. Deduplicate detections by detected text
        seen = set()
        deduped = []
        for d in raw_detections:
            key = d["detected_text"].lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(d)

        risk_score, risk_level = self.calculate_risk(deduped)

        return {
            "url": req.url,
            "page_title": req.page_title,
            "overall_risk_score": risk_score,
            "risk_level": risk_level,
            "total_patterns_detected": len(deduped),
            "detections": deduped
        }
