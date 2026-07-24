"""Tests unitaires pour les schémas Pydantic (`schemas.py`)."""

import pytest
from pydantic import ValidationError

from url_shortener.schemas import ShortenRequest, ShortenResponse


def test_shorten_request_accepts_valid_url() -> None:
    """Une URL valide doit être acceptée et exposée sous forme de chaîne."""
    payload = ShortenRequest(url="https://example.com/some/path")
    assert str(payload.url) == "https://example.com/some/path"


@pytest.mark.parametrize(
    "invalid_url",
    [
        "not-a-url",
        "ftp:/broken",
        "",
        "just some text",
    ],
)
def test_shorten_request_rejects_invalid_url(invalid_url: str) -> None:
    """Une chaîne qui n'est pas une URL valide doit lever une erreur de validation."""
    with pytest.raises(ValidationError):
        ShortenRequest(url=invalid_url)


def test_shorten_response_serialization() -> None:
    """La réponse doit exposer fidèlement le code et l'URL courte fournis."""
    response = ShortenResponse(code="abc123", short_url="http://localhost:8000/abc123")
    assert response.model_dump() == {
        "code": "abc123",
        "short_url": "http://localhost:8000/abc123",
    }
