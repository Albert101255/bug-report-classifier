from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from serving.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bug_description = Column(Text, nullable=False)
    bug_title = Column(String(500), nullable=True)
    predicted_team = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, default=0.0)
    model_version = Column(String(50), default="v1.0-tfidf-mc")
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), default="anonymous")
    
    feedbacks = relationship("Feedback", back_populates="prediction", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"))
    human_label = Column(String(100), nullable=False)
    reason = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), default="human_reviewer")
    
    prediction = relationship("Prediction", back_populates="feedbacks")

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(50), nullable=False)
    accuracy = Column(Float, default=0.92)
    precision = Column(Float, default=0.91)
    recall = Column(Float, default=0.90)
    f1_score = Column(Float, default=0.905)
    training_date = Column(DateTime, default=datetime.utcnow)
    test_set_size = Column(Integer, default=500)

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    backlog_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
