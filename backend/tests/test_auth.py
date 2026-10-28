import pytest


@pytest.mark.asyncio
async def test_register_first_user_creates_org(async_client):
    res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "lead@startup.io",
            "password": "StrongPassword123!",
            "full_name": "Engineering Lead",
            "organization_name": "Acme Systems",
            "role": "ORG_ADMIN",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "lead@startup.io"
    assert data["user"]["role"] == "ORG_ADMIN"


@pytest.mark.asyncio
async def test_login_success(async_client, seed_data):
    res = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminSecret123!",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"


@pytest.mark.asyncio
async def test_login_invalid_password(async_client, seed_data):
    res = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "WrongPassword!",
        },
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_me_profile(async_client, auth_headers):
    res = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "ORG_ADMIN"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(async_client):
    res = await async_client.get("/api/v1/auth/me")
    assert res.status_code == 401
