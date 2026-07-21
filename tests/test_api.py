import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from serving.main import app

client = TestClient(app)

def test_predict_valid_input():
    response = client.post(
        "/api/v1/predict/single",
        json={"description": "OAuth token validation failure on login endpoint"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert 'prediction' in data
    assert 0 <= data['confidence'] <= 1
    assert 0 <= data['uncertainty'] <= 1

def test_predict_invalid_input_empty():
    response = client.post(
        "/api/v1/predict/single",
        json={"description": ""}
    )
    assert response.status_code == 422

def test_get_history():
    response = client.get("/api/v1/predictions/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert 'total' in data

def test_get_model_info():
    response = client.get("/api/v1/models/info")
    assert response.status_code == 200
    data = response.json()
    assert data['version']
    assert data['num_teams'] == 10

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
