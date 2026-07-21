import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Prediction, Feedback
from app.schemas import ReviewQueueItem, CorrectionRequest, CorrectionResponse

router = APIRouter(prefix="", tags=["Review Queue & Feedback"])

@router.get("/predict/review-queue", response_model=List[ReviewQueueItem])
async def get_review_queue(db: AsyncSession = Depends(get_db)):
    query = select(Prediction).filter(Prediction.status == "needs_review").order_by(Prediction.created_at.desc())
    res = await db.execute(query)
    rows = res.scalars().all()
    
    items = []
    for r in rows:
        items.append(ReviewQueueItem(
            id=r.id,
            bug_description=r.bug_description,
            subject=r.subject,
            predicted_team=r.predicted_team,
            confidence_score=r.confidence_score,
            uncertainty_score=r.uncertainty_score,
            confidence_level=r.confidence_level,
            top_alternatives=r.top_alternatives or [],
            created_at=r.created_at.isoformat()
        ))
    return items

@router.post("/feedback/correct", response_model=CorrectionResponse)
async def correct_prediction(req: CorrectionRequest, db: AsyncSession = Depends(get_db)):
    query = select(Prediction).filter(Prediction.id == req.prediction_id)
    res = await db.execute(query)
    pred = res.scalar_one_or_none()
    
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    orig_team = pred.predicted_team
    pred.predicted_team = req.corrected_team
    pred.status = "human_corrected"
    
    fb = Feedback(
        id=f"fb-{uuid.uuid4().hex[:12]}",
        prediction_id=req.prediction_id,
        original_team=orig_team,
        corrected_team=req.corrected_team,
        reason=req.reason,
        reviewer_user_id=req.reviewer_user_id or "reviewer_1"
    )
    
    db.add(fb)
    await db.commit()
    
    return CorrectionResponse(
        success=True,
        prediction_id=req.prediction_id,
        original_team=orig_team,
        corrected_team=req.corrected_team,
        message=f"Prediction updated to '{req.corrected_team}' and logged for retraining audit trail."
    )
