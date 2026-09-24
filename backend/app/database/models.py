from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    url = Column(Text, nullable=False, index=True)
    page_title = Column(String(500), nullable=True)
    scan_time = Column(DateTime, default=datetime.utcnow)
    overall_risk_score = Column(Float, nullable=False, default=0.0)
    total_patterns_detected = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="scans")
    detections = relationship("Detection", back_populates="scan", cascade="all, delete-orphan")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    detected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    html_selector = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="detections")
    feedback_items = relationship("Feedback", back_populates="detection", cascade="all, delete-orphan")
    predictions = relationship("ModelPrediction", back_populates="detection", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, index=True)
    user_feedback = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("Detection", back_populates="feedback_items")

class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    predicted_class = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("Detection", back_populates="predictions")
