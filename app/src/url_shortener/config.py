"""Application configuration (loaded from the environment)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, overridden by environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/url_shortener"
    code_length: int = 6
    pool_min_size: int = 1
    pool_max_size: int = 10


settings = Settings()
