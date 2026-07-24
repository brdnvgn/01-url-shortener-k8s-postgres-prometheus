"""Unit tests for the data access layer (`repository.py`).

These tests isolate the business logic (retry on collision, hit counting) by
substituting a fake connection pool: they don't require PostgreSQL.
"""

from unittest.mock import AsyncMock

import asyncpg
import pytest

from url_shortener import repository


class FakePool:
    """Fake asyncpg pool driven by the tests."""

    def __init__(self, execute: AsyncMock | None = None, fetchrow: AsyncMock | None = None) -> None:
        self.execute = execute or AsyncMock()
        self.fetchrow = fetchrow or AsyncMock()


async def test_create_short_link_returns_generated_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """In the absence of a collision, the first generated code is returned as-is."""
    fake_pool = FakePool()
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    code = await repository.create_short_link("https://example.com", code_length=6)

    assert len(code) == 6
    fake_pool.execute.assert_awaited_once()


async def test_create_short_link_retries_on_collision(monkeypatch: pytest.MonkeyPatch) -> None:
    """On collision (code already existing), the function retries with a new code."""
    fake_pool = FakePool(
        execute=AsyncMock(side_effect=[asyncpg.UniqueViolationError(), None]),
    )
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    code = await repository.create_short_link("https://example.com", code_length=6)

    assert len(code) == 6
    assert fake_pool.execute.await_count == 2


async def test_create_short_link_raises_after_max_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    """If all attempts fail due to collision, an explicit error is raised."""
    fake_pool = FakePool(execute=AsyncMock(side_effect=asyncpg.UniqueViolationError()))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    with pytest.raises(RuntimeError, match="unique code"):
        await repository.create_short_link("https://example.com", code_length=6, max_retries=3)

    assert fake_pool.execute.await_count == 3


async def test_resolve_and_count_returns_long_url_when_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing code must return the associated long URL."""
    fake_pool = FakePool(fetchrow=AsyncMock(return_value={"long_url": "https://example.com"}))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    result = await repository.resolve_and_count("abc123")

    assert result == "https://example.com"


async def test_resolve_and_count_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unknown code must return None (later translated into a 404 by the route)."""
    fake_pool = FakePool(fetchrow=AsyncMock(return_value=None))
    monkeypatch.setattr(repository, "get_pool", lambda: fake_pool)

    result = await repository.resolve_and_count("inconnu")

    assert result is None
