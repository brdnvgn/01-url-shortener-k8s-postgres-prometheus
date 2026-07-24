"""Integration tests for the health probe (`GET /healthz`).

Require a real PostgreSQL database available (see docker-compose.yml).
"""

import pytest
from fastapi.testclient import TestClient

from url_shortener import db


def test_healthz_returns_200_when_database_is_reachable(client: TestClient) -> None:
    """When PostgreSQL can serve a query, /healthz must report ok."""
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_returns_503_when_database_is_unreachable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the database pool can't serve a query, /healthz must report failure
    instead of a false-positive "ok", since /shorten and GET /{code} both
    depend on PostgreSQL to serve traffic.
    """

    class _BrokenPool:
        def acquire(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(db, "_pool", _BrokenPool())

    response = client.get("/healthz")

    assert response.status_code == 503
