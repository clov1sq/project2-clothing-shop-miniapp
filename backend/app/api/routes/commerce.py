from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import Identity, get_current_identity
from app.commerce.schemas import CartItemCreate, CartItemUpdate
from app.commerce.service import (
    add_cart_item,
    add_favorite,
    clear_cart,
    delete_cart_item,
    get_cart,
    list_favorites,
    refresh_cart_prices,
    remove_favorite,
    serialize_cart,
    update_cart_item,
)
from app.db.session import get_session

router = APIRouter(prefix="/api/v1", tags=["favorites", "cart"])


@router.get("/favorites")
async def favorites(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=60),
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await list_favorites(session, identity.user.id, page=page, limit=limit),
    }


@router.post("/favorites/{product_id}")
async def favorite_add(
    product_id: UUID,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": await add_favorite(session, identity.user.id, product_id)}


@router.delete("/favorites/{product_id}")
async def favorite_delete(
    product_id: UUID,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": await remove_favorite(session, identity.user.id, product_id)}


@router.get("/cart")
async def cart_get(
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": serialize_cart(await get_cart(session, identity.user.id))}


@router.post("/cart/items")
async def cart_add_item(
    payload: CartItemCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await add_cart_item(
            session,
            identity.user.id,
            payload.variant_id,
            payload.quantity,
            idempotency_key or "",
        ),
    }


@router.patch("/cart/items/{item_id}")
async def cart_update_item(
    item_id: UUID,
    payload: CartItemUpdate,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await update_cart_item(session, identity.user.id, item_id, payload.quantity),
    }


@router.delete("/cart/items/{item_id}")
async def cart_delete_item(
    item_id: UUID,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await delete_cart_item(session, identity.user.id, item_id),
    }


@router.delete("/cart")
async def cart_clear(
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": await clear_cart(session, identity.user.id)}


@router.post("/cart/refresh")
async def cart_refresh(
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": await refresh_cart_prices(session, identity.user.id)}
