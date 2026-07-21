import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    res = await async_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_single_prediction(async_client):
    payload = {
        "description": "PostgreSQL database connection timeout when executing complex inner join query",
        "subject": "DB Timeout Issue",
        "user_id": "test_user_1"
    }
    res = await async_client.post("/api/v1/predict/single", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_team" in data
    assert "confidence_score" in data
    assert "uncertainty_score" in data
    assert data["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]

@pytest.mark.asyncio
async def test_batch_prediction(async_client):
    payload = {
        "items": [
            {"description": "OAuth login failed on mobile auth screen", "subject": "Auth Bug"},
            {"description": "Stripe webhook signature validation failed", "subject": "Billing Bug"}
        ]
    }
    res = await async_client.post("/api/v1/predict/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 2
    assert len(data["predictions"]) == 2

@pytest.mark.asyncio
async def test_teams_list(async_client):
    res = await async_client.get("/api/v1/teams/list")
    assert res.status_code == 200
    teams = res.json()
    assert len(teams) >= 5

@pytest.mark.asyncio
async def test_analytics_summary(async_client):
    res = await async_client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    summary = res.json()
    assert "avg_confidence" in summary
    assert "team_accuracy_breakdown" in summary
