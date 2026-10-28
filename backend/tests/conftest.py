import os
import sys

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pytest
import pytest_asyncio
from app.auth.security import create_access_token, get_password_hash
from app.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models import Organization, OrganizationMember, Project, Team, User
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def seed_data():
    async with AsyncSessionLocal() as db:
        # Create Org
        org = Organization(
            id="test-org-1",
            name="Test Organization",
            slug="test-org",
        )
        db.add(org)

        # Create Admin User
        admin = User(
            id="test-user-admin",
            email="admin@test.com",
            hashed_password=get_password_hash("AdminSecret123!"),
            full_name="Admin User",
            role="ORG_ADMIN",
            is_active=True,
        )
        db.add(admin)

        # Create Developer User
        dev = User(
            id="test-user-dev",
            email="dev@test.com",
            hashed_password=get_password_hash("DevSecret123!"),
            full_name="Dev User",
            role="DEVELOPER",
            is_active=True,
        )
        db.add(dev)

        # Add memberships
        db.add(
            OrganizationMember(
                id="mem-1", organization_id=org.id, user_id=admin.id, role="ORG_ADMIN"
            )
        )
        db.add(
            OrganizationMember(
                id="mem-2", organization_id=org.id, user_id=dev.id, role="DEVELOPER"
            )
        )

        # Create Project
        project = Project(
            id="test-proj-1",
            organization_id=org.id,
            name="Test Project",
            key="TEST",
            description="Test engineering project",
        )
        db.add(project)

        # Create Teams
        t1 = Team(
            id="team-auth",
            organization_id=org.id,
            code="BL-101",
            name="BL-101 (Authentication & AuthZ)",
            description="Auth team",
            category="Security & Identity",
        )
        t2 = Team(
            id="team-db",
            organization_id=org.id,
            code="BL-102",
            name="BL-102 (Database & ORM)",
            description="Database team",
            category="Core Infrastructure",
        )
        db.add_all([t1, t2])
        await db.commit()

        return {
            "org": org,
            "admin": admin,
            "dev": dev,
            "project": project,
            "teams": [t1, t2],
        }


@pytest.fixture
def admin_token(seed_data):
    admin = seed_data["admin"]
    return create_access_token(
        {"sub": admin.id, "email": admin.email, "role": admin.role}
    )


@pytest.fixture
def dev_token(seed_data):
    dev = seed_data["dev"]
    return create_access_token({"sub": dev.id, "email": dev.email, "role": dev.role})


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def dev_headers(dev_token):
    return {"Authorization": f"Bearer {dev_token}"}


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
