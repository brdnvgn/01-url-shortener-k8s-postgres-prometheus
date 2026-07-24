"""Tests unitaires pour la gestion du pool de connexions (`db.py`)."""

import pytest

from url_shortener import db


def test_get_pool_raises_when_not_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Appeler get_pool() avant connect() doit lever une erreur explicite."""
    monkeypatch.setattr(db, "_pool", None)

    with pytest.raises(RuntimeError, match="pas initialisé"):
        db.get_pool()


def test_get_pool_returns_pool_when_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Une fois le pool initialisé, get_pool() doit le renvoyer tel quel."""
    sentinel_pool = object()
    monkeypatch.setattr(db, "_pool", sentinel_pool)

    assert db.get_pool() is sentinel_pool
