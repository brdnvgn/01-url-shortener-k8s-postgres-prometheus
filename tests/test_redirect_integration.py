"""Integration tests for redirection (`GET /{code}`).

Require a real PostgreSQL database available (see docker-compose.yml).
"""

import pytest
from fastapi.testclient import TestClient

from url_shortener.config import settings

pytestmark = pytest.mark.usefixtures("clean_db")


@pytest.mark.parametrize(
    "invalid_code",
    [
        "has-dash",  # dash not allowed by the [0-9A-Za-z] pattern
        "has_underscore",  # underscore not allowed
        "toolongcode123",  # more than 10 characters
        "space code",  # space not allowed
    ],
)
def test_redirect_code_not_matching_pattern_rejected_before_lookup(
    client: TestClient, invalid_code: str
) -> None:
    """A code that doesn't match the path param regex must be rejected (422) before
    any attempt to resolve it in the database: format validation is indeed the
    first line of defense, not the database lookup (which returns 404).
    """
    response = client.get(f"/{invalid_code}", follow_redirects=False)

    assert response.status_code == 422


def test_redirect_unknown_but_valid_code_returns_404(client: TestClient) -> None:
    """A well-formatted code that is absent from the database must return an explicit application 404."""
    response = client.get("/abc123", follow_redirects=False)

    assert response.status_code == 404
    assert response.json()["detail"] == "Code not found."


def test_redirect_known_code_returns_302_to_long_url(client: TestClient) -> None:
    """An existing code must redirect (302) to the original long URL."""
    long_url = "https://example.com/known-code"
    code = client.post("/shorten", json={"url": long_url}).json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == long_url


async def test_redirect_increments_hits_counter_in_db(client: TestClient) -> None:
    """Each successful redirect must increment the `hits` counter in the database."""
    import asyncpg

    long_url = "https://example.com/counted"
    code = client.post("/shorten", json={"url": long_url}).json()["code"]

    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    conn = await asyncpg.connect(settings.database_url)
    try:
        hits = await conn.fetchval("SELECT hits FROM links WHERE code = $1", code)
    finally:
        await conn.close()

    assert hits == 3
