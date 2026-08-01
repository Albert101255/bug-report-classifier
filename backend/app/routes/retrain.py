from pathlib import Path

from app.config import settings
from app.schemas import ModelInfoResponse
from app.security import require_admin_key
from app.services.model_manager import model_manager
from app.worker import retrain_model_task
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/models", tags=["Model Management"])


@router.get("/info", response_model=ModelInfoResponse)
async def get_model_info() -> ModelInfoResponse:
    return ModelInfoResponse(**model_manager.info())


@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
async def trigger_retraining(_: None = Depends(require_admin_key)) -> dict:
    if not settings.ENABLE_RETRAINING:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Retraining is disabled. Set ENABLE_RETRAINING=true to enable it.",
        )

    dataset_path = Path(settings.TRAINING_DATA_PATH)
    if not dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Training dataset not found: {dataset_path}",
        )

    task = retrain_model_task.delay(str(dataset_path))
    return {
        "accepted": True,
        "task_id": task.id,
        "message": "Baseline retraining was queued. The API reloads new artifacts automatically.",
    }
