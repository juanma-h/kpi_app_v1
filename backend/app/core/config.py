from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ruta absoluta al archivo .env en la raíz de /backend
BASE_DIR = Path(__file__).resolve().parents[2]   # app/core -> app -> backend
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8")

    DATABASE_URL: str
    JWT_SECRET: str = "change_this_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 60


settings = Settings()
