import uuid
from datetime import UTC, datetime

from app.auth.dependencies import get_current_user, get_user_organization
from app.database import get_db
from app.models import AuditEvent, Feedback, Issue, Organization, Prediction, Team, User
from app.schemas import (
    CorrectionRequest,
    CorrectionResponse,
    DuplicateSuggestion,
    ReviewQueueItem,
    SinglePredictRequest,
    SinglePredictResponse,
    StacktraceAnalysis,
    TriageApprovalRequest,
    TriageApprovalResponse,
)
from app.services.dedup_engine import find_duplicates
from app.services.model_manager import model_manager
from app.services.rules_engine import evaluate_rules
from app.services.severity_engine import calculate_severity
from app.services.stacktrace_parser import parse_stacktrace
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/triage", tags=["Intelligent Triage & Review"])


@router.post("/predict", response_model=SinglePredictResponse)
async def predict_single_issue(
    req: SinglePredictRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SinglePredictResponse:
    # 1. Deterministic Rule Matching
    rule_match = evaluate_rules(req.description, req.subject or "")
    if rule_match:
        pred_result = {
            "predicted_team": rule_match["target_team"],
            "confidence_score": 0.99,
            "uncertainty_score": 0.01,
            "confidence_level": "HIGH",
            "status": "auto_assigned",
            "top_alternatives": [],
            "top_keywords": [{"word": "policy_rule", "score": 1.0}],
            "latency_ms": 0.15,
            "model_version": "policy-rule-engine",
            "engine": "rule_policy",
        }
        matched_rule = rule_match["rule_name"]
    else:
        try:
            pred_result = model_manager.predict(req.description, req.subject or "")
        except Exception:
            pred_result = {
                "predicted_team": "BL-106 (API Gateway & Microservices)",
                "confidence_score": 0.50,
                "uncertainty_score": 0.50,
                "confidence_level": "LOW",
                "status": "needs_review",
                "top_alternatives": [],
                "top_keywords": [],
                "latency_ms": 0.0,
                "model_version": "rules-fallback",
                "engine": "rules-fallback",
            }
        matched_rule = None

    # 2. Heuristic Severity & SLA
    severity_info = calculate_severity(req.description, req.subject or "")
    if rule_match and "forced_severity" in rule_match:
        severity_info["severity"] = rule_match["forced_severity"]

    # 3. Stack Trace Analysis
    trace_info = parse_stacktrace(req.description)

    # 4. Duplicate Detection (scoped to org)
    duplicates_raw = await find_duplicates(
        description=req.description,
        subject=req.subject or "",
        organization_id=org.id,
        project_id=req.project_id,
        db=db,
    )
    duplicates = [DuplicateSuggestion(**d) for d in duplicates_raw]

    # 5. Persist Prediction record
    prediction_id = f"pred-{uuid.uuid4().hex[:12]}"
    pred_record = Prediction(
        id=prediction_id,
        organization_id=org.id,
        issue_id=None,
        subject=req.subject,
        bug_description=req.description,
        predicted_team=pred_result["predicted_team"],
        confidence_score=pred_result["confidence_score"],
        uncertainty_score=pred_result["uncertainty_score"],
        confidence_level=pred_result["confidence_level"],
        status=pred_result["status"],
        top_alternatives=pred_result["top_alternatives"],
        top_keywords=pred_result["top_keywords"],
        model_version=pred_result["model_version"],
        engine=pred_result["engine"],
        latency_ms=pred_result["latency_ms"],
    )
    db.add(pred_record)
    await db.commit()

    return SinglePredictResponse(
        id=prediction_id,
        bug_description=req.description,
        subject=req.subject,
        predicted_team=pred_result["predicted_team"],
        confidence_score=pred_result["confidence_score"],
        uncertainty_score=pred_result["uncertainty_score"],
        confidence_level=pred_result["confidence_level"],
        status=pred_result["status"],
        severity=severity_info["severity"],
        sla_hours=severity_info["sla_hours"],
        sla_deadline=severity_info["sla_deadline"],
        impact_summary=severity_info["impact_summary"],
        top_alternatives=pred_result["top_alternatives"],
        top_keywords=pred_result["top_keywords"],
        potential_duplicates=duplicates,
        stacktrace_analysis=StacktraceAnalysis(**trace_info),
        matched_rule=matched_rule,
        latency_ms=pred_result["latency_ms"],
        created_at=datetime.now(UTC).isoformat(),
        model_version=pred_result["model_version"],
        engine=pred_result["engine"],
    )


@router.get("/review-queue", response_model=list[ReviewQueueItem])
async def get_review_queue(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> list[ReviewQueueItem]:
    # Query predictions needing human review
    query = (
        select(Prediction, Issue)
        .outerjoin(Issue, Prediction.issue_id == Issue.id)
        .filter(
            Prediction.organization_id == org.id,
            Prediction.status == "needs_review",
        )
        .order_by(Prediction.created_at.desc())
        .limit(100)
    )
    res = await db.execute(query)
    rows = res.all()

    items = []
    for pred, issue in rows:
        severity_info = calculate_severity(pred.bug_description, pred.subject or "")
        items.append(
            ReviewQueueItem(
                id=pred.id,
                issue_id=issue.id if issue else None,
                issue_key=issue.issue_key if issue else None,
                title=issue.title if issue else pred.subject,
                bug_description=pred.bug_description,
                subject=pred.subject,
                predicted_team=pred.predicted_team,
                confidence_score=pred.confidence_score,
                uncertainty_score=pred.uncertainty_score,
                confidence_level=pred.confidence_level,
                severity=issue.severity if issue else severity_info["severity"],
                top_alternatives=pred.top_alternatives or [],
                top_keywords=pred.top_keywords or [],
                created_at=pred.created_at.isoformat(),
            )
        )
    return items


@router.post("/approve", response_model=TriageApprovalResponse)
async def approve_prediction(
    req: TriageApprovalRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TriageApprovalResponse:
    res = await db.execute(
        select(Prediction).filter(
            Prediction.id == req.prediction_id,
            Prediction.organization_id == org.id,
        )
    )
    pred = res.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction record not found.")

    pred.status = "human_approved"

    # If linked to an issue, confirm team assignment
    if pred.issue_id or req.issue_id:
        issue_id = pred.issue_id or req.issue_id
        iss_res = await db.execute(select(Issue).filter(Issue.id == issue_id))
        issue = iss_res.scalar_one_or_none()
        if issue:
            # Find team in org
            teams_res = await db.execute(
                select(Team).filter(Team.organization_id == org.id)
            )
            for t in teams_res.scalars().all():
                if t.code in pred.predicted_team or t.name in pred.predicted_team:
                    issue.team_id = t.id
                    break
            issue.triage_status = "APPROVED"
            if issue.status == "NEW":
                issue.status = "TRIAGE"

            audit = AuditEvent(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                issue_id=issue.id,
                actor_id=current_user.id,
                action="TRIAGE_APPROVED",
                entity_type="Issue",
                entity_id=issue.id,
                details={
                    "prediction_id": pred.id,
                    "confirmed_team": pred.predicted_team,
                    "reviewer": current_user.email,
                },
            )
            db.add(audit)

    await db.commit()
    return TriageApprovalResponse(
        success=True,
        prediction_id=pred.id,
        confirmed_team=pred.predicted_team,
        message=f"Routing confirmed for team '{pred.predicted_team}'.",
    )


@router.post("/override", response_model=CorrectionResponse)
async def override_prediction(
    req: CorrectionRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CorrectionResponse:
    res = await db.execute(
        select(Prediction).filter(
            Prediction.id == req.prediction_id,
            Prediction.organization_id == org.id,
        )
    )
    pred = res.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction record not found.")

    original_team = pred.predicted_team
    pred.predicted_team = req.corrected_team
    pred.status = "human_corrected"

    # Create immutable Feedback record for audit and future retraining dataset
    feedback = Feedback(
        id=f"fb-{uuid.uuid4().hex[:12]}",
        prediction_id=pred.id,
        issue_id=pred.issue_id or req.issue_id,
        original_team=original_team,
        corrected_team=req.corrected_team,
        reason=req.reason,
        reviewer_user_id=current_user.id,
    )
    db.add(feedback)

    # If linked to an issue, update team
    issue_id = pred.issue_id or req.issue_id
    if issue_id:
        iss_res = await db.execute(select(Issue).filter(Issue.id == issue_id))
        issue = iss_res.scalar_one_or_none()
        if issue:
            teams_res = await db.execute(
                select(Team).filter(Team.organization_id == org.id)
            )
            for t in teams_res.scalars().all():
                if t.code in req.corrected_team or t.name in req.corrected_team:
                    issue.team_id = t.id
                    break
            issue.triage_status = "OVERRIDDEN"
            if issue.status == "NEW":
                issue.status = "TRIAGE"

            audit = AuditEvent(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                issue_id=issue.id,
                actor_id=current_user.id,
                action="TRIAGE_OVERRIDDEN",
                entity_type="Issue",
                entity_id=issue.id,
                details={
                    "original_team": original_team,
                    "corrected_team": req.corrected_team,
                    "reason": req.reason,
                    "reviewer": current_user.email,
                },
            )
            db.add(audit)

    await db.commit()
    return CorrectionResponse(
        success=True,
        prediction_id=pred.id,
        original_team=original_team,
        corrected_team=req.corrected_team,
        message=f"Team routing updated from '{original_team}' to '{req.corrected_team}' and logged for audit.",
    )
