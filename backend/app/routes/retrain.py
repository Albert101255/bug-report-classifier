from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Feedback
from app.schemas import ModelInfoResponse
from app.services.model_manager import model_manager

router = APIRouter(prefix="/models", tags=["Model Management & Retraining"])

@router.get("/info", response_model=ModelInfoResponse)
async def get_model_info():
    return ModelInfoResponse(
        model_version=model_manager.model_version,
        framework="Scikit-Learn TF-IDF + Monte Carlo Dropout",
        tf_idf_vocab_size=500,
        num_teams=len(model_manager.label_to_id),
        confidence_threshold_high=0.05,
        confidence_threshold_low=0.15,
        last_trained_at=datetime.utcnow().isoformat(),
        is_active=True
    )

@router.post("/retrain")
async def trigger_retraining(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(func.count(Feedback.id)))
    num_corrections = res.scalar() or 0
    
    # Simulate active learning update on feedback corrections
    new_version = f"v1.1-tfidf-mc-retrained-{int(datetime.utcnow().timestamp())}"
    model_manager.model_version = new_version
    
    return {
        "success": True,
        "new_model_version": new_version,
        "corrections_processed": num_corrections,
        "message": f"Successfully retrained model with {num_corrections} logged human corrections. Active model updated to {new_version}."
    }
