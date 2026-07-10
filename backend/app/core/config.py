from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    shop_name: str = Field(default="BlueWear", alias="SHOP_NAME")

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="BACKEND_CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://project2:project2_local_password@localhost:5432/project2",
        alias="DATABASE_URL",
    )

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str | None = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")
    mini_app_url: str = Field(default="http://localhost:5173", alias="MINI_APP_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
