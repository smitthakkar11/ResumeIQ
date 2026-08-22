"""Application configuration.

Every tunable value lives here and comes from the environment, never from a
literal buried in the code. `Settings` is a Pydantic model, so a missing or
malformed variable fails loudly at startup instead of silently at 3am.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[2] == backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "ResumeIQ"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api"

    # --- Database ---
    DATABASE_URL: str

    # --- CORS ---
    # Kept as a plain string on purpose: Pydantic tries to JSON-decode env vars
    # typed as `list`, which chokes on "a,b". We split it ourselves below.
    CORS_ORIGINS: str = "http://localhost:5174,http://127.0.0.1:5174"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so the .env file is parsed exactly once per process."""
    return Settings()


settings = get_settings()
