import time
from celery import Celery
from app.config import settings

celery_app = Celery(
    "bug_classifier_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="retrain_model_task")
def retrain_model_task(num_corrections: int):
    # Simulate a heavy machine learning retraining job
    time.sleep(10)

    # In a real scenario, this would trigger model.fit(...)
    return {
        "status": "success",
        "message": f"Successfully retrained model with {num_corrections} logged human corrections.",
        "corrections_processed": num_corrections,
    }
