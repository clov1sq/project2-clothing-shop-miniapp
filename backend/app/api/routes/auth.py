from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import write_audit
from app.auth.dependencies import Identity, get_current_identity
from app.auth.models import UserSession
from app.auth.schemas import TelegramAuthRequest, user_payload
from app.auth.service import authenticate_user, hash_session_token
from app.core.config import get_settings
from app.db.session import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/telegram")
async def telegram_auth(
    payload: TelegramAuthRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    settings = get_settings()
    user, token, expires_at = await authenticate_user(
        session,
        settings,
        payload.init_data,
        request.headers.get("user-agent"),
    )
    role = user.membership.role if user.membership and user.membership.is_active else None
    await write_audit(
        session,
        actor_user_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=str(user.id),
        payload={"telegram_id": user.telegram_id},
    )
    await session.commit()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_days * 24 * 60 * 60,
        expires=expires_at,
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax",
        path="/",
    )
    return {"ok": True, "data": {"user": user_payload(user, role)}}


@router.get("/me")
async def me(identity: Identity = Depends(get_current_identity)) -> dict[str, object]:
    return {"ok": True, "data": {"user": user_payload(identity.user, identity.role)}}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        user_session = await session.scalar(
            select(UserSession).where(UserSession.token_hash == hash_session_token(token))
        )
        if user_session:
            user_session.revoked_at = datetime.now(UTC)
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="auth.logout",
        entity_type="user",
        entity_id=str(identity.user.id),
    )
    await session.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True, "data": {"logged_out": True}}
