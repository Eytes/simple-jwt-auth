import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    """Класс конфигурации приложения, использует переменные окружения."""

    BASE_DIR: Path = Path(__file__).parent.parent

    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "public.pem"
    ALGORITHM: str = "RS256"

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_DB: int = int(os.getenv("REDIS_DB"))

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


settings = Settings()
