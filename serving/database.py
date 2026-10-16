import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv(
    "SERVING_DATABASE_URL",
    os.getenv("DATABASE_URL", "sqlite:///./serving_classifier.db"),
)

# Convert async sqlite/postgres url if passed for sync engine
sync_db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace(
    "sqlite+aiosqlite://", "sqlite://"
)

engine_kwargs = {
    "connect_args": {"check_same_thread": False} if "sqlite" in sync_db_url else {},
    "pool_pre_ping": True,
}
if sync_db_url in ("sqlite://", "sqlite:///:memory:"):
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(sync_db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
