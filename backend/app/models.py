from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bug_description: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    predicted_team: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False) # e.g. 0.94 (94%)
    uncertainty_score: Mapped[float] = mapped_column(Float, nullable=False) # Standard deviation Monte Carlo variance
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False) # HIGH / MEDIUM / LOW
    status: Mapped[str] = mapped_column(String(30), default="auto_assigned") # auto_assigned / needs_review / human_corrected
    top_alternatives: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    top_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    user_id: Mapped[str] = mapped_column(String(50), default="anonymous")
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0-tfidf-mc")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="prediction", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prediction_id: Mapped[str] = mapped_column(String(36), ForeignKey("predictions.id"), nullable=False)
    original_team: Mapped[str] = mapped_column(String(100), nullable=False)
    corrected_team: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_user_id: Mapped[str] = mapped_column(String(50), default="human_reviewer")
    is_retrained: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="feedbacks")

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    val_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.15)
    total_predictions: Mapped[int] = mapped_column(Integer, default=0)
    human_correction_rate: Mapped[float] = mapped_column(Float, default=0.0)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Team(Base):
    __tablename__ = "teams"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. BL-101
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Core Engineering")
    accuracy_rate: Mapped[float] = mapped_column(Float, default=92.5)
    total_bugs_assigned: Mapped[int] = mapped_column(Integer, default=0)
