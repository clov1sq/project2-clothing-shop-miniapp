from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.auth.models import UserSession
from app.auth.service import hash_session_token
from app.core.config import get_settings
from app.db.session import get_session
from app.main import app


@pytest.fixture
def production_auth_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEV_AUTH_ENABLED", "true")
    monkeypatch.setenv("SESSION_COOKIE_NAME", "project2_session")
    monkeypatch.setenv("SESSION_TTL_DAYS", "14")
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


async def _auth_client(session_maker):
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://backend.test",
        headers={"Origin": "https://frontend.test"},
    )


@pytest.mark.asyncio
async def test_cookie_session_reaches_me_cart_and_favorites(
    session_maker,
    production_auth_settings,
) -> None:
    async with await _auth_client(session_maker) as client:
        login = await client.post("/api/v1/auth/telegram", json={"init_data": ""})
        assert login.status_code == 200

        set_cookie = login.headers.get("set-cookie", "")
        assert "project2_session=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "Secure" in set_cookie
        assert "SameSite=none" in set_cookie
        assert "Path=/" in set_cookie
        assert "Domain=" not in set_cookie

        me = await client.get("/api/v1/auth/me")
        token = client.cookies.get("project2_session")
        assert token
        async with session_maker() as session:
            stored = await session.scalar(
                select(UserSession).where(UserSession.token_hash == hash_session_token(token))
            )
            assert stored is not None
            assert stored.last_used_at is not None
        cart = await client.get("/api/v1/cart")
        favorites = await client.get("/api/v1/favorites")

        assert me.status_code == 200
        assert cart.status_code == 200
        assert favorites.status_code == 200
        assert cart.json()["data"]["items"] == []
        assert favorites.json()["data"]["items"] == []

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_protected_request_without_cookie_is_unauthorized(
    session_maker,
    production_auth_settings,
) -> None:
    async with await _auth_client(session_maker) as client:
        assert (await client.get("/api/v1/auth/me")).status_code == 401
        assert (await client.get("/api/v1/cart")).status_code == 401
        assert (await client.get("/api/v1/favorites")).status_code == 401

    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["expired", "revoked"])
async def test_expired_or_revoked_session_is_unauthorized(
    session_maker,
    production_auth_settings,
    state: str,
) -> None:
    async with await _auth_client(session_maker) as client:
        login = await client.post("/api/v1/auth/telegram", json={"init_data": ""})
        assert login.status_code == 200
        token = client.cookies.get("project2_session")
        assert token

        async with session_maker() as session:
            stored = await session.scalar(
                select(UserSession).where(UserSession.token_hash == hash_session_token(token))
            )
            assert stored is not None
            if state == "expired":
                stored.expires_at = datetime.now(UTC) - timedelta(minutes=1)
            else:
                stored.revoked_at = datetime.now(UTC)
            await session.commit()

        assert (await client.get("/api/v1/auth/me")).status_code == 401

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_logout_revokes_session_and_clears_cookie(
    session_maker,
    production_auth_settings,
) -> None:
    async with await _auth_client(session_maker) as client:
        login = await client.post("/api/v1/auth/telegram", json={"init_data": ""})
        assert login.status_code == 200
        token = client.cookies.get("project2_session")
        assert token

        logout = await client.post("/api/v1/auth/logout")
        assert logout.status_code == 200
        assert "project2_session=" in logout.headers.get("set-cookie", "")
        assert client.cookies.get("project2_session") is None
        assert (await client.get("/api/v1/auth/me")).status_code == 401

        async with session_maker() as session:
            stored = await session.scalar(
                select(UserSession).where(UserSession.token_hash == hash_session_token(token))
            )
            assert stored is not None
            assert stored.revoked_at is not None

    app.dependency_overrides.clear()
