"""Gestion du pool de connexions PostgreSQL (asyncpg)."""

import asyncpg

from .config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    code       VARCHAR(10) PRIMARY KEY,
    long_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hits       BIGINT DEFAULT 0
);
"""

_pool: asyncpg.Pool | None = None


async def connect() -> None:
    """Initialise le pool de connexions et crée la table si nécessaire."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.pool_min_size,
            max_size=settings.pool_max_size,
        )
        async with _pool.acquire() as conn:
            await conn.execute(_SCHEMA)


async def disconnect() -> None:
    """Ferme proprement le pool de connexions."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """Retourne le pool actif ou lève une erreur s'il n'est pas initialisé."""
    if _pool is None:
        raise RuntimeError("Le pool PostgreSQL n'est pas initialisé.")
    return _pool
