from datetime import UTC, datetime, timedelta

from app.auth.dependencies import get_user_organization
from app.database import get_db
from app.models import Feedback, Issue, Organization, Prediction, Team
from app.schemas import AnalyticsSummary
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["Operational Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    # 1. Total Issues
    total_res = await db.execute(
        select(func.count(Issue.id)).filter(Issue.organization_id == org.id)
    )
    total_issues = total_res.scalar() or 0

    # 2. Open vs Resolved
    open_res = await db.execute(
        select(func.count(Issue.id)).filter(
            Issue.organization_id == org.id,
            Issue.status.in_(["NEW", "TRIAGE", "IN_PROGRESS", "REOPENED"]),
        )
    )
    open_issues = open_res.scalar() or 0

    resolved_res = await db.execute(
        select(func.count(Issue.id)).filter(
            Issue.organization_id == org.id,
            Issue.status.in_(["FIXED", "VERIFICATION", "CLOSED"]),
        )
    )
    resolved_issues = resolved_res.scalar() or 0

    # 3. Triage pending queue count
    triage_res = await db.execute(
        select(func.count(Prediction.id)).filter(
            Prediction.organization_id == org.id,
            Prediction.status == "needs_review",
        )
    )
    triage_pending = triage_res.scalar() or 0

    # 4. Average confidence from predictions
    conf_res = await db.execute(
        select(func.avg(Prediction.confidence_score)).filter(
            Prediction.organization_id == org.id
        )
    )
    avg_conf_raw = conf_res.scalar()
    avg_confidence = round(float(avg_conf_raw), 4) if avg_conf_raw is not None else 0.0

    # 5. Human Override Rate (from feedback vs total predictions)
    pred_count_res = await db.execute(
        select(func.count(Prediction.id)).filter(Prediction.organization_id == org.id)
    )
    total_preds = pred_count_res.scalar() or 0

    override_res = await db.execute(
        select(func.count(Feedback.id))
        .join(Prediction, Feedback.prediction_id == Prediction.id)
        .filter(Prediction.organization_id == org.id)
    )
    total_overrides = override_res.scalar() or 0
    override_rate = (
        round((total_overrides / total_preds) * 100, 1) if total_preds > 0 else 0.0
    )

    # 6. Severity Breakdown
    sev_res = await db.execute(
        select(Issue.severity, func.count(Issue.id))
        .filter(Issue.organization_id == org.id)
        .group_by(Issue.severity)
    )
    severity_breakdown = {row[0]: row[1] for row in sev_res.all()}

    # 7. Status Breakdown
    status_res = await db.execute(
        select(Issue.status, func.count(Issue.id))
        .filter(Issue.organization_id == org.id)
        .group_by(Issue.status)
    )
    status_breakdown = {row[0]: row[1] for row in status_res.all()}

    # 8. Team Workload
    team_res = await db.execute(
        select(Team.name, func.count(Issue.id))
        .join(Issue, Issue.team_id == Team.id)
        .filter(Issue.organization_id == org.id)
        .group_by(Team.name)
    )
    team_workload = {row[0]: row[1] for row in team_res.all()}

    # 9. Daily Volume Trend (Last 7 days)
    daily_volume_trend = []
    today = datetime.now(UTC).date()
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time(), tzinfo=UTC)
        day_end = datetime.combine(day_date, datetime.max.time(), tzinfo=UTC)

        day_count_res = await db.execute(
            select(func.count(Issue.id)).filter(
                Issue.organization_id == org.id,
                Issue.created_at >= day_start,
                Issue.created_at <= day_end,
            )
        )
        day_count = day_count_res.scalar() or 0

        day_conf_res = await db.execute(
            select(func.avg(Prediction.confidence_score)).filter(
                Prediction.organization_id == org.id,
                Prediction.created_at >= day_start,
                Prediction.created_at <= day_end,
            )
        )
        day_conf = day_conf_res.scalar()
        daily_volume_trend.append(
            {
                "day": day_date.strftime("%a %m/%d"),
                "count": day_count,
                "avg_confidence": round(float(day_conf), 2) if day_conf else 0.0,
            }
        )

    return AnalyticsSummary(
        total_issues=total_issues,
        open_issues=open_issues,
        resolved_issues=resolved_issues,
        triage_pending_count=triage_pending,
        avg_confidence=avg_confidence,
        human_override_rate=override_rate,
        severity_breakdown=severity_breakdown,
        status_breakdown=status_breakdown,
        team_workload=team_workload,
        daily_volume_trend=daily_volume_trend,
    )
