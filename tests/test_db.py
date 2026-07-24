"""Unit tests for connection pool management (`db.py`)."""

import pytest

from url_shortener import db


def test_get_pool_raises_when_not_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Calling get_pool() before connect() must raise an explicit error."""
    monkeypatch.setattr(db, "_pool", None)

    with pytest.raises(RuntimeError, match="not initialized"):
        db.get_pool()


def test_get_pool_returns_pool_when_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Once the pool is initialized, get_pool() must return it as-is."""
    sentinel_pool = object()
    monkeypatch.setattr(db, "_pool", sentinel_pool)

    assert db.get_pool() is sentinel_pool
