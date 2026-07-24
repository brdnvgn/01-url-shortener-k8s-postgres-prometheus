"""Application configuration (loaded from the environment)."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# The `links.code` column is VARCHAR(10) and the /{code} route only accepts
# 1-10 alphanumeric characters, so code_length must stay within that range.
MAX_CODE_LENGTH = 10

# Top-level paths registered directly on the FastAPI app (see main.py), which
# are matched before GET /{code}. A generated code equal to one of these would
# create a short link that can never redirect, so they must be excluded from
# code generation (see repository.create_short_link).
RESERVED_CODES = {"healthz", "readyz", "metrics"}


class Settings(BaseSettings):
    """Application settings, overridden by environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/url_shortener"
    code_length: int = Field(default=6, ge=1, le=MAX_CODE_LENGTH)
    pool_min_size: int = 1
    pool_max_size: int = 10
    # Public URL the API is exposed under (e.g. behind a Kubernetes Ingress).
    # When unset, falls back to X-Forwarded-* headers, then the raw ASGI base URL.
    public_base_url: str | None = None


settings = Settings()
