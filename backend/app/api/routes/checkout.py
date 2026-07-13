from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import Identity, get_current_identity
from app.checkout.schemas import CheckoutConfirmRequest, CheckoutValidateRequest
from app.checkout.service import confirm_checkout, get_order, validate_checkout
from app.db.session import get_session

router = APIRouter(prefix="/api/v1/checkout", tags=["checkout"])


@router.post("/validate")
async def checkout_validate(
    payload: CheckoutValidateRequest,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await validate_checkout(session, identity.user.id, payload),
    }


@router.post("/confirm")
async def checkout_confirm(
    payload: CheckoutConfirmRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {
        "ok": True,
        "data": await confirm_checkout(
            session, identity.user.id, payload, idempotency_key or ""
        ),
    }


@router.get("/orders/{order_id}")
async def checkout_order(
    order_id: UUID,
    identity: Identity = Depends(get_current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return {"ok": True, "data": await get_order(session, identity.user.id, order_id)}
