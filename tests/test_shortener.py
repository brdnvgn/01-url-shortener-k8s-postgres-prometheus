"""Tests unitaires pour la génération de codes courts (`shortener.py`)."""

import re

import pytest

from url_shortener.shortener import generate_code

# Alphabet base62 attendu, identique à celui accepté par la route GET /{code}.
CODE_REGEX = re.compile(r"^[0-9A-Za-z]+$")


@pytest.mark.parametrize("length", [1, 4, 6, 10])
def test_generate_code_matches_base62_regex(length: int) -> None:
    """Un code généré ne doit contenir que des caractères alphanumériques (base62)."""
    code = generate_code(length)
    assert CODE_REGEX.match(code), f"Le code '{code}' ne respecte pas le regex base62."


@pytest.mark.parametrize("length", [1, 4, 6, 10])
def test_generate_code_has_expected_length(length: int) -> None:
    """Le code généré doit avoir exactement la longueur demandée."""
    code = generate_code(length)
    assert len(code) == length


def test_generate_code_matches_route_path_pattern() -> None:
    """Un code de longueur par défaut (6) doit aussi respecter le pattern de la route GET /{code}."""
    route_pattern = re.compile(r"^[0-9A-Za-z]{1,10}$")
    code = generate_code(6)
    assert route_pattern.match(code)


def test_generate_code_is_random() -> None:
    """Deux appels successifs ne doivent (quasi) jamais produire le même code."""
    codes = {generate_code(8) for _ in range(200)}
    # Avec un alphabet de 62 caractères sur 8 positions, les collisions sont
    # statistiquement négligeables sur un échantillon de 200 tirages.
    assert len(codes) == 200
