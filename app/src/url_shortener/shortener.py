"""Génération de codes courts aléatoires (base62)."""

import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int) -> str:
    """Génère un code aléatoire base62 de la longueur demandée."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
