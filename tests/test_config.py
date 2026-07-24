"""Unit tests for application settings (`config.py`)."""

import pytest
from pydantic import ValidationError

from url_shortener.config import MAX_CODE_LENGTH, Settings


@pytest.mark.parametrize("code_length", [1, 6, MAX_CODE_LENGTH])
def test_settings_accepts_code_length_within_bounds(code_length: int) -> None:
    """A code_length within [1, MAX_CODE_LENGTH] must be accepted as-is."""
    settings = Settings(code_length=code_length)
    assert settings.code_length == code_length


@pytest.mark.parametrize("code_length", [0, -1, MAX_CODE_LENGTH + 1, 100])
def test_settings_rejects_code_length_out_of_bounds(code_length: int) -> None:
    """A code_length outside [1, MAX_CODE_LENGTH] must be rejected.

    The `links.code` column is VARCHAR(10) and GET /{code} only accepts
    1-10 characters, so out-of-range values would otherwise break inserts
    (truncation) or collision handling (empty codes).
    """
    with pytest.raises(ValidationError):
        Settings(code_length=code_length)
