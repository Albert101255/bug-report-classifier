from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./bug_classifier.db"
)

# Convert async sqlite/postgres url if passed for sync engine
sync_db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")

engine = create_engine(
    sync_db_url,
    connect_args={"check_same_thread": False} if "sqlite" in sync_db_url else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
