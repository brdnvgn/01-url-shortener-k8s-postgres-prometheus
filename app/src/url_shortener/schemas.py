"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    """Request body for POST /shorten."""

    url: HttpUrl


class ShortenResponse(BaseModel):
    """Response returned after creating a short link."""

    code: str
    short_url: str
