from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter()

@router.get("/")
def root_info():
    return {
        "message": "Dark Pattern Detector API",
        "status": "running"
    }

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
