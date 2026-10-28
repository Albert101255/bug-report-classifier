import pytest


@pytest.mark.asyncio
async def test_single_predict_inference(async_client, auth_headers):
    payload = {
        "description": "User login session ends abruptly with HTTP 500 when validating OAuth access token",
        "subject": "OAuth Session Timeout",
    }
    res = await async_client.post(
        "/api/v1/triage/predict", json=payload, headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert "predicted_team" in data
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert 0.0 <= data["uncertainty_score"] <= 1.0
    assert data["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert "severity" in data
    assert "sla_deadline" in data
    assert "stacktrace_analysis" in data


@pytest.mark.asyncio
async def test_review_queue_and_human_override(async_client, auth_headers):
    # Predict with low confidence or needs review
    payload = {
        "description": "Uncertain feature request or minor edge case without distinct keywords",
        "subject": "Minor edge behavior",
    }
    pred_res = await async_client.post(
        "/api/v1/triage/predict", json=payload, headers=auth_headers
    )
    pred_id = pred_res.json()["id"]

    # Check review queue
    q_res = await async_client.get("/api/v1/triage/review-queue", headers=auth_headers)
    assert q_res.status_code == 200

    # Human override
    override_res = await async_client.post(
        "/api/v1/triage/override",
        json={
            "prediction_id": pred_id,
            "corrected_team": "BL-102 (Database & ORM)",
            "reason": "Actually an ORM query mapping issue",
        },
        headers=auth_headers,
    )
    assert override_res.status_code == 200
    assert override_res.json()["corrected_team"] == "BL-102 (Database & ORM)"
    assert override_res.json()["success"] is True
