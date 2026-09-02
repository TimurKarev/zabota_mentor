"""Tests for the FastAPI app skeleton (Story 1.1a, AC-6)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_create_app_returns_fastapi_instance() -> None:
    app = create_app()
    assert isinstance(app, FastAPI)


@pytest.mark.parametrize("path", ["/", "/health"])
def test_liveness_routes_return_ok(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
