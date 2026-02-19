"""Unit tests for main app (health, CORS) — TDD style."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert data.get("status") == "ok"


class TestAppConfig:
    def test_app_title(self):
        from main import app
        assert app.title == "BLS Signature Scheme"

    def test_bls_router_included(self):
        from main import app
        routes = [r.path for r in app.routes]
        assert any("/bls" in p or "bls" in p for p in routes)
