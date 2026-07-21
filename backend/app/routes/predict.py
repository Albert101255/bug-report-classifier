import uuid
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import SinglePredictRequest, SinglePredictResponse, BatchPredictRequest, BatchPredictResponse
from app.services.model_manager import model_manager
from app.models import Prediction

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/single", response_model=SinglePredictResponse)
async def predict_single(req: SinglePredictRequest, db: AsyncSession = Depends(get_db)):
    if not req.description.trim() if hasattr(req.description, 'trim') else not req.description.strip():
        raise HTTPException(status_code=400, detail="Bug description cannot be empty")
        
    start_time = time.time()
    res = model_manager.predict(req.description, req.subject or "")
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    pred_id = f"pred-{uuid.uuid4().hex[:12]}"
    now_iso = datetime.utcnow().isoformat()
    
    # Save Prediction Audit Trail to Database
    db_pred = Prediction(
        id=pred_id,
        bug_description=req.description,
        subject=req.subject,
        predicted_team=res["predicted_team"],
        confidence_score=res["confidence_score"],
        uncertainty_score=res["uncertainty_score"],
        confidence_level=res["confidence_level"],
        status=res["status"],
        top_alternatives=res["top_alternatives"],
        top_keywords=res["top_keywords"],
        latency_ms=latency_ms,
        user_id=req.user_id or "anonymous"
    )
    
    db.add(db_pred)
    await db.commit()
    
    return SinglePredictResponse(
        id=pred_id,
        bug_description=req.description,
        subject=req.subject,
        predicted_team=res["predicted_team"],
        confidence_score=res["confidence_score"],
        uncertainty_score=res["uncertainty_score"],
        confidence_level=res["confidence_level"],
        status=res["status"],
        top_alternatives=res["top_alternatives"],
        top_keywords=res["top_keywords"],
        latency_ms=latency_ms,
        created_at=now_iso
    )

@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(req: BatchPredictRequest, db: AsyncSession = Depends(get_db)):
    predictions = []
    for item in req.items:
        res = model_manager.predict(item.description, item.subject or "")
        pred_id = f"pred-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.utcnow().isoformat()
        
        db_pred = Prediction(
            id=pred_id,
            bug_description=item.description,
            subject=item.subject,
            predicted_team=res["predicted_team"],
            confidence_score=res["confidence_score"],
            uncertainty_score=res["uncertainty_score"],
            confidence_level=res["confidence_level"],
            status=res["status"],
            top_alternatives=res["top_alternatives"],
            top_keywords=res["top_keywords"],
            latency_ms=res["latency_ms"],
            user_id=item.user_id or "batch_user"
        )
        db.add(db_pred)
        
        predictions.append(SinglePredictResponse(
            id=pred_id,
            bug_description=item.description,
            subject=item.subject,
            predicted_team=res["predicted_team"],
            confidence_score=res["confidence_score"],
            uncertainty_score=res["uncertainty_score"],
            confidence_level=res["confidence_level"],
            status=res["status"],
            top_alternatives=res["top_alternatives"],
            top_keywords=res["top_keywords"],
            latency_ms=res["latency_ms"],
            created_at=now_iso
        ))
        
    await db.commit()
    
    return BatchPredictResponse(
        total_processed=len(predictions),
        successful=len(predictions),
        predictions=predictions
    )
