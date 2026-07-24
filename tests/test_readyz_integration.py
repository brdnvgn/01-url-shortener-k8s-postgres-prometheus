"""Integration tests for the readiness probe (`GET /readyz`).

Require a real PostgreSQL database available (see docker-compose.yml).
"""

import pytest
from fastapi.testclient import TestClient

from url_shortener import db


def test_readyz_returns_200_when_database_is_reachable(client: TestClient) -> None:
    """When PostgreSQL can serve a query, /readyz must report ok."""
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_returns_503_when_database_is_unreachable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the database pool can't serve a query, /readyz must report failure
    instead of a false-positive "ok", since /shorten and GET /{code} both
    depend on PostgreSQL to serve traffic.
    """

    class _BrokenPool:
        def acquire(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(db, "_pool", _BrokenPool())

    response = client.get("/readyz")

    assert response.status_code == 503
