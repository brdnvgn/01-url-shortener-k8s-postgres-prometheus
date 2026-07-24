"""Integration tests for short link creation (`POST /shorten`).

Require a real PostgreSQL database available (see docker-compose.yml).
"""

import re

import pytest
from fastapi.testclient import TestClient
from pydantic import HttpUrl, TypeAdapter

from url_shortener.config import settings

pytestmark = pytest.mark.usefixtures("clean_db")

CODE_REGEX = re.compile(r"^[0-9A-Za-z]{1,10}$")
_url_adapter: TypeAdapter[HttpUrl] = TypeAdapter(HttpUrl)


def test_shorten_returns_201_with_valid_short_url(client: TestClient) -> None:
    """The returned short_url must be a syntactically valid URL."""
    response = client.post("/shorten", json={"url": "https://example.com/some/very/long/path"})

    assert response.status_code == 201
    body = response.json()

    assert "code" in body and "short_url" in body
    # Raises a ValidationError if the URL isn't valid.
    _url_adapter.validate_python(body["short_url"])
    assert body["short_url"].endswith(f"/{body['code']}")


def test_shorten_returns_code_matching_route_pattern(client: TestClient) -> None:
    """The generated code must match the pattern accepted by GET /{code}."""
    response = client.post("/shorten", json={"url": "https://example.com"})

    assert response.status_code == 201
    code = response.json()["code"]
    assert CODE_REGEX.match(code)


def test_shorten_rejects_invalid_url_with_422(client: TestClient) -> None:
    """An invalid URL in the request body must be rejected (422)."""
    response = client.post("/shorten", json={"url": "not-a-valid-url"})

    assert response.status_code == 422


def test_shorten_created_short_url_actually_resolves(client: TestClient) -> None:
    """The created short_url, once called, must resolve back to the original URL."""
    long_url = "https://example.com/target-page"
    create_response = client.post("/shorten", json={"url": long_url})
    code = create_response.json()["code"]

    redirect_response = client.get(f"/{code}", follow_redirects=False)

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == long_url


def test_shorten_uses_x_forwarded_host_over_internal_base_url(client: TestClient) -> None:
    """Behind a reverse proxy/Ingress, short_url must use the public host from
    X-Forwarded-Host/X-Forwarded-Proto instead of the internal ASGI base_url.
    """
    response = client.post(
        "/shorten",
        json={"url": "https://example.com/proxied"},
        headers={"X-Forwarded-Host": "short.example.com", "X-Forwarded-Proto": "https"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["short_url"] == f"https://short.example.com/{body['code']}"


def test_shorten_uses_configured_public_base_url_over_forwarded_headers(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicitly configured PUBLIC_BASE_URL must take precedence over
    forwarded headers and the raw request base URL.
    """
    monkeypatch.setattr(settings, "public_base_url", "https://configured.example.com")

    response = client.post(
        "/shorten",
        json={"url": "https://example.com/configured"},
        headers={"X-Forwarded-Host": "should-be-ignored.example.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["short_url"] == f"https://configured.example.com/{body['code']}"
