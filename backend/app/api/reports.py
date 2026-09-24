from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database.database import get_db
from backend.app.database.schemas import (
    ReportSummary, ScanResponse, DetectionItem, FeedbackCreate, FeedbackResponse
)
from backend.app.services.report_service import ReportService

router = APIRouter()

@router.get("/reports", response_model=List[ReportSummary])
def list_reports(limit: int = 20, db: Session = Depends(get_db)):
    scans = ReportService.get_recent_scans(db, limit=limit)
    summaries = []
    for s in scans:
        if s.overall_risk_score >= 60.0:
            level = "High"
        elif s.overall_risk_score >= 30.0:
            level = "Medium"
        else:
            level = "Low"
            
        summaries.append(ReportSummary(
            id=s.id,
            url=s.url,
            page_title=s.page_title,
            scan_time=s.scan_time,
            overall_risk_score=s.overall_risk_score,
            risk_level=level,
            total_patterns_detected=s.total_patterns_detected
        ))
    return summaries

@router.get("/reports/{scan_id}", response_model=ScanResponse)
def get_report_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = ReportService.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found.")

    if scan.overall_risk_score >= 60.0:
        level = "High"
    elif scan.overall_risk_score >= 30.0:
        level = "Medium"
    else:
        level = "Low"

    detections = []
    for d in scan.detections:
        detections.append(DetectionItem(
            id=d.id,
            type=d.pattern_type,
            confidence=d.confidence,
            severity=d.severity,
            text=d.detected_text,
            explanation=d.explanation,
            html_selector=d.html_selector,
            created_at=d.created_at
        ))

    return ScanResponse(
        id=scan.id,
        url=scan.url,
        page_title=scan.page_title,
        overall_risk_score=scan.overall_risk_score,
        risk_level=level,
        total_patterns_detected=scan.total_patterns_detected,
        detections=detections,
        scan_time=scan.scan_time
    )

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    try:
        feedback = ReportService.record_feedback(db, payload.detection_id, payload.user_feedback)
        return feedback
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to record feedback: {str(e)}")
