from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://sidequests:password@db:5432/sidequests"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    secret_key: str = "super_secret_temporary_key_for_dev_change_me"
    access_token_expire_minutes: int = 60 * 24 * 7 # 7 days for dev convenience

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
