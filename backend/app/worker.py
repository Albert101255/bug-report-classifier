from pathlib import Path

from celery import Celery

from app.config import settings
from app.services.training import train_baseline

celery_app = Celery(
    "bug_classifier_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="retrain_model_task")
def retrain_model_task(dataset_path: str | None = None) -> dict:
    metadata = train_baseline(
        Path(dataset_path or settings.TRAINING_DATA_PATH),
        Path(settings.MODEL_DIR),
    )
    return {"status": "success", **metadata}
