from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("")
async def meta() -> dict[str, object]:
    settings = get_settings()
    return {
        "ok": True,
        "data": {
            "shop_name": settings.shop_name,
            "version": "0.5.0",
            "features": {
                "telegram_auth": True,
                "catalog": True,
                "favorites": True,
                "cart": True,
                "checkout": True,
                "admin": True,
            },
        },
    }
