import math
import uuid
from datetime import UTC, datetime

from app.auth.dependencies import get_current_user, get_user_organization
from app.database import get_db
from app.models import (
    AuditEvent,
    Comment,
    Issue,
    Organization,
    Prediction,
    Project,
    Team,
    User,
)
from app.schemas import (
    AuditEventOut,
    CommentCreate,
    CommentOut,
    IssueCreateRequest,
    IssueOut,
    IssueUpdateRequest,
    PaginatedIssuesResponse,
)
from app.services.model_manager import model_manager
from app.services.rules_engine import evaluate_rules
from app.services.severity_engine import calculate_severity
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/issues", tags=["Issues Management"])

VALID_TRANSITIONS: dict[str, set[str]] = {
    "NEW": {"TRIAGE", "IN_PROGRESS", "CLOSED"},
    "TRIAGE": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"FIXED", "TRIAGE", "CLOSED"},
    "FIXED": {"VERIFICATION", "REOPENED", "IN_PROGRESS"},
    "VERIFICATION": {"CLOSED", "REOPENED", "IN_PROGRESS"},
    "CLOSED": {"REOPENED"},
    "REOPENED": {"TRIAGE", "IN_PROGRESS", "FIXED"},
}


@router.post("", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
async def create_issue(
    req: IssueCreateRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IssueOut:
    # Verify project
    proj_res = await db.execute(
        select(Project).filter(
            Project.id == req.project_id,
            Project.organization_id == org.id,
        )
    )
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this organization.",
        )

    # Generate next sequential issue key without collisions across the workspace
    keys_res = await db.execute(
        select(Issue.issue_key).filter(Issue.issue_key.like(f"{project.key}-%"))
    )
    existing_keys = keys_res.scalars().all()
    max_num = 0
    for k in existing_keys:
        try:
            num = int(k.split("-")[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass
    issue_num = max_num + 1
    issue_key = f"{project.key}-{issue_num}"

    # Calculate severity & parse stacktrace
    severity_info = calculate_severity(req.description, req.title)
    assigned_severity = (
        req.severity if req.severity != "P2 - Major" else severity_info["severity"]
    )

    # Rule Engine check
    rule_match = evaluate_rules(req.description, req.title)
    if rule_match:
        pred_team_name = rule_match["target_team"]
        assigned_severity = rule_match["forced_severity"]
        pred_result = {
            "predicted_team": pred_team_name,
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
    else:
        try:
            pred_result = model_manager.predict(req.description, req.title)
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

    # Match team in org
    teams_res = await db.execute(select(Team).filter(Team.organization_id == org.id))
    all_teams = teams_res.scalars().all()
    matched_team = None
    for t in all_teams:
        if (
            t.code in pred_result["predicted_team"]
            or t.name in pred_result["predicted_team"]
        ):
            matched_team = t
            break

    # Determine initial triage state
    target_team_id = req.team_id or (
        matched_team.id
        if matched_team and pred_result["confidence_level"] == "HIGH"
        else None
    )
    initial_status = "TRIAGE" if target_team_id else "NEW"
    triage_state = (
        "APPROVED"
        if (matched_team and pred_result["confidence_level"] == "HIGH")
        else "PENDING"
    )

    issue_id = str(uuid.uuid4())
    issue = Issue(
        id=issue_id,
        organization_id=org.id,
        project_id=project.id,
        issue_key=issue_key,
        title=req.title,
        description=req.description,
        steps_to_reproduce=req.steps_to_reproduce,
        expected_behavior=req.expected_behavior,
        actual_behavior=req.actual_behavior,
        environment=req.environment,
        build_version=req.build_version,
        browser_os=req.browser_os,
        technical_logs=req.technical_logs,
        status=initial_status,
        severity=assigned_severity,
        priority=req.priority,
        reporter_id=current_user.id,
        assignee_id=req.assignee_id,
        team_id=target_team_id,
        recommended_team_id=matched_team.id if matched_team else None,
        triage_status=triage_state,
    )
    db.add(issue)

    # Store Prediction Record
    pred_record = Prediction(
        id=f"pred-{uuid.uuid4().hex[:12]}",
        organization_id=org.id,
        issue_id=issue_id,
        subject=req.title,
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

    # Audit event for issue creation
    audit = AuditEvent(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        issue_id=issue_id,
        actor_id=current_user.id,
        action="ISSUE_CREATED",
        entity_type="Issue",
        entity_id=issue_id,
        details={
            "issue_key": issue_key,
            "title": req.title,
            "predicted_team": pred_result["predicted_team"],
            "confidence": pred_result["confidence_score"],
            "engine": pred_result["engine"],
        },
    )
    db.add(audit)

    await db.commit()

    # Re-fetch with relationships
    final_res = await db.execute(
        select(Issue)
        .options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.team),
            selectinload(Issue.recommended_team),
            selectinload(Issue.comments),
        )
        .filter(Issue.id == issue_id)
    )
    created_issue = final_res.scalar_one()
    return IssueOut.model_validate(created_issue)


@router.get("", response_model=PaginatedIssuesResponse)
async def list_issues(
    project_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = None,
    priority: str | None = None,
    team_id: str | None = None,
    assignee_id: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> PaginatedIssuesResponse:
    query = select(Issue).filter(Issue.organization_id == org.id)

    if project_id:
        query = query.filter(Issue.project_id == project_id)
    if status_filter:
        query = query.filter(Issue.status == status_filter)
    if severity:
        query = query.filter(Issue.severity == severity)
    if priority:
        query = query.filter(Issue.priority == priority)
    if team_id:
        query = query.filter(Issue.team_id == team_id)
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Issue.title.ilike(search_pattern),
                Issue.issue_key.ilike(search_pattern),
                Issue.description.ilike(search_pattern),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = (
        query.options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.team),
            selectinload(Issue.recommended_team),
            selectinload(Issue.comments).selectinload(Comment.author),
        )
        .order_by(Issue.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    items_res = await db.execute(query)
    issues = items_res.scalars().all()
    total_pages = max(1, math.ceil(total / page_size))

    return PaginatedIssuesResponse(
        items=[IssueOut.model_validate(iss) for iss in issues],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{issue_id}", response_model=IssueOut)
async def get_issue_detail(
    issue_id: str,
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> IssueOut:
    res = await db.execute(
        select(Issue)
        .options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.team),
            selectinload(Issue.recommended_team),
            selectinload(Issue.comments).selectinload(Comment.author),
        )
        .filter(Issue.id == issue_id, Issue.organization_id == org.id)
    )
    issue = res.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")
    return IssueOut.model_validate(issue)


@router.patch("/{issue_id}", response_model=IssueOut)
async def update_issue(
    issue_id: str,
    req: IssueUpdateRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IssueOut:
    res = await db.execute(
        select(Issue)
        .options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.team),
            selectinload(Issue.recommended_team),
            selectinload(Issue.comments).selectinload(Comment.author),
        )
        .filter(Issue.id == issue_id, Issue.organization_id == org.id)
    )
    issue = res.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    changes = {}

    # Status transition check
    if req.status and req.status != issue.status:
        allowed = VALID_TRANSITIONS.get(issue.status, set())
        if req.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{issue.status}' to '{req.status}'. Allowed: {sorted(allowed)}",
            )
        changes["status"] = {"from": issue.status, "to": req.status}
        issue.status = req.status

    if req.team_id is not None and req.team_id != issue.team_id:
        changes["team_id"] = {"from": issue.team_id, "to": req.team_id}
        issue.team_id = req.team_id
        issue.triage_status = "APPROVED"

    if req.assignee_id is not None and req.assignee_id != issue.assignee_id:
        changes["assignee_id"] = {"from": issue.assignee_id, "to": req.assignee_id}
        issue.assignee_id = req.assignee_id

    if req.severity and req.severity != issue.severity:
        changes["severity"] = {"from": issue.severity, "to": req.severity}
        issue.severity = req.severity

    if req.priority and req.priority != issue.priority:
        changes["priority"] = {"from": issue.priority, "to": req.priority}
        issue.priority = req.priority

    if req.title:
        issue.title = req.title
    if req.description:
        issue.description = req.description
    if req.steps_to_reproduce is not None:
        issue.steps_to_reproduce = req.steps_to_reproduce
    if req.expected_behavior is not None:
        issue.expected_behavior = req.expected_behavior
    if req.actual_behavior is not None:
        issue.actual_behavior = req.actual_behavior
    if req.environment is not None:
        issue.environment = req.environment
    if req.technical_logs is not None:
        issue.technical_logs = req.technical_logs
    if req.triage_status:
        issue.triage_status = req.triage_status

    issue.updated_at = datetime.now(UTC)

    if changes:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            issue_id=issue.id,
            actor_id=current_user.id,
            action="ISSUE_UPDATED",
            entity_type="Issue",
            entity_id=issue.id,
            details=changes,
        )
        db.add(audit)

    await db.commit()
    await db.refresh(issue)
    return IssueOut.model_validate(issue)


@router.post("/{issue_id}/comments", response_model=CommentOut)
async def add_comment(
    issue_id: str,
    req: CommentCreate,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentOut:
    res = await db.execute(
        select(Issue).filter(Issue.id == issue_id, Issue.organization_id == org.id)
    )
    issue = res.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    comment = Comment(
        id=str(uuid.uuid4()),
        issue_id=issue.id,
        author_id=current_user.id,
        content=req.content,
    )
    db.add(comment)

    audit = AuditEvent(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        issue_id=issue.id,
        actor_id=current_user.id,
        action="COMMENT_ADDED",
        entity_type="Comment",
        entity_id=comment.id,
        details={"preview": req.content[:100]},
    )
    db.add(audit)

    await db.commit()

    # Re-fetch comment with author
    c_res = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .filter(Comment.id == comment.id)
    )
    full_comment = c_res.scalar_one()
    return CommentOut.model_validate(full_comment)


@router.get("/{issue_id}/audit-trail", response_model=list[AuditEventOut])
async def get_issue_audit_trail(
    issue_id: str,
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> list[AuditEventOut]:
    res = await db.execute(
        select(AuditEvent)
        .options(selectinload(AuditEvent.actor))
        .filter(AuditEvent.issue_id == issue_id, AuditEvent.organization_id == org.id)
        .order_by(AuditEvent.created_at.desc())
    )
    events = res.scalars().all()
    return [AuditEventOut.model_validate(e) for e in events]
