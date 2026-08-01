from typing import Any

from pydantic import BaseModel, Field


class SinglePredictRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=3,
        max_length=10_000,
        json_schema_extra={
            "example": "User login failed with HTTP 500 when submitting an OAuth token"
        },
    )
    subject: str | None = Field(
        None,
        max_length=255,
        json_schema_extra={"example": "Auth service OAuth failure"},
    )
    user_id: str | None = Field(default="user_1", max_length=50)


class AlternativePrediction(BaseModel):
    team: str
    confidence: float
    uncertainty: float


class KeywordInfluence(BaseModel):
    word: str
    score: float


class SinglePredictResponse(BaseModel):
    id: str
    bug_description: str
    subject: str | None = None
    predicted_team: str
    confidence_score: float
    uncertainty_score: float
    confidence_level: str
    status: str
    top_alternatives: list[AlternativePrediction] = Field(default_factory=list)
    top_keywords: list[KeywordInfluence] = Field(default_factory=list)
    latency_ms: float
    created_at: str


class BatchPredictRequest(BaseModel):
    items: list[SinglePredictRequest] = Field(min_length=1, max_length=100)


class BatchPredictResponse(BaseModel):
    total_processed: int
    successful: int
    predictions: list[SinglePredictResponse]


class CorrectionRequest(BaseModel):
    prediction_id: str
    corrected_team: str
    reason: str | None = "Human reviewer override"
    reviewer_user_id: str | None = "reviewer_1"


class CorrectionResponse(BaseModel):
    success: bool
    prediction_id: str
    original_team: str
    corrected_team: str
    message: str


class ReviewQueueItem(BaseModel):
    id: str
    bug_description: str
    subject: str | None = None
    predicted_team: str
    confidence_score: float
    uncertainty_score: float
    confidence_level: str
    top_alternatives: list[AlternativePrediction] = Field(default_factory=list)
    created_at: str


class TeamInfo(BaseModel):
    code: str
    name: str
    description: str
    category: str
    accuracy_rate: float
    total_bugs_assigned: int


class AnalyticsSummary(BaseModel):
    total_predictions: int
    avg_confidence: float
    avg_uncertainty: float
    auto_assigned_pct: float
    needs_review_pct: float
    corrected_pct: float
    team_accuracy_breakdown: dict[str, float]
    daily_prediction_trend: list[dict[str, Any]]


class ModelInfoResponse(BaseModel):
    model_version: str
    framework: str
    tf_idf_vocab_size: int
    num_teams: int
    confidence_threshold_high: float
    confidence_threshold_low: float
    last_trained_at: str
    is_active: bool
