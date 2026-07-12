from fastapi import APIRouter

from app.core.config import get_settings
from app.db.health import check_database

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, object]:
    settings = get_settings()
    return {"ok": True, "service": "project2-backend", "env": settings.app_env, "version": "0.3.0"}


@router.get("/ready")
async def ready() -> dict[str, object]:
    await check_database()
    return {"ok": True, "database": "ok", "version": "0.3.0"}


@router.get("/db")
async def database_ready() -> dict[str, object]:
    await check_database()
    return {"ok": True, "database": "ok"}
