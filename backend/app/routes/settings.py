import uuid
from datetime import UTC, datetime

from app.auth.dependencies import get_user_organization, require_role
from app.database import get_db
from app.models import Organization, Setting, User
from app.schemas import (
    OrganizationSettingsOut,
    OrganizationSettingsUpdate,
)
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/settings", tags=["Settings & Configuration"])


@router.get("/organization", response_model=OrganizationSettingsOut)
async def get_org_settings(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> OrganizationSettingsOut:
    res = await db.execute(
        select(Setting).filter(
            Setting.organization_id == org.id,
            Setting.key == "triage_policy",
        )
    )
    setting = res.scalar_one_or_none()

    policy = (
        setting.value
        if setting
        else {
            "confidence_high_threshold": 0.25,
            "confidence_low_threshold": 0.50,
            "auto_assign_enabled": True,
            "duplicate_detection_threshold": 0.22,
        }
    )

    return OrganizationSettingsOut(
        organization_id=org.id,
        organization_name=org.name,
        confidence_high_threshold=policy.get("confidence_high_threshold", 0.25),
        confidence_low_threshold=policy.get("confidence_low_threshold", 0.50),
        auto_assign_enabled=policy.get("auto_assign_enabled", True),
        duplicate_detection_threshold=policy.get("duplicate_detection_threshold", 0.22),
    )


@router.patch("/organization", response_model=OrganizationSettingsOut)
async def update_org_settings(
    req: OrganizationSettingsUpdate,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(require_role(["ORG_ADMIN"])),
    db: AsyncSession = Depends(get_db),
) -> OrganizationSettingsOut:
    if req.organization_name:
        org.name = req.organization_name

    res = await db.execute(
        select(Setting).filter(
            Setting.organization_id == org.id,
            Setting.key == "triage_policy",
        )
    )
    setting = res.scalar_one_or_none()
    current_val = setting.value if setting else {}

    if req.confidence_high_threshold is not None:
        current_val["confidence_high_threshold"] = req.confidence_high_threshold
    if req.confidence_low_threshold is not None:
        current_val["confidence_low_threshold"] = req.confidence_low_threshold
    if req.auto_assign_enabled is not None:
        current_val["auto_assign_enabled"] = req.auto_assign_enabled
    if req.duplicate_detection_threshold is not None:
        current_val["duplicate_detection_threshold"] = req.duplicate_detection_threshold

    if setting:
        setting.value = current_val
        setting.updated_at = datetime.now(UTC)
    else:
        setting = Setting(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            key="triage_policy",
            value=current_val,
        )
        db.add(setting)

    await db.commit()
    await db.refresh(org)

    return OrganizationSettingsOut(
        organization_id=org.id,
        organization_name=org.name,
        confidence_high_threshold=current_val.get("confidence_high_threshold", 0.25),
        confidence_low_threshold=current_val.get("confidence_low_threshold", 0.50),
        auto_assign_enabled=current_val.get("auto_assign_enabled", True),
        duplicate_detection_threshold=current_val.get(
            "duplicate_detection_threshold", 0.22
        ),
    )
