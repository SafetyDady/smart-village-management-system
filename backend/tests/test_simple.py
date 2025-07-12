"""
Simple tests to verify basic functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    """Test main endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_docs_endpoint():
    """Test that docs endpoint is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint():
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


def test_login_endpoint_exists():
    """Test that login endpoint exists and returns proper error for invalid data"""
    response = client.post("/api/v1/auth/login", data={
        "username": "invalid@example.com",
        "password": "wrongpassword"
    })
    # Should return 401 for invalid credentials
    assert response.status_code == 401


def test_users_endpoint_requires_auth():
    """Test that users endpoint requires authentication"""
    response = client.get("/api/v1/users/")
    # Should return 401 for missing authentication
    assert response.status_code == 401


def test_villages_endpoint_requires_auth():
    """Test that villages endpoint requires authentication"""
    response = client.get("/api/v1/villages/")
    # Should return 401 for missing authentication
    assert response.status_code == 401


def test_properties_endpoint_requires_auth():
    """Test that properties endpoint requires authentication"""
    response = client.get("/api/v1/properties/")
    # Should return 401 for missing authentication
    assert response.status_code == 401

