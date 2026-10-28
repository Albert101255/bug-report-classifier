from pathlib import Path

from app.auth.dependencies import require_role
from app.config import settings
from app.models import User
from app.schemas import ModelInfoResponse
from app.services.model_manager import model_manager
from app.services.training import train_baseline
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/models", tags=["Machine Learning Models"])


@router.get("/info", response_model=ModelInfoResponse)
async def get_model_info() -> ModelInfoResponse:
    info = model_manager.info()
    return ModelInfoResponse(
        model_version=info["model_version"],
        framework=info["framework"],
        tf_idf_vocab_size=info["tf_idf_vocab_size"],
        num_teams=info["num_teams"],
        confidence_threshold_high=info["confidence_threshold_high"],
        confidence_threshold_low=info["confidence_threshold_low"],
        last_trained_at=info["last_trained_at"],
        is_active=info["is_active"],
        training_dataset_provenance=info["training_dataset_provenance"],
        accuracy=info.get("accuracy"),
        macro_f1=info.get("macro_f1"),
    )


@router.post("/retrain", response_model=dict)
async def trigger_retraining(
    current_user: User = Depends(require_role(["ORG_ADMIN"])),
) -> dict:
    if not settings.ENABLE_RETRAINING:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Retraining is disabled in application settings.",
        )

    dataset_path = Path(settings.TRAINING_DATA_PATH)
    if not dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Training dataset not found: {dataset_path}",
        )

    try:
        metadata = train_baseline(dataset_path, Path(settings.MODEL_DIR))
        # Force reload in model_manager
        model_manager._load_artifacts()
        return {
            "success": True,
            "message": "Model retraining completed successfully and new artifacts are active.",
            "metrics": metadata,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model retraining failed: {exc}",
        ) from exc
