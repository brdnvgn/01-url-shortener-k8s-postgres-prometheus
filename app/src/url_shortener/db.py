"""Management of the PostgreSQL connection pool (asyncpg)."""

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
    """Initializes the connection pool and creates the table if needed."""
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
    """Cleanly closes the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """Returns the active pool or raises an error if it isn't initialized."""
    if _pool is None:
        raise RuntimeError("The PostgreSQL pool is not initialized.")
    return _pool
