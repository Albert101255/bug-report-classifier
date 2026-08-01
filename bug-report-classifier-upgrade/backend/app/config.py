from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Bug Report Triage Platform"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./bug_classifier.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    MODEL_DIR: Path = Path("saved_models/tfidf_model")
    TRAINING_DATA_PATH: Path = Path("data/demo_bug_reports.csv")
    MODEL_RELOAD_SECONDS: int = 5

    # Uncertainty is 1 - predicted probability. Lower is better.
    CONFIDENCE_HIGH_THRESHOLD: float = 0.25
    CONFIDENCE_LOW_THRESHOLD: float = 0.50

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    ADMIN_API_KEY: str | None = None
    ENABLE_RETRAINING: bool = False
    SEED_DEMO_DATA: bool = False
    MAX_BATCH_SIZE: int = 100
    RATE_LIMIT_PER_MINUTE: int = 100

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
