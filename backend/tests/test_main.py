"""
Tests for main application endpoints
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "diagnoleads-api"
    assert data["version"] == "0.1.0"


def test_root(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "DiagnoLeads API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/api/docs"


def test_docs_available(client: TestClient):
    """Test that API docs are accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_openapi_schema_available(client: TestClient):
    """Test that OpenAPI schema is accessible"""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "DiagnoLeads API"
