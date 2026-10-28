import re
import uuid

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models import Organization, OrganizationMember, Project, Team, User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication & Accounts"])

DEFAULT_TEAMS = [
    (
        "BL-101",
        "Authentication & AuthZ",
        "OAuth2, JWT tokens, SSO, login flows, and permissions",
        "Security & Identity",
    ),
    (
        "BL-102",
        "Database & ORM",
        "PostgreSQL clusters, SQLAlchemy, connection pooling, and migrations",
        "Core Infrastructure",
    ),
    (
        "BL-103",
        "UI Components & Design System",
        "React components, CSS layout, accessibility, and responsive views",
        "Frontend Engineering",
    ),
    (
        "BL-104",
        "Payment Gateway & Billing",
        "Stripe processing, subscriptions, invoicing, and refunds",
        "Business Systems",
    ),
    (
        "BL-105",
        "Cloud Infrastructure & K8s",
        "Kubernetes pods, container runtime, OOM failures, and caching",
        "Platform Engineering",
    ),
    (
        "BL-106",
        "API Gateway & Microservices",
        "REST endpoints, FastAPI gateways, serialization, and webhooks",
        "Backend Services",
    ),
    (
        "BL-107",
        "Search & Indexing Engine",
        "Elasticsearch clusters, search ranking, and text indexing",
        "Search & Data",
    ),
    (
        "BL-108",
        "Notification & Webhooks",
        "Transactional email, SMS, push notifications, and dispatch",
        "Communications",
    ),
    (
        "BL-109",
        "Analytics & Telemetry",
        "Prometheus metrics, latency tracking, dashboards, and event logs",
        "Observability",
    ),
    (
        "BL-110",
        "Security & Compliance",
        "Vulnerability management, CVE response, TLS certs, and injection flaws",
        "Security",
    ),
]


@router.post("/register", response_model=TokenResponse)
async def register_user(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # Check if user already exists
    res = await db.execute(select(User).filter(User.email == req.email.lower()))
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Find or create organization based on organization_name
    slug = (
        re.sub(r"[^a-z0-9]+", "-", req.organization_name.lower()).strip("-")
        or "default-org"
    )
    org_res = await db.execute(
        select(Organization).filter(
            (Organization.name == req.organization_name) | (Organization.slug == slug)
        )
    )
    org = org_res.scalar_one_or_none()

    if not org:
        org = Organization(
            id=str(uuid.uuid4()),
            name=req.organization_name,
            slug=slug,
        )
        db.add(org)
        await db.flush()

        # Create default project for this org
        project = Project(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            name="Main Platform",
            key="TRIAGE",
            description="Primary software engineering project for bug tracking and intelligent triage.",
        )
        db.add(project)

        # Seed standard engineering teams for this org
        for code, name, description, category in DEFAULT_TEAMS:
            team = Team(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                code=code,
                name=f"{code} ({name})",
                description=description,
                category=category,
            )
            db.add(team)

        user_role = "ORG_ADMIN"
    else:
        user_role = req.role

    user = User(
        id=str(uuid.uuid4()),
        email=req.email.lower(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=user_role,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    member = OrganizationMember(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        user_id=user.id,
        role=user_role,
    )
    db.add(member)

    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        {"sub": user.id, "email": user.email, "role": user.role}
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    res = await db.execute(select(User).filter(User.email == req.email.lower()))
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated.",
        )

    token = create_access_token(
        {"sub": user.id, "email": user.email, "role": user.role}
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    return UserOut.model_validate(current_user)
