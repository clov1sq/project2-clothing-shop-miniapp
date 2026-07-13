import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.checkout import router as checkout_router
from app.api.routes.commerce import router as commerce_router
from app.api.routes.health import router as health_router
from app.api.routes.meta import router as meta_router
from app.checkout.worker import reservation_expiry_loop
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, validation_error_handler
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    stop_event = asyncio.Event()
    worker = asyncio.create_task(reservation_expiry_loop(stop_event), name="reservation-expiry")
    try:
        yield
    finally:
        stop_event.set()
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)


app = FastAPI(title="Project2 Fashion Store API", version="0.5.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Idempotency-Key"],
)

app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
app.include_router(health_router)
app.include_router(meta_router)
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(commerce_router)
app.include_router(checkout_router)
app.include_router(admin_router)


@app.get("/")
async def root() -> dict[str, object]:
    return {"ok": True, "service": "project2", "version": "0.5.0"}
