from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==================== Auth & Users ====================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=100)
    organization_name: str | None = Field(default="Acme Engineering", max_length=100)
    role: str = Field(default="DEVELOPER")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


# ==================== Organizations, Projects & Teams ====================
class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    key: str = Field(min_length=2, max_length=10)
    description: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    key: str
    description: str | None = None
    created_at: datetime


class TeamCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    description: str
    category: str = "Core Engineering"


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    code: str
    name: str
    description: str
    category: str
    created_at: datetime


# ==================== Issues ====================
class IssueCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=5, max_length=20_000)
    project_id: str
    severity: str = "P2 - Major"
    priority: str = "MEDIUM"
    steps_to_reproduce: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    environment: str | None = None
    build_version: str | None = None
    browser_os: str | None = None
    technical_logs: str | None = None
    team_id: str | None = None
    assignee_id: str | None = None


class IssueUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = (
        None  # NEW, TRIAGE, IN_PROGRESS, FIXED, VERIFICATION, CLOSED, REOPENED
    )
    severity: str | None = None
    priority: str | None = None
    steps_to_reproduce: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    environment: str | None = None
    build_version: str | None = None
    browser_os: str | None = None
    technical_logs: str | None = None
    team_id: str | None = None
    assignee_id: str | None = None
    triage_status: str | None = None


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    author: UserOut
    content: str
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str | None = None
    actor: UserOut | None = None
    action: str
    entity_type: str
    entity_id: str
    details: Any | None = None
    created_at: datetime


class DuplicateSuggestion(BaseModel):
    issue_id: str
    issue_key: str
    title: str
    status: str
    similarity_score: float
    explanation: str


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    project_id: str
    issue_key: str
    title: str
    description: str
    steps_to_reproduce: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    environment: str | None = None
    build_version: str | None = None
    browser_os: str | None = None
    technical_logs: str | None = None
    status: str
    severity: str
    priority: str
    reporter: UserOut
    assignee: UserOut | None = None
    team: TeamOut | None = None
    recommended_team: TeamOut | None = None
    triage_status: str
    created_at: datetime
    updated_at: datetime
    comments: list[CommentOut] = Field(default_factory=list)


class PaginatedIssuesResponse(BaseModel):
    items: list[IssueOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Triage & ML ====================
class SinglePredictRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=3,
        max_length=20_000,
        json_schema_extra={
            "example": "User login failed with HTTP 500 when submitting an OAuth token"
        },
    )
    subject: str | None = Field(
        None,
        max_length=255,
        json_schema_extra={"example": "Auth service OAuth failure"},
    )
    project_id: str | None = None


class AlternativePrediction(BaseModel):
    team: str
    confidence: float
    uncertainty: float


class KeywordInfluence(BaseModel):
    word: str
    score: float


class StacktraceAnalysis(BaseModel):
    has_trace: bool = False
    detected_exception: str | None = None
    source_file: str | None = None
    line_number: int | None = None


class SinglePredictResponse(BaseModel):
    id: str
    bug_description: str
    subject: str | None = None
    predicted_team: str
    confidence_score: float
    uncertainty_score: float
    confidence_level: str
    status: str
    severity: str
    sla_hours: int
    sla_deadline: str
    impact_summary: str
    top_alternatives: list[AlternativePrediction] = Field(default_factory=list)
    top_keywords: list[KeywordInfluence] = Field(default_factory=list)
    potential_duplicates: list[DuplicateSuggestion] = Field(default_factory=list)
    stacktrace_analysis: StacktraceAnalysis
    matched_rule: str | None = None
    latency_ms: float
    created_at: str
    model_version: str
    engine: str


class ReviewQueueItem(BaseModel):
    id: str
    issue_id: str | None = None
    issue_key: str | None = None
    title: str | None = None
    bug_description: str
    subject: str | None = None
    predicted_team: str
    confidence_score: float
    uncertainty_score: float
    confidence_level: str
    severity: str
    top_alternatives: list[AlternativePrediction] = Field(default_factory=list)
    top_keywords: list[KeywordInfluence] = Field(default_factory=list)
    created_at: str


class TriageApprovalRequest(BaseModel):
    prediction_id: str
    issue_id: str | None = None


class TriageApprovalResponse(BaseModel):
    success: bool
    prediction_id: str
    confirmed_team: str
    message: str


class CorrectionRequest(BaseModel):
    prediction_id: str
    corrected_team: str
    issue_id: str | None = None
    reason: str | None = "Engineering lead reassignment"


class CorrectionResponse(BaseModel):
    success: bool
    prediction_id: str
    original_team: str
    corrected_team: str
    message: str


# ==================== Analytics ====================
class AnalyticsSummary(BaseModel):
    total_issues: int
    open_issues: int
    resolved_issues: int
    triage_pending_count: int
    avg_confidence: float
    human_override_rate: float
    severity_breakdown: dict[str, int]
    status_breakdown: dict[str, int]
    team_workload: dict[str, int]
    daily_volume_trend: list[dict[str, Any]]


# ==================== Settings & Integrations ====================
class OrganizationSettingsOut(BaseModel):
    organization_id: str
    organization_name: str
    confidence_high_threshold: float
    confidence_low_threshold: float
    auto_assign_enabled: bool
    duplicate_detection_threshold: float


class OrganizationSettingsUpdate(BaseModel):
    organization_name: str | None = None
    confidence_high_threshold: float | None = None
    confidence_low_threshold: float | None = None
    auto_assign_enabled: bool | None = None
    duplicate_detection_threshold: float | None = None


class GitHubConfigOut(BaseModel):
    is_enabled: bool
    repo: str | None = None
    has_token: bool = False


class GitHubConfigUpdate(BaseModel):
    is_enabled: bool
    repo: str
    access_token: str | None = None


class GitHubSyncRequest(BaseModel):
    issue_id: str


class GitHubSyncResponse(BaseModel):
    success: bool
    github_issue_number: int | None = None
    github_issue_url: str | None = None
    message: str


# ==================== Model Info ====================
class ModelInfoResponse(BaseModel):
    model_version: str
    framework: str
    tf_idf_vocab_size: int
    num_teams: int
    confidence_threshold_high: float
    confidence_threshold_low: float
    last_trained_at: str
    is_active: bool
    training_dataset_provenance: str
    accuracy: float | None = None
    macro_f1: float | None = None
