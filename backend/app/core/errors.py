from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, object] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    payload: dict[str, object] = {
        "ok": False,
        "error": {"code": exc.code, "message": exc.message},
    }
    if exc.details:
        payload["error"]["details"] = exc.details  # type: ignore[index]
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Перевірте введені дані",
                "details": {"fields": exc.errors()},
            },
        },
    )
