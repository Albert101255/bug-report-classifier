from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Prediction
from app.schemas import SinglePredictResponse

router = APIRouter(prefix="/predict", tags=["History"])

@router.get("/history", response_model=List[SinglePredictResponse])
async def get_prediction_history(
    limit: int = Query(50, ge=1, le=500),
    team: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Prediction).order_by(Prediction.created_at.desc()).limit(limit)
    
    if team:
        query = query.filter(Prediction.predicted_team == team)
    if level:
        query = query.filter(Prediction.confidence_level == level.upper())
    if search:
        query = query.filter(Prediction.bug_description.ilike(f"%{search}%"))
        
    res = await db.execute(query)
    rows = res.scalars().all()
    
    output = []
    for r in rows:
        output.append(SinglePredictResponse(
            id=r.id,
            bug_description=r.bug_description,
            subject=r.subject,
            predicted_team=r.predicted_team,
            confidence_score=r.confidence_score,
            uncertainty_score=r.uncertainty_score,
            confidence_level=r.confidence_level,
            status=r.status,
            top_alternatives=r.top_alternatives or [],
            top_keywords=r.top_keywords or [],
            latency_ms=r.latency_ms,
            created_at=r.created_at.isoformat()
        ))
        
    return output
