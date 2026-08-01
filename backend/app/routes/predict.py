import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.metrics import PREDICTION_LATENCY, PREDICTIONS_TOTAL
from app.models import Prediction
from app.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    SinglePredictRequest,
    SinglePredictResponse,
)
from app.services.model_manager import model_manager

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _response(
    prediction_id: str, request: SinglePredictRequest, result: dict
) -> SinglePredictResponse:
    return SinglePredictResponse(
        id=prediction_id,
        bug_description=request.description,
        subject=request.subject,
        predicted_team=result["predicted_team"],
        confidence_score=result["confidence_score"],
        uncertainty_score=result["uncertainty_score"],
        confidence_level=result["confidence_level"],
        status=result["status"],
        top_alternatives=result["top_alternatives"],
        top_keywords=result["top_keywords"],
        latency_ms=result["latency_ms"],
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _database_record(
    prediction_id: str, request: SinglePredictRequest, result: dict
) -> Prediction:
    return Prediction(
        id=prediction_id,
        bug_description=request.description,
        subject=request.subject,
        predicted_team=result["predicted_team"],
        confidence_score=result["confidence_score"],
        uncertainty_score=result["uncertainty_score"],
        confidence_level=result["confidence_level"],
        status=result["status"],
        top_alternatives=result["top_alternatives"],
        top_keywords=result["top_keywords"],
        latency_ms=result["latency_ms"],
        user_id=request.user_id or "anonymous",
        model_version=result["model_version"],
    )


async def _run_prediction(request: SinglePredictRequest) -> dict:
    try:
        result = await run_in_threadpool(
            model_manager.predict,
            request.description,
            request.subject or "",
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    PREDICTIONS_TOTAL.labels(
        confidence_level=result["confidence_level"],
        engine=result["engine"],
    ).inc()
    PREDICTION_LATENCY.observe(result["latency_ms"])
    return result


@router.post("/single", response_model=SinglePredictResponse)
async def predict_single(
    req: SinglePredictRequest,
    db: AsyncSession = Depends(get_db),
) -> SinglePredictResponse:
    result = await _run_prediction(req)
    prediction_id = f"pred-{uuid.uuid4().hex[:12]}"
    db.add(_database_record(prediction_id, req, result))
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return _response(prediction_id, req, result)


@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(
    req: BatchPredictRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchPredictResponse:
    responses: list[SinglePredictResponse] = []
    for item in req.items:
        result = await _run_prediction(item)
        prediction_id = f"pred-{uuid.uuid4().hex[:12]}"
        db.add(_database_record(prediction_id, item, result))
        responses.append(_response(prediction_id, item, result))

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return BatchPredictResponse(
        total_processed=len(responses),
        successful=len(responses),
        predictions=responses,
    )
