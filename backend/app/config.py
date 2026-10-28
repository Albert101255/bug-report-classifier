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

    PROJECT_NAME: str = "Triage"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./bug_classifier.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Authentication & Security
    JWT_SECRET_KEY: str = "triage_super_secure_jwt_secret_key_change_in_production_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    MODEL_DIR: Path = Path("saved_models/tfidf_model")
    TRAINING_DATA_PATH: Path = Path("data/training_dataset.jsonl")
    MODEL_RELOAD_SECONDS: int = 5

    # Confidence Thresholds
    CONFIDENCE_HIGH_THRESHOLD: float = 0.25
    CONFIDENCE_LOW_THRESHOLD: float = 0.50

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    ADMIN_API_KEY: str | None = None
    ENABLE_RETRAINING: bool = True
    SEED_DEMO_DATA: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    # GitHub Integration
    GITHUB_TOKEN: str | None = None
    GITHUB_DEFAULT_REPO: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
