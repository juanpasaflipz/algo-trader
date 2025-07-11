"""Basic health check tests for the API."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"
    assert "timestamp" in data

    # Verify timestamp is valid
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert isinstance(timestamp, datetime)


def test_status_check(client):
    """Test the status check endpoint."""
    response = client.get("/api/v1/status")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "operational"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"
    assert "timestamp" in data
    assert "services" in data

    # Check service statuses
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert "webhooks" in services
    assert services["webhooks"] == "active"


def test_root_redirect(client):
    """Test that root path returns appropriate response."""
    response = client.get("/")
    # The app doesn't have a root handler, so it should return 404
    assert response.status_code == 404


def test_docs_available(client):
    """Test that API docs are available in development."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "Algo Trader"
    assert schema["info"]["version"] == "0.1.0"
