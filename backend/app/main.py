from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.meta import router as meta_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="Project2 Clothing Store API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.include_router(health_router)
app.include_router(meta_router)


@app.get("/")
async def root() -> dict[str, object]:
    return {"ok": True, "service": "project2", "version": "0.1.0"}
