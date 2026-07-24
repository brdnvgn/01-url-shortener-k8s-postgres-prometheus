"""Integration tests for the liveness probe (`GET /healthz`)."""

import pytest
from fastapi.testclient import TestClient

from url_shortener import db


def test_healthz_returns_200_when_database_is_reachable(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_returns_200_even_when_database_is_unreachable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """/healthz is a pure liveness probe: it must report ok regardless of the
    database state, so a transient PostgreSQL outage doesn't cause Kubernetes
    to restart an otherwise healthy pod (see /readyz for the DB-aware check).
    """

    class _BrokenPool:
        def acquire(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(db, "_pool", _BrokenPool())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
