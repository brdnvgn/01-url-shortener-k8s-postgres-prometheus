"""Random short code generation (base62)."""

import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int) -> str:
    """Generates a random base62 code of the requested length."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
