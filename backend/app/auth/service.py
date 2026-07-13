import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import ShopMember, User, UserSession
from app.auth.telegram import validate_init_data
from app.core.config import Settings
from app.core.errors import AppError


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def authenticate_user(
    session: AsyncSession,
    settings: Settings,
    init_data: str,
    user_agent: str | None,
) -> tuple[User, str, datetime]:
    if init_data:
        if not settings.telegram_bot_token:
            raise AppError(
                "TELEGRAM_AUTH_UNAVAILABLE",
                "На сервері не налаштовано Telegram-бота",
                503,
            )
        telegram_user = validate_init_data(
            init_data,
            settings.telegram_bot_token,
            settings.telegram_auth_max_age_seconds,
        )
    elif settings.dev_auth_enabled or settings.app_env.lower() in {"local", "test"}:
        telegram_user = {
            "id": 990001,
            "first_name": "Demo",
            "last_name": "Admin",
            "username": "demo_admin",
            "language_code": "uk",
        }
    else:
        raise AppError("TELEGRAM_AUTH_REQUIRED", "Відкрийте магазин через Telegram", 401)

    raw_telegram_id = telegram_user.get("id")
    if not isinstance(raw_telegram_id, int | str):
        raise AppError("TELEGRAM_USER_INVALID", "Telegram не передав коректний user id", 401)
    telegram_id = int(raw_telegram_id)
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=str(telegram_user["username"]) if telegram_user.get("username") else None,
            first_name=str(telegram_user.get("first_name") or "Користувач"),
            last_name=str(telegram_user["last_name"]) if telegram_user.get("last_name") else None,
            language_code=(
                str(telegram_user["language_code"]) if telegram_user.get("language_code") else None
            ),
        )
        session.add(user)
        await session.flush()
    else:
        user.username = str(telegram_user["username"]) if telegram_user.get("username") else None
        user.first_name = str(telegram_user.get("first_name") or user.first_name)
        user.last_name = str(telegram_user["last_name"]) if telegram_user.get("last_name") else None
        user.language_code = (
            str(telegram_user["language_code"]) if telegram_user.get("language_code") else None
        )

    should_be_admin = telegram_id in settings.admin_telegram_ids or (
        not init_data
        and (settings.dev_auth_enabled or settings.app_env.lower() in {"local", "test"})
    )
    if should_be_admin:
        membership = await session.scalar(select(ShopMember).where(ShopMember.user_id == user.id))
        if membership is None:
            session.add(ShopMember(user_id=user.id, role="owner", is_active=True))
        else:
            membership.is_active = True

    token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.session_ttl_days)
    session.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            created_at=now,
            expires_at=expires_at,
            last_used_at=now,
            user_agent=user_agent,
        )
    )
    await session.commit()
    await session.refresh(user, attribute_names=["membership"])
    return user, token, expires_at
