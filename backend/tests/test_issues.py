import pytest


@pytest.mark.asyncio
async def test_create_and_fetch_issue(async_client, auth_headers, seed_data):
    project = seed_data["project"]
    payload = {
        "title": "OAuth 500 error when refreshing access tokens",
        "description": "User login fails on auth refresh token rotation with Internal Server Error 500",
        "project_id": project.id,
        "severity": "P1 - Critical",
        "priority": "HIGH",
        "environment": "Production",
        "technical_logs": "Traceback: OAuthTokenError: connection timeout on redis session pool",
    }
    res = await async_client.post("/api/v1/issues", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["issue_key"].startswith("TEST-")
    assert data["title"] == payload["title"]
    assert data["reporter"]["email"] == "admin@test.com"

    # Fetch detail
    issue_id = data["id"]
    detail_res = await async_client.get(
        f"/api/v1/issues/{issue_id}", headers=auth_headers
    )
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == issue_id


@pytest.mark.asyncio
async def test_status_lifecycle_transitions(async_client, auth_headers, seed_data):
    project = seed_data["project"]
    res = await async_client.post(
        "/api/v1/issues",
        json={
            "title": "Database slow query in report dashboard",
            "description": "PostgreSQL query runs slow and hits pool limit",
            "project_id": project.id,
        },
        headers=auth_headers,
    )
    assert res.status_code == 201
    issue_id = res.json()["id"]
    assert res.json()["status"] in ["NEW", "TRIAGE"]

    # Valid transition to IN_PROGRESS
    upd_res = await async_client.patch(
        f"/api/v1/issues/{issue_id}",
        json={"status": "IN_PROGRESS"},
        headers=auth_headers,
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["status"] == "IN_PROGRESS"

    # Valid transition to FIXED
    fix_res = await async_client.patch(
        f"/api/v1/issues/{issue_id}",
        json={"status": "FIXED"},
        headers=auth_headers,
    )
    assert fix_res.status_code == 200
    assert fix_res.json()["status"] == "FIXED"

    # Invalid jump (FIXED cannot jump directly to TRIAGE without REOPENED)
    invalid_res = await async_client.patch(
        f"/api/v1/issues/{issue_id}",
        json={"status": "TRIAGE"},
        headers=auth_headers,
    )
    assert invalid_res.status_code == 400


@pytest.mark.asyncio
async def test_comments_and_audit_trail(async_client, auth_headers, seed_data):
    project = seed_data["project"]
    res = await async_client.post(
        "/api/v1/issues",
        json={
            "title": "UI modal clipping on mobile Safari",
            "description": "Dropdown clipped",
            "project_id": project.id,
        },
        headers=auth_headers,
    )
    issue_id = res.json()["id"]

    # Add comment
    comment_res = await async_client.post(
        f"/api/v1/issues/{issue_id}/comments",
        json={"content": "Reproduced on iPhone 15 Pro iOS 17.4"},
        headers=auth_headers,
    )
    assert comment_res.status_code == 200
    assert comment_res.json()["content"] == "Reproduced on iPhone 15 Pro iOS 17.4"

    # Fetch audit trail
    audit_res = await async_client.get(
        f"/api/v1/issues/{issue_id}/audit-trail", headers=auth_headers
    )
    assert audit_res.status_code == 200
    actions = [e["action"] for e in audit_res.json()]
    assert "ISSUE_CREATED" in actions
    assert "COMMENT_ADDED" in actions
