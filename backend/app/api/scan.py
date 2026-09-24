from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.database.schemas import ScanRequest, ScanResponse, DetectionItem
from backend.app.services.scanner import ScannerService
from backend.app.services.report_service import ReportService

router = APIRouter()
scanner_service = ScannerService()

@router.post("/scan", response_model=ScanResponse)
def perform_scan(payload: ScanRequest, db: Session = Depends(get_db)):
    if not payload.url:
        raise HTTPException(status_code=400, detail="Target URL is required for scanning.")

    # Execute hybrid detection pipeline
    result = scanner_service.scan_page(payload)

    # Persist to database
    try:
        saved_scan = ReportService.save_scan_result(db, result)
        result["id"] = saved_scan.id
        result["scan_time"] = saved_scan.scan_time
        
        # Enrich detection items with generated database IDs
        for idx, det_record in enumerate(saved_scan.detections):
            if idx < len(result["detections"]):
                result["detections"][idx]["id"] = det_record.id
                result["detections"][idx]["created_at"] = det_record.created_at
    except Exception as e:
        print(f"[Database Error] Could not persist scan: {e}")

    # Map to schema output
    items = []
    for d in result["detections"]:
        items.append(DetectionItem(
            id=d.get("id"),
            type=d["pattern_type"],
            confidence=d["confidence"],
            severity=d["severity"],
            text=d["detected_text"],
            explanation=d["explanation"],
            html_selector=d.get("html_selector"),
            created_at=d.get("created_at")
        ))

    return ScanResponse(
        id=result.get("id"),
        url=result["url"],
        page_title=result.get("page_title"),
        overall_risk_score=result["overall_risk_score"],
        risk_level=result["risk_level"],
        total_patterns_detected=result["total_patterns_detected"],
        detections=items,
        scan_time=result.get("scan_time")
    )
