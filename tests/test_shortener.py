"""Unit tests for short code generation (`shortener.py`)."""

import re

import pytest

from url_shortener.shortener import generate_code

# Expected base62 alphabet, identical to the one accepted by the GET /{code} route.
CODE_REGEX = re.compile(r"^[0-9A-Za-z]+$")


@pytest.mark.parametrize("length", [1, 4, 6, 10])
def test_generate_code_matches_base62_regex(length: int) -> None:
    """A generated code must contain only alphanumeric characters (base62)."""
    code = generate_code(length)
    assert CODE_REGEX.match(code), f"Code '{code}' does not match the base62 regex."


@pytest.mark.parametrize("length", [1, 4, 6, 10])
def test_generate_code_has_expected_length(length: int) -> None:
    """The generated code must have exactly the requested length."""
    code = generate_code(length)
    assert len(code) == length


def test_generate_code_matches_route_path_pattern() -> None:
    """A code with the default length (6) must also match the GET /{code} route pattern."""
    route_pattern = re.compile(r"^[0-9A-Za-z]{1,10}$")
    code = generate_code(6)
    assert route_pattern.match(code)


def test_generate_code_is_random() -> None:
    """Two successive calls must (almost) never produce the same code."""
    codes = {generate_code(8) for _ in range(200)}
    # With a 62-character alphabet over 8 positions, collisions are
    # statistically negligible over a sample of 200 draws.
    assert len(codes) == 200
