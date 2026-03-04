import os
import datetime
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Try to find the root directory (.env location)
# If we're in backend/ it's parent; if we're in /app/ it might be same or parent
BACKEND_DIR = Path(__file__).resolve().parent
POSSIBLE_ENV_PATHS = [
    BACKEND_DIR.parent / ".env",   # Local root (running from backend/)
    Path("/app/.env"),             # Docker root
    BACKEND_DIR / ".env",          # Fallback inside backend
]

def get_env_file():
    for p in POSSIBLE_ENV_PATHS:
        if p.exists():
            return p
    return ".env"

class Settings(BaseSettings):
    database_host: str = Field("db", alias="DATABASE_HOST")
    database_port: str = Field("5432", alias="DATABASE_PORT")
    database_user: str = Field("sidequests", alias="POSTGRES_USER")
    database_password: str = Field("password", alias="POSTGRES_PASSWORD")
    database_name: str = Field("sidequests", alias="POSTGRES_DB")
    
    timezone: str = Field("UTC", alias="TIMEZONE")
    
    @property
    def database_url(self) -> str:
        # Check for DATABASE_URL environment variable directly for internal overrides (like tests)
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        return f"postgresql+psycopg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    @property
    def tz(self) -> datetime.timezone:
        """Returns a timezone object based on the configured timezone string."""
        try:
            import zoneinfo
        except ImportError:
            from backports import zoneinfo
        
        try:
            return zoneinfo.ZoneInfo(self.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            return zoneinfo.ZoneInfo("UTC")

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    secret_key: str = Field("super_secret_temporary_key_for_dev_change_me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    generator_type: str = Field("hardcoded", alias="GENERATOR_TYPE")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-5-mini", alias="OPENAI_MODEL")

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding='utf-8',
        extra="ignore",
        case_sensitive=False
    )

try:
    settings = Settings()
    print(f"--- Settings Loaded successfully (Source: {get_env_file()}) ---")
except Exception as e:
    print(f"--- Error loading settings: {e} ---")
    raise e
