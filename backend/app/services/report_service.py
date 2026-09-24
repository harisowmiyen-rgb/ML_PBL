from sqlalchemy.orm import Session
from backend.app.database.models import Scan, Detection, Feedback, ModelPrediction
from typing import Dict, Any, List, Optional

class ReportService:
    @staticmethod
    def save_scan_result(db: Session, scan_data: Dict[str, Any]) -> Scan:
        scan_record = Scan(
            url=scan_data["url"],
            page_title=scan_data.get("page_title"),
            overall_risk_score=scan_data["overall_risk_score"],
            total_patterns_detected=scan_data["total_patterns_detected"]
        )
        db.add(scan_record)
        db.flush()

        for d in scan_data["detections"]:
            det_record = Detection(
                scan_id=scan_record.id,
                pattern_type=d["pattern_type"],
                confidence=d["confidence"],
                detected_text=d["detected_text"],
                explanation=d["explanation"],
                severity=d["severity"],
                html_selector=d.get("html_selector")
            )
            db.add(det_record)
            db.flush()

            # Record model prediction entry
            pred_record = ModelPrediction(
                detection_id=det_record.id,
                model_name="DistilBERT-DarkPatterns",
                confidence=d["confidence"],
                predicted_class=d["pattern_type"]
            )
            db.add(pred_record)

        db.commit()
        db.refresh(scan_record)
        return scan_record

    @staticmethod
    def get_recent_scans(db: Session, limit: int = 20) -> List[Scan]:
        return db.query(Scan).order_by(Scan.scan_time.desc()).limit(limit).all()

    @staticmethod
    def get_scan_by_id(db: Session, scan_id: int) -> Optional[Scan]:
        return db.query(Scan).filter(Scan.id == scan_id).first()

    @staticmethod
    def record_feedback(db: Session, detection_id: int, user_feedback: str) -> Feedback:
        feedback = Feedback(
            detection_id=detection_id,
            user_feedback=user_feedback
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
