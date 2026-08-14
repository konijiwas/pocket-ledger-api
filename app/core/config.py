from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketLedger API"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./pocket_ledger.db"

    jwt_secret_key: str = (
        "development-only-secret-key-change-before-production"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
   
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()