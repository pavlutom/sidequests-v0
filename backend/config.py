from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str = "db"
    database_port: str = "5432"
    database_user: str = "sidequests"
    database_password: str = "password"
    database_name: str = "sidequests"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    secret_key: str = "super_secret_temporary_key_for_dev_change_me"
    access_token_expire_minutes: int = 60 * 24 * 7 # 7 days for dev convenience

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
