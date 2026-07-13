from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import ShopMember, User, UserSession
from app.auth.service import hash_session_token
from app.core.config import get_settings
from app.core.errors import AppError
from app.db.session import get_session


@dataclass(slots=True)
class Identity:
    user: User
    role: str | None

    @property
    def is_admin(self) -> bool:
        return self.role in {"admin", "owner"}


async def _resolve_identity(
    request: Request, session: AsyncSession
) -> Identity | None:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        return None

    statement = (
        select(UserSession)
        .options(selectinload(UserSession.user).selectinload(User.membership))
        .where(
            UserSession.token_hash == hash_session_token(token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(UTC),
        )
    )
    user_session = await session.scalar(statement)
    if user_session is None or user_session.user.is_blocked:
        return None
    user_session.last_used_at = datetime.now(UTC)
    await session.commit()
    membership: ShopMember | None = user_session.user.membership
    role = membership.role if membership and membership.is_active else None
    return Identity(user=user_session.user, role=role)


async def get_optional_identity(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Identity | None:
    return await _resolve_identity(request, session)


async def get_current_identity(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Identity:
    identity = await _resolve_identity(request, session)
    if identity is None:
        raise AppError("AUTH_REQUIRED", "Потрібна авторизація", 401)
    return identity


async def require_admin(identity: Identity = Depends(get_current_identity)) -> Identity:
    if not identity.is_admin:
        raise AppError("ADMIN_ACCESS_REQUIRED", "Потрібні права адміністратора", 403)
    return identity
