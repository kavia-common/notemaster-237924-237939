import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    # Database
    postgres_url: str

    # Auth
    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    access_token_ttl_minutes: int

    # CORS
    cors_allow_origins: list[str]


def _parse_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load and validate settings from environment variables.

    Required env vars:
      - POSTGRES_URL
      - JWT_SECRET

    Optional env vars:
      - JWT_ISSUER (default: "notemaster")
      - JWT_AUDIENCE (default: "notemaster-web")
      - ACCESS_TOKEN_TTL_MINUTES (default: 10080 i.e. 7 days)
      - CORS_ALLOW_ORIGINS (default: "*")
    """
    postgres_url = os.getenv("POSTGRES_URL", "").strip()
    if not postgres_url:
        raise RuntimeError("Missing required env var POSTGRES_URL")

    jwt_secret = os.getenv("JWT_SECRET", "").strip()
    if not jwt_secret:
        raise RuntimeError("Missing required env var JWT_SECRET")

    jwt_issuer = os.getenv("JWT_ISSUER", "notemaster").strip()
    jwt_audience = os.getenv("JWT_AUDIENCE", "notemaster-web").strip()

    ttl_str = os.getenv("ACCESS_TOKEN_TTL_MINUTES", "10080").strip()
    try:
        ttl = int(ttl_str)
    except ValueError as exc:
        raise RuntimeError("ACCESS_TOKEN_TTL_MINUTES must be an integer") from exc

    cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
    cors_allow_origins = ["*"] if cors_origins_raw == "*" else _parse_csv(cors_origins_raw)

    return Settings(
        postgres_url=postgres_url,
        jwt_secret=jwt_secret,
        jwt_issuer=jwt_issuer,
        jwt_audience=jwt_audience,
        access_token_ttl_minutes=ttl,
        cors_allow_origins=cors_allow_origins,
    )
