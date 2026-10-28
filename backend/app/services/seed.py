import uuid

from app.auth.security import get_password_hash
from app.database import AsyncSessionLocal
from app.models import Organization, OrganizationMember, Project, Setting, Team, User
from app.routes.auth import DEFAULT_TEAMS
from sqlalchemy import select


async def seed_initial_workspace():
    async with AsyncSessionLocal() as session:
        # Check or create default organization
        org_res = await session.execute(select(Organization).limit(1))
        org = org_res.scalar_one_or_none()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name="Acme Engineering",
                slug="acme-engineering",
            )
            session.add(org)
            await session.flush()

            # Create default project
            project = Project(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                name="Main Platform",
                key="TRIAGE",
                description="Primary software engineering project for bug tracking and intelligent triage.",
            )
            session.add(project)

            # Seed default teams
            for code, name, description, category in DEFAULT_TEAMS:
                team = Team(
                    id=str(uuid.uuid4()),
                    organization_id=org.id,
                    code=code,
                    name=f"{code} ({name})",
                    description=description,
                    category=category,
                )
                session.add(team)

            # Default settings
            setting = Setting(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                confidence_high_threshold=0.25,
                confidence_low_threshold=0.50,
                auto_assign_enabled=True,
                duplicate_detection_threshold=0.22,
            )
            session.add(setting)

        # Check if admin@triage.local exists
        res = await session.execute(
            select(User).filter(User.email == "admin@triage.local")
        )
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email="admin@triage.local",
                hashed_password=get_password_hash("password123"),
                full_name="System Administrator",
                role="ORG_ADMIN",
                is_active=True,
            )
            session.add(user)
            await session.flush()

            member = OrganizationMember(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                user_id=user.id,
                role="ORG_ADMIN",
            )
            session.add(member)

        await session.commit()
