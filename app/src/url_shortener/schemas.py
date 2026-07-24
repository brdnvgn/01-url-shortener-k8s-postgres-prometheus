"""Schémas Pydantic pour les requêtes et réponses de l'API."""

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    """Corps de la requête POST /shorten."""

    url: HttpUrl


class ShortenResponse(BaseModel):
    """Réponse renvoyée après création d'un lien court."""

    code: str
    short_url: str
