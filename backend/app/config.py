from functools import lru_cache
from pathlib import Path
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "ChangeMe-Secret-Key-please-override"


def _resolve_secret(raw: str) -> str:
    """未显式配置 secret 时，自动生成并持久化到本地文件，
    避免 token 用公开默认密钥签发（可被伪造），同时重启不失效。"""
    if raw != _DEFAULT_SECRET:
        return raw
    key_file = Path(__file__).resolve().parent.parent / ".jwt_secret"
    try:
        if key_file.exists():
            saved = key_file.read_text().strip()
            if saved:
                return saved
        secret = secrets.token_hex(32)
        key_file.write_text(secret)
        return secret
    except OSError:
        return secrets.token_hex(32)  # 只读环境：每次重启换密钥，旧 token 全失效


class Settings(BaseSettings):
    """应用配置。可通过环境变量或 .env 覆盖。"""

    app_name: str = "classmate"
    version: str = "0.2.0"
    secret_key: str = _DEFAULT_SECRET
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 天

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.secret_key = _resolve_secret(s.secret_key)
    return s
