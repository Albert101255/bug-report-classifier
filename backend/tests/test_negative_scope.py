import pytest
from app.database import Base


@pytest.mark.asyncio
async def test_batch_routes_do_not_exist(async_client, auth_headers):
    # Old prediction batch route must return 404 Not Found
    res = await async_client.post(
        "/api/v1/predict/batch",
        json={"items": [{"description": "foo"}]},
        headers=auth_headers,
    )
    assert res.status_code == 404

    # Triage batch route must also return 404
    res2 = await async_client.post(
        "/api/v1/triage/batch",
        json={"items": [{"description": "foo"}]},
        headers=auth_headers,
    )
    assert res2.status_code == 404

    # Bulk issue import must not exist (returns 404 or 405 method not allowed)
    res3 = await async_client.post(
        "/api/v1/issues/import",
        json={"csv": "foo,bar"},
        headers=auth_headers,
    )
    assert res3.status_code in [404, 405]


def test_no_import_tables_in_database_metadata():
    table_names = set(Base.metadata.tables.keys())
    for banned in ["import_jobs", "batch_imports", "csv_uploads", "batch_predictions"]:
        assert banned not in table_names, (
            f"Disallowed table '{banned}' found in database metadata"
        )


def test_openapi_schema_contains_no_batch_endpoints(async_client):
    from app.main import app

    openapi = app.openapi()
    paths = openapi.get("paths", {})
    for path in paths:
        assert "batch" not in path.lower(), (
            f"Disallowed batch endpoint found in OpenAPI: {path}"
        )
        assert "import" not in path.lower(), (
            f"Disallowed import endpoint found in OpenAPI: {path}"
        )
        assert "upload" not in path.lower(), (
            f"Disallowed bulk upload endpoint found in OpenAPI: {path}"
        )
