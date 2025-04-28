import datetime
from pathlib import Path

from aiogram.enums import ContentType
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytz


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra="ignore"
    )

    BOT_TOKEN: SecretStr
    GROUP_ID: int
    TOPIC_ID: int

    TIMEZONE: str

    RULES_URL: str
    
    ALLOWED_CONTENT_TYPES: list[ContentType] = [ContentType.VIDEO_NOTE, ContentType.VIDEO, ContentType.ANIMATION]

    @property
    def tzinfo(self) -> datetime.tzinfo:
        return pytz.timezone(self.TIMEZONE)


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8', 
        env_prefix="REDIS_",
        extra="ignore"    
    )

    HOST: str
    PORT: int
    DB: int = 0
    TASKIQ_DB: int

    @property
    def taskiq_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.TASKIQ_DB}"


class DbSettings(BaseSettings):
    DB: str
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="ignore"
    )

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class AdminSettings(BaseSettings):

    HOST: str
    PORT: int
    ENDPOINT: str

    SECRET_TOKEN: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    USERNAME: str
    PASSWORD: str


    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="ADMIN_",
        extra="ignore"
    )


admin_settings = AdminSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
db_settings = DbSettings()  # type: ignore
settings = Settings()  # type: ignore
