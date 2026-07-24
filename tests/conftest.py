"""Fixtures partagées pour les tests unitaires et d'intégration."""

from collections.abc import AsyncIterator, Generator

import asyncpg
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from url_shortener.config import settings
from url_shortener.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Client de test FastAPI. Déclenche le lifespan (connexion/déconnexion PostgreSQL)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def clean_db(client: TestClient) -> AsyncIterator[None]:
    """Vide la table `links` avant chaque test pour garantir l'isolation des tests.

    Utilise une connexion asyncpg indépendante du pool de l'application (qui vit
    dans la boucle d'événements interne du TestClient) afin d'éviter tout conflit
    de boucle d'événements entre le test et l'app.
    """
    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute("TRUNCATE TABLE links")
    finally:
        await conn.close()
    yield
