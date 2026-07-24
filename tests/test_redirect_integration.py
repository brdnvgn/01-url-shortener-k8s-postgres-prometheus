"""Tests d'intégration pour la redirection (`GET /{code}`).

Nécessitent une vraie base PostgreSQL disponible (voir docker-compose.yml).
"""

import pytest
from fastapi.testclient import TestClient

from url_shortener.config import settings

pytestmark = pytest.mark.usefixtures("clean_db")


@pytest.mark.parametrize(
    "invalid_code",
    [
        "has-dash",  # tiret non autorisé par le pattern [0-9A-Za-z]
        "has_underscore",  # underscore non autorisé
        "toolongcode123",  # plus de 10 caractères
        "space code",  # espace non autorisé
    ],
)
def test_redirect_code_not_matching_pattern_rejected_before_lookup(
    client: TestClient, invalid_code: str
) -> None:
    """Un code qui ne respecte pas le regex du path param doit être rejeté (422) avant
    toute tentative de résolution en base : la validation de format est bien la
    première ligne de défense, et non la recherche du code en base (qui renvoie 404).
    """
    response = client.get(f"/{invalid_code}", follow_redirects=False)

    assert response.status_code == 422


def test_redirect_unknown_but_valid_code_returns_404(client: TestClient) -> None:
    """Un code au bon format mais absent en base doit renvoyer une 404 applicative explicite."""
    response = client.get("/abc123", follow_redirects=False)

    assert response.status_code == 404
    assert response.json()["detail"] == "Code introuvable."


def test_redirect_known_code_returns_302_to_long_url(client: TestClient) -> None:
    """Un code existant doit rediriger (302) vers l'URL longue d'origine."""
    long_url = "https://example.com/known-code"
    code = client.post("/shorten", json={"url": long_url}).json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == long_url


async def test_redirect_increments_hits_counter_in_db(client: TestClient) -> None:
    """Chaque redirection réussie doit incrémenter le compteur `hits` en base."""
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
