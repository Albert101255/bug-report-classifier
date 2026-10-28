import pytest


@pytest.mark.asyncio
async def test_analytics_empty_and_populated(async_client, auth_headers, seed_data):
    # Initial empty state
    res = await async_client.get("/api/v1/analytics/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_issues"] == 0
    assert data["open_issues"] == 0
    assert data["avg_confidence"] == 0.0

    # Create an issue
    project = seed_data["project"]
    await async_client.post(
        "/api/v1/issues",
        json={
            "title": "Stripe webhook payment error",
            "description": "Payment failed during checkout with webhook dropped error",
            "project_id": project.id,
            "severity": "P1 - Critical",
        },
        headers=auth_headers,
    )

    # Check updated analytics
    updated_res = await async_client.get(
        "/api/v1/analytics/summary", headers=auth_headers
    )
    assert updated_res.status_code == 200
    updated_data = updated_res.json()
    assert updated_data["total_issues"] == 1
    assert updated_data["open_issues"] == 1
    assert "P1 - Critical" in updated_data["severity_breakdown"]
