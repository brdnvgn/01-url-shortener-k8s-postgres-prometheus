"""Data access layer: persisting and reading links in PostgreSQL."""

import asyncpg

from .config import RESERVED_CODES
from .db import get_pool
from .shortener import generate_code


async def create_short_link(long_url: str, code_length: int, max_retries: int = 5) -> str:
    """Creates a short link while guaranteeing code uniqueness (retries on collision)."""
    pool = get_pool()
    for _ in range(max_retries):
        code = generate_code(code_length)
        if code in RESERVED_CODES:
            # Would shadow a top-level route (e.g. /healthz) and never redirect.
            continue
        try:
            await pool.execute(
                "INSERT INTO links (code, long_url) VALUES ($1, $2)",
                code,
                long_url,
            )
            return code
        except asyncpg.UniqueViolationError:
            continue
    raise RuntimeError("Unable to generate a unique code after several attempts.")


async def resolve_and_count(code: str) -> str | None:
    """Returns the long URL associated with the code and increments its hit counter."""
    pool = get_pool()
    row = await pool.fetchrow(
        "UPDATE links SET hits = hits + 1 WHERE code = $1 RETURNING long_url",
        code,
    )
    return row["long_url"] if row is not None else None
