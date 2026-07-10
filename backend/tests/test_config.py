from app.core.config import Settings


def test_settings_parses_cors_origins() -> None:
    settings = Settings(BACKEND_CORS_ORIGINS="http://localhost:5173,http://example.com")
    assert settings.backend_cors_origins == ["http://localhost:5173", "http://example.com"]


def test_shop_name_default_is_configurable() -> None:
    settings = Settings(SHOP_NAME="DemoShop")
    assert settings.shop_name == "DemoShop"
