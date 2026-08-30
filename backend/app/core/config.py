"""Application configuration.

Every tunable value lives here and comes from the environment, never from a
literal buried in the code. `Settings` is a Pydantic model, so a missing or
malformed variable fails loudly at startup instead of silently at 3am.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
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

    # --- Security / JWT ---
    # Signing key for our own access tokens. Anyone who has this can mint a
    # valid token for ANY user, so it must be random, secret, and per-environment.
    # Generate one with:  python -c "import secrets; print(secrets.token_urlsafe(48))"
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    # Short-lived on purpose: a JWT cannot be revoked, so expiry is the only
    # thing bounding the damage from a stolen token.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BCRYPT_COST: int = 12  # 2^12 = 4096 rounds, ~200ms per hash

    # --- Google OAuth 2.0 ---
    # Empty by default so the app runs fine without Google configured; the
    # /api/auth/google endpoint reports 503 instead of crashing at startup.
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5174/login"

    @property
    def google_oauth_configured(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)

    # --- Match score weights (must sum to 1.0) ---
    TEXT_SIMILARITY_WEIGHT: float = 0.4
    SKILL_MATCH_WEIGHT: float = 0.4
    KEYWORD_MATCH_WEIGHT: float = 0.2
    TOP_KEYWORDS: int = 15

    # A required skill the resume does not name, but shows related experience
    # for, earns this fraction of a point. 0 would ignore related work
    # entirely; 1 would treat Kubernetes as if it were Docker.
    PARTIAL_SKILL_CREDIT: float = 0.5

    # Phase 9, optional. Reported alongside TF-IDF similarity, never folded into
    # the overall score: that would make the score unexplainable and would
    # silently shift it relative to saved history.
    SEMANTIC_SIMILARITY_ENABLED: bool = True

    # --- CORS ---
    # Kept as a plain string on purpose: Pydantic tries to JSON-decode env vars
    # typed as `list`, which chokes on "a,b". We split it ourselves below.
    CORS_ORIGINS: str = "http://localhost:5174,http://127.0.0.1:5174"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, value: str) -> str:
        """Fail at startup rather than ship a forgeable signing key."""
        if len(value) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. Generate one with: "
                'python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if value.startswith("replace_me"):
            raise ValueError("SECRET_KEY is still the placeholder from .env.example")
        return value

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so the .env file is parsed exactly once per process."""
    return Settings()


settings = get_settings()
