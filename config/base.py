from pathlib import Path

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    BASE_DOMAIN: str = "http://127.0.0.1:8000"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DB_IP: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "test"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = "123456"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()


BASE_DOMAIN = settings.BASE_DOMAIN

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


TEMP_FOLDER_PATH = BASE_DIR / "temp"

CONF_FOLDER_PATH = BASE_DIR / "config"
