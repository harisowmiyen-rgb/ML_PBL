import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env")

    PROJECT_NAME: str = "Dark Pattern Detector API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "default-dev-secret-key-replace-in-production"
    
    # Database: SQLite fallback if postgres not configured/available
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dark_patterns.db")
    
    # ML & Fusion Weights
    MODEL_PATH: str = os.getenv("MODEL_PATH", "ml/models/dark-pattern-distilbert")
    ML_WEIGHT: float = float(os.getenv("ML_WEIGHT", 0.60))
    RULE_WEIGHT: float = float(os.getenv("RULE_WEIGHT", 0.40))
    HIGH_CONFIDENCE_THRESHOLD: float = 0.80
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.60
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()
