"""Accès aux données : persistance et lecture des liens dans PostgreSQL."""

import asyncpg

from .db import get_pool
from .shortener import generate_code


async def create_short_link(long_url: str, code_length: int, max_retries: int = 5) -> str:
    """Crée un lien court en garantissant l'unicité du code (retry sur collision)."""
    pool = get_pool()
    for _ in range(max_retries):
        code = generate_code(code_length)
        try:
            await pool.execute(
                "INSERT INTO links (code, long_url) VALUES ($1, $2)",
                code,
                long_url,
            )
            return code
        except asyncpg.UniqueViolationError:
            continue
    raise RuntimeError("Impossible de générer un code unique après plusieurs tentatives.")


async def resolve_and_count(code: str) -> str | None:
    """Retourne l'URL longue associée au code et incrémente son compteur de hits."""
    pool = get_pool()
    row = await pool.fetchrow(
        "UPDATE links SET hits = hits + 1 WHERE code = $1 RETURNING long_url",
        code,
    )
    return row["long_url"] if row is not None else None
