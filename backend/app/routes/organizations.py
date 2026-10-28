import uuid

from app.auth.dependencies import get_user_organization, require_role
from app.database import get_db
from app.models import Organization, Project, Team, User
from app.schemas import OrganizationOut, ProjectCreate, ProjectOut, TeamCreate, TeamOut
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="", tags=["Organizations & Teams"])


@router.get("/organizations/current", response_model=OrganizationOut)
async def get_current_organization(
    org: Organization = Depends(get_user_organization),
) -> OrganizationOut:
    return OrganizationOut.model_validate(org)


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectOut]:
    res = await db.execute(
        select(Project)
        .filter(Project.organization_id == org.id)
        .order_by(Project.created_at.asc())
    )
    projects = res.scalars().all()
    return [ProjectOut.model_validate(p) for p in projects]


@router.post(
    "/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED
)
async def create_project(
    req: ProjectCreate,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(require_role(["ORG_ADMIN", "PROJECT_MANAGER"])),
    db: AsyncSession = Depends(get_db),
) -> ProjectOut:
    # Check key uniqueness in org
    res = await db.execute(
        select(Project).filter(
            Project.organization_id == org.id,
            Project.key == req.key.upper(),
        )
    )
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with key '{req.key}' already exists in this organization.",
        )

    project = Project(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        name=req.name,
        key=req.key.upper(),
        description=req.description,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectOut.model_validate(project)


@router.get("/teams", response_model=list[TeamOut])
async def list_teams(
    org: Organization = Depends(get_user_organization),
    db: AsyncSession = Depends(get_db),
) -> list[TeamOut]:
    res = await db.execute(
        select(Team).filter(Team.organization_id == org.id).order_by(Team.code.asc())
    )
    teams = res.scalars().all()
    return [TeamOut.model_validate(t) for t in teams]


@router.post("/teams", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def create_team(
    req: TeamCreate,
    org: Organization = Depends(get_user_organization),
    current_user: User = Depends(require_role(["ORG_ADMIN", "PROJECT_MANAGER"])),
    db: AsyncSession = Depends(get_db),
) -> TeamOut:
    # Check code uniqueness
    res = await db.execute(
        select(Team).filter(
            Team.organization_id == org.id,
            Team.code == req.code,
        )
    )
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team with code '{req.code}' already exists in this organization.",
        )

    team = Team(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        code=req.code,
        name=req.name,
        description=req.description,
        category=req.category,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return TeamOut.model_validate(team)
