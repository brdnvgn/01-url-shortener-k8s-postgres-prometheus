"""Unit tests for Pydantic schemas (`schemas.py`)."""

import pytest
from pydantic import ValidationError

from url_shortener.schemas import ShortenRequest, ShortenResponse


def test_shorten_request_accepts_valid_url() -> None:
    """A valid URL must be accepted and exposed as a string."""
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
    """A string that isn't a valid URL must raise a validation error."""
    with pytest.raises(ValidationError):
        ShortenRequest(url=invalid_url)


def test_shorten_response_serialization() -> None:
    """The response must faithfully expose the provided code and short URL."""
    response = ShortenResponse(code="abc123", short_url="http://localhost:8000/abc123")
    assert response.model_dump() == {
        "code": "abc123",
        "short_url": "http://localhost:8000/abc123",
    }
