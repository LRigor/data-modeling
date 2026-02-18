"""
Example test file for Patient endpoints.
This demonstrates the testing structure - full implementation would require
test database setup and more comprehensive test cases.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_patients_empty():
    """Test getting patients when none exist."""
    response = client.get("/api/v1/patients")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []


def test_create_patient_validation_error():
    """Test patient creation with invalid data."""
    response = client.post(
        "/api/v1/patients",
        json={
            "person": {
                "first_name": "",
                "last_name": "Doe",
                "email": "invalid-email"
            },
            "medical_condition_id": "invalid-uuid"
        }
    )
    assert response.status_code == 422
