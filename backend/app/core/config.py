from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    shop_name: str = Field(default="BlueWear", alias="SHOP_NAME")

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    backend_cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="BACKEND_CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://project2:project2_local_password@localhost:5432/project2",
        alias="DATABASE_URL",
    )

    telegram_bot_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("TELEGRAM_BOT_TOKEN", "BOT_TOKEN"),
    )
    telegram_webhook_secret: str | None = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_auth_max_age_seconds: int = Field(default=86400, alias="TELEGRAM_AUTH_MAX_AGE_SECONDS")
    mini_app_url: str = Field(default="http://localhost:5173", alias="MINI_APP_URL")
    admin_telegram_ids_raw: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")

    session_cookie_name: str = Field(default="p2_session", alias="SESSION_COOKIE_NAME")
    session_ttl_days: int = Field(default=14, alias="SESSION_TTL_DAYS")
    dev_auth_enabled: bool = Field(default=False, alias="DEV_AUTH_ENABLED")

    media_max_size_mb: int = Field(default=10, alias="MEDIA_MAX_SIZE_MB")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def backend_cors_origins(self) -> list[str]:
        raw = self.backend_cors_origins_raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]
        return [item.strip().strip('"').strip("'") for item in raw.split(",") if item.strip()]

    @property
    def admin_telegram_ids(self) -> set[int]:
        values: set[int] = set()
        for item in self.admin_telegram_ids_raw.split(","):
            item = item.strip()
            if item:
                try:
                    values.add(int(item))
                except ValueError:
                    continue
        return values

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
