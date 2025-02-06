from os import getenv

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

load_dotenv(getenv("ENV_FILE", ".env"), override=True)


class Settings(BaseSettings):
    """Application Settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    DEBUG: bool = False
    PROJECT_NAME: str = "smart-room"
    VERSION: str = "0.0.1"
    DESCRIPTION:str = "Sistema de gerenciamento de salas de reuniões"

    LOG_LEVEL: str = "INFO"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"


settings = Settings()
