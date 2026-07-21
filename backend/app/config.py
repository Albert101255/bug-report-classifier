import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bug Report Classifier Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bug_classifier.db")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "/home/albert/project 1/bug_classification_research/saved_models/tfidf_model")
    
    CONFIDENCE_HIGH_THRESHOLD: float = 0.05
    CONFIDENCE_LOW_THRESHOLD: float = 0.15
    
    RATE_LIMIT_PER_MINUTE: int = 100

settings = Settings()
