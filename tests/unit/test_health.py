"""Unit tests for the application entry point and health check endpoint."""

from __future__ import annotations

import pytest
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    """Create a test client for a fresh app instance.

    Returns:
        Synchronous test client wrapping the FastAPI app.
    """
    return TestClient(create_app())


@pytest.mark.unit()
def test_health_returns_ok(client: TestClient) -> None:
    """GET /health should return HTTP 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rkgb"}


@pytest.mark.unit()
def test_health_content_type_is_json(client: TestClient) -> None:
    """GET /health response should have a JSON content-type header."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


@pytest.mark.unit()
def test_create_app_returns_fastapi_instance() -> None:
    """create_app() should return a configured FastAPI application."""
    from fastapi import FastAPI

    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "Research Knowledge Graph Builder"
