"""Tests d'intégration pour la création de liens courts (`POST /shorten`).

Nécessitent une vraie base PostgreSQL disponible (voir docker-compose.yml).
"""

import re

import pytest
from fastapi.testclient import TestClient
from pydantic import HttpUrl, TypeAdapter

pytestmark = pytest.mark.usefixtures("clean_db")

CODE_REGEX = re.compile(r"^[0-9A-Za-z]{1,10}$")
_url_adapter: TypeAdapter[HttpUrl] = TypeAdapter(HttpUrl)


def test_shorten_returns_201_with_valid_short_url(client: TestClient) -> None:
    """La short_url renvoyée doit être une URL syntaxiquement valide."""
    response = client.post("/shorten", json={"url": "https://example.com/some/very/long/path"})

    assert response.status_code == 201
    body = response.json()

    assert "code" in body and "short_url" in body
    # Lève une ValidationError si l'URL n'est pas valide.
    _url_adapter.validate_python(body["short_url"])
    assert body["short_url"].endswith(f"/{body['code']}")


def test_shorten_returns_code_matching_route_pattern(client: TestClient) -> None:
    """Le code généré doit respecter le pattern accepté par GET /{code}."""
    response = client.post("/shorten", json={"url": "https://example.com"})

    assert response.status_code == 201
    code = response.json()["code"]
    assert CODE_REGEX.match(code)


def test_shorten_rejects_invalid_url_with_422(client: TestClient) -> None:
    """Une URL invalide dans le corps de la requête doit être rejetée (422)."""
    response = client.post("/shorten", json={"url": "not-a-valid-url"})

    assert response.status_code == 422


def test_shorten_created_short_url_actually_resolves(client: TestClient) -> None:
    """La short_url créée doit permettre, une fois appelée, de retomber sur l'URL d'origine."""
    long_url = "https://example.com/target-page"
    create_response = client.post("/shorten", json={"url": long_url})
    code = create_response.json()["code"]

    redirect_response = client.get(f"/{code}", follow_redirects=False)

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == long_url
