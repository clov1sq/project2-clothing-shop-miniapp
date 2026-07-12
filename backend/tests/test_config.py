from app.core.config import Settings


def test_cors_accepts_plain_comma_list() -> None:
    settings = Settings(BACKEND_CORS_ORIGINS="https://front.example,http://localhost:5173")
    assert settings.backend_cors_origins == ["https://front.example", "http://localhost:5173"]


def test_cors_accepts_json_like_value() -> None:
    settings = Settings(BACKEND_CORS_ORIGINS='["https://front.example"]')
    assert settings.backend_cors_origins == ["https://front.example"]


def test_admin_ids_ignore_invalid_values() -> None:
    settings = Settings(ADMIN_TELEGRAM_IDS="12, nope,34")
    assert settings.admin_telegram_ids == {12, 34}


def test_bot_token_legacy_alias_is_supported() -> None:
    settings = Settings(BOT_TOKEN="legacy-token")
    assert settings.telegram_bot_token == "legacy-token"


def test_telegram_bot_token_alias_is_supported() -> None:
    settings = Settings(TELEGRAM_BOT_TOKEN="telegram-token")
    assert settings.telegram_bot_token == "telegram-token"
