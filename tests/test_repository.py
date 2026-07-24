"""Tests unitaires pour la couche d'accès aux données (`repository.py`).

Ces tests isolent la logique métier (retry sur collision, comptage des hits) en
substituant un faux pool de connexions : ils ne nécessitent pas de PostgreSQL.
"""

from unittest.mock import AsyncMock

import asyncpg
import pytest

from url_shortener import repository


class FakePool:
    """Faux pool asyncpg piloté par les tests."""

    def __init__(self, execute: AsyncMock | None = None, fetchrow: AsyncMock | None = None) -> None:
        self.execute = execute or AsyncMock()
        self.fetchrow = fetchrow or AsyncMock()


async def test_create_short_link_returns_generated_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """En l'absence de collision, le premier code généré est renvoyé tel quel."""
    fake_pool = FakePool()
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    code = await repository.create_short_link("https://example.com", code_length=6)

    assert len(code) == 6
    fake_pool.execute.assert_awaited_once()


async def test_create_short_link_retries_on_collision(monkeypatch: pytest.MonkeyPatch) -> None:
    """En cas de collision (code déjà existant), la fonction retente avec un nouveau code."""
    fake_pool = FakePool(
        execute=AsyncMock(side_effect=[asyncpg.UniqueViolationError(), None]),
    )
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    code = await repository.create_short_link("https://example.com", code_length=6)

    assert len(code) == 6
    assert fake_pool.execute.await_count == 2


async def test_create_short_link_raises_after_max_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    """Si toutes les tentatives échouent par collision, une erreur explicite est levée."""
    fake_pool = FakePool(execute=AsyncMock(side_effect=asyncpg.UniqueViolationError()))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    with pytest.raises(RuntimeError, match="code unique"):
        await repository.create_short_link("https://example.com", code_length=6, max_retries=3)

    assert fake_pool.execute.await_count == 3


async def test_resolve_and_count_returns_long_url_when_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un code existant doit renvoyer l'URL longue associée."""
    fake_pool = FakePool(fetchrow=AsyncMock(return_value={"long_url": "https://example.com"}))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    result = await repository.resolve_and_count("abc123")

    assert result == "https://example.com"


async def test_resolve_and_count_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un code inconnu doit renvoyer None (traduit ensuite en 404 par la route)."""
    fake_pool = FakePool(fetchrow=AsyncMock(return_value=None))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    result = await repository.resolve_and_count("inconnu")

    assert result is None
