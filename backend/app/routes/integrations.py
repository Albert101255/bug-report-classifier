import uuid
from datetime import UTC, datetime

from app.auth.dependencies import get_current_user, get_user_organization, require_role
from app.database import get_db
from app.models import AuditEvent, IntegrationConfig, Issue, Organization, User
from app.schemas import (
    GitHubConfigOut,
    GitHubConfigUpdate,
    GitHubSyncRequest,
    GitHubSyncResponse,
)
from app.services.github_service import GitHubService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/github", response_model=GitHubConfigOut)
async def get_github_integration(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> GitHubConfigOut:
    res = await db.execute(
        select(IntegrationConfig).filter(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.provider == "github",
        )
    )
    cfg = res.scalar_one_or_none()

    if not cfg:
        return GitHubConfigOut(
            is_enabled=False,
            repo=None,
            has_token=False,
        )

    return GitHubConfigOut(
        is_enabled=cfg.is_enabled,
        repo=cfg.repo_or_project,
        has_token=bool(cfg.access_token),
    )


@router.patch("/github", response_model=GitHubConfigOut)
async def configure_github_integration(
    req: GitHubConfigUpdate,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(require_role(["ORG_ADMIN"])),
    db: AsyncSession = Depends(get_db),
) -> GitHubConfigOut:
    res = await db.execute(
        select(IntegrationConfig).filter(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.provider == "github",
        )
    )
    cfg = res.scalar_one_or_none()

    if not cfg:
        cfg = IntegrationConfig(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            provider="github",
            is_enabled=req.is_enabled,
            repo_or_project=req.repo,
            access_token=req.access_token,
        )
        db.add(cfg)
    else:
        cfg.is_enabled = req.is_enabled
        cfg.repo_or_project = req.repo
        if req.access_token is not None:
            cfg.access_token = req.access_token
        cfg.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(cfg)

    return GitHubConfigOut(
        is_enabled=cfg.is_enabled,
        repo=cfg.repo_or_project,
        has_token=bool(cfg.access_token),
    )


@router.post("/github/sync", response_model=GitHubSyncResponse)
async def sync_issue_to_github(
    req: GitHubSyncRequest,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GitHubSyncResponse:
    # 1. Fetch issue
    iss_res = await db.execute(
        select(Issue).filter(
            Issue.id == req.issue_id,
            Issue.organization_id == org.id,
        )
    )
    issue = iss_res.scalar_one_or_none()
    if not issue:
        raise HTTPException(
            status_code=404, detail="Issue not found in this organization."
        )

    # 2. Fetch GitHub config
    cfg_res = await db.execute(
        select(IntegrationConfig).filter(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.provider == "github",
        )
    )
    cfg = cfg_res.scalar_one_or_none()

    if not cfg or not cfg.is_enabled:
        return GitHubSyncResponse(
            success=False,
            github_issue_number=None,
            github_issue_url=None,
            message="GitHub integration is not enabled for this organization. Configure in Settings.",
        )

    # 3. Call real GitHub Service
    body = (
        f"**Triage Issue:** {issue.issue_key}\n"
        f"**Severity:** {issue.severity} | **Priority:** {issue.priority}\n\n"
        f"### Description\n{issue.description}\n\n"
        f"**Steps to Reproduce:**\n{issue.steps_to_reproduce or 'N/A'}\n\n"
        f"**Technical Logs:**\n```\n{issue.technical_logs or 'None'}\n```\n"
    )

    result = await GitHubService.create_github_issue(
        title=f"[{issue.issue_key}] {issue.title}",
        body=body,
        custom_token=cfg.access_token,
        custom_repo=cfg.repo_or_project,
    )

    if result["success"]:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            issue_id=issue.id,
            actor_id=current_user.id,
            action="GITHUB_SYNCED",
            entity_type="Issue",
            entity_id=issue.id,
            details={
                "github_issue_number": result["github_issue_number"],
                "github_issue_url": result["github_issue_url"],
            },
        )
        db.add(audit)
        await db.commit()

    return GitHubSyncResponse(
        success=result["success"],
        github_issue_number=result.get("github_issue_number"),
        github_issue_url=result.get("github_issue_url"),
        message=result["message"],
    )
