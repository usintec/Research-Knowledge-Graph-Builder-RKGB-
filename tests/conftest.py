"""Root pytest configuration and shared fixtures.

Place fixtures used across all test suites here.
Suite-specific fixtures belong in the relevant sub-package conftest.py.
"""

from __future__ import annotations

import pytest
from app.main import create_app  # noqa: E402
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app() -> object:
    """Create a test FastAPI application instance.

    Returns:
        Configured FastAPI app.
    """
    return create_app()


@pytest.fixture(scope="session")
def client(app: object) -> TestClient:
    """Create a synchronous test client for the FastAPI app.

    Args:
        app: The FastAPI application fixture.

    Returns:
        Starlette TestClient wrapping the app.
    """
    return TestClient(app)  # type: ignore[arg-type]
