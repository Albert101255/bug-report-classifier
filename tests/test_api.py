import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
repository_root = Path(__file__).resolve().parents[1]
backend_root = repository_root / "backend"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_models_info():
    response = client.get("/api/v1/models/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "framework" in data
    assert "num_teams" in data


def test_batch_route_strictly_absent():
    response = client.post("/api/v1/predict/batch", json={"items": []})
    assert response.status_code in [404, 405]
