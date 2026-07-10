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
            "version": "0.1.0",
            "features": {
                "telegram_auth": False,
                "catalog": False,
                "cart": False,
                "checkout": False,
                "admin": False,
            },
        },
    }
