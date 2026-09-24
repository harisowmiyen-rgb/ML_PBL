import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.database import init_db

# Ensure tables are created for tests
init_db()

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Dark Pattern Detector API"
    assert data["status"] == "running"

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_scan_endpoint():
    payload = {
        "url": "https://test-shop.com/deals",
        "page_title": "Fast Mega Deals",
        "text": "Hurry! Only 2 items left in stock before this deal expires in 04:00 minutes!",
        "elements": [
            {
                "text": "Only 2 items left in stock!",
                "tag": "div",
                "selector": "#stock-alert"
            },
            {
                "text": "Deal expires in 04:00 minutes!",
                "tag": "span",
                "selector": ".countdown"
            }
        ]
    }
    res = client.post("/api/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["url"] == payload["url"]
    assert "overall_risk_score" in data
    assert "risk_level" in data
    assert data["total_patterns_detected"] >= 1
    assert len(data["detections"]) >= 1

def test_reports_and_feedback():
    res = client.get("/api/reports")
    assert res.status_code == 200
    reports = res.json()
    assert isinstance(reports, list)

    if len(reports) > 0:
        scan_id = reports[0]["id"]
        detail_res = client.get(f"/api/reports/{scan_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["id"] == scan_id
        
        if len(detail_data["detections"]) > 0:
            det_id = detail_data["detections"][0]["id"]
            fb_res = client.post("/api/feedback", json={
                "detection_id": det_id,
                "user_feedback": "Correct"
            })
            assert fb_res.status_code == 200
            assert fb_res.json()["user_feedback"] == "Correct"
