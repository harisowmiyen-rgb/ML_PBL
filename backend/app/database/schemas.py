from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class FeedbackCreate(BaseModel):
    detection_id: int
    user_feedback: str = Field(..., description="User assessment, e.g. 'Correct' or 'Incorrect'")

class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    detection_id: int
    user_feedback: str
    created_at: datetime

class ModelPredictionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    model_name: str
    confidence: float
    predicted_class: str

class DetectionItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: Optional[int] = None
    type: str
    confidence: float
    severity: str
    text: str
    explanation: str
    html_selector: Optional[str] = None
    created_at: Optional[datetime] = None

class DOMElementInput(BaseModel):
    text: str
    tag: Optional[str] = None
    selector: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class ScanRequest(BaseModel):
    url: str
    page_title: Optional[str] = "E-Commerce Page"
    text: Optional[str] = ""
    html: Optional[str] = ""
    elements: Optional[List[DOMElementInput]] = []

class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    url: str
    page_title: Optional[str] = None
    overall_risk_score: float
    risk_level: str
    total_patterns_detected: int
    detections: List[DetectionItem]
    scan_time: Optional[datetime] = None

class ReportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    page_title: Optional[str] = None
    scan_time: datetime
    overall_risk_score: float
    risk_level: str
    total_patterns_detected: int
