"""Test Application Endpoints

Tests for the main application endpoints including health checks.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "AAS PAAS"
    assert data["version"] == "0.1.0"
    assert "environment" in data
    assert data["status"] == "operational"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "version" in data


def test_api_health_check(client: TestClient):
    """Test API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["api_version"] == "v1"


def test_not_found_endpoint(client: TestClient):
    """Test 404 handler for non-existent endpoint."""
    response = client.get("/nonexistent")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_cors_headers(client: TestClient):
    """Test CORS headers are present."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )

    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_security_headers(client: TestClient):
    """Test security headers are present in responses."""
    response = client.get("/")

    # Check security headers
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-xss-protection") == "1; mode=block"
