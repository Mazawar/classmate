from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置。可通过环境变量或 .env 覆盖。"""

    app_name: str = "classmate"
    version: str = "0.1.0"
    secret_key: str = "ChangeMe-Secret-Key-please-override"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 天

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
