"""Shared fixtures for unit and integration tests."""

from collections.abc import AsyncIterator, Generator

import asyncpg
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from url_shortener.config import settings
from url_shortener.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client. Triggers the lifespan (PostgreSQL connect/disconnect)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def clean_db(client: TestClient) -> AsyncIterator[None]:
    """Empties the `links` table before each test to guarantee test isolation.

    Uses an asyncpg connection independent from the application's pool (which
    lives in the TestClient's internal event loop) to avoid any event loop
    conflict between the test and the app.
    """
    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute("TRUNCATE TABLE links")
    finally:
        await conn.close()
    yield
