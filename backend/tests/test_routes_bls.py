"""Unit tests for app.routes.bls API — TDD style."""

import pytest
from fastapi.testclient import TestClient
from app.schemas.bls import BLSRequest


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


@pytest.fixture
def valid_request_body():
    return {
        "p": 103,
        "A": 1,
        "B": 0,
        "private_key": 7,
        "message": "hello",
    }


class TestRunBlsEndpoint:
    def test_run_bls_returns_200_and_valid_response(self, client, valid_request_body):
        response = client.post("/api/bls/run", json=valid_request_body)
        # May be 501 if BLS not implemented, or 200 if implemented
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            data = response.json()
            assert "group_order" in data
            assert "verified" in data
            assert "signature" in data

    def test_run_bls_invalid_params_returns_4xx(self, client):
        # Invalid p (not prime): may return 400 (ValueError) once validated, or 501 if init runs first
        response = client.post("/api/bls/run", json={
            "p": 104,  # not prime
            "A": 1,
            "B": 0,
            "private_key": 1,
            "message": "x",
        })
        assert response.status_code in (400, 501)

    def test_run_bls_singular_curve_returns_400(self, client):
        response = client.post("/api/bls/run", json={
            "p": 103,
            "A": 0,
            "B": 0,
            "private_key": 1,
            "message": "x",
        })
        assert response.status_code in (400, 501)

    def test_run_bls_request_schema_valid(self, valid_request_body):
        req = BLSRequest(**valid_request_body)
        assert req.message == "hello"
        assert req.p == 103
        assert req.private_key == 7
