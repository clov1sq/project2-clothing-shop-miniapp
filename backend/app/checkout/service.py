import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.catalog.models import Inventory, InventoryMovement, Product, ProductVariant
from app.catalog.service import (
    money,
    product_primary_media,
    variant_effective_compare,
    variant_effective_price,
)
from app.checkout.models import InventoryReservation, Order, OrderItem
from app.checkout.schemas import CheckoutConfirmRequest, CheckoutDelivery, CheckoutValidateRequest
from app.commerce.models import CartItem, IdempotencyKey
from app.commerce.service import CART_LOAD_OPTIONS, get_cart, serialize_cart
from app.core.errors import AppError

RESERVATION_MINUTES = 15

ORDER_LOAD_OPTIONS = (
    selectinload(Order.items),
    selectinload(Order.reservations),
)


def _now() -> datetime:
    return datetime.now(UTC)


def normalize_phone(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if digits.startswith("380") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+38{digits}"
    if len(digits) == 9:
        return f"+380{digits}"
    raise AppError("CHECKOUT_CONTACT_INVALID", "Вкажіть коректний номер телефону", 422)


def delivery_payload(delivery: CheckoutDelivery) -> dict[str, str | None]:
    return {
        "method": delivery.method,
        "city": delivery.city,
        "branch": delivery.branch,
        "address": delivery.address,
    }


def _request_hash(payload: CheckoutConfirmRequest) -> str:
    encoded = json.dumps(
        payload.model_dump(mode="json"), ensure_ascii=False, sort_keys=True
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


async def reserve_inventory_quantity(
    session: AsyncSession,
    inventory_id: UUID,
    quantity: int,
    now: datetime,
) -> tuple[int, int] | None:
    """Atomically reserve stock and return available quantities before/after."""
    reserved_row = (
        await session.execute(
            update(Inventory)
            .where(
                Inventory.id == inventory_id,
                Inventory.quantity_on_hand - Inventory.quantity_reserved >= quantity,
            )
            .values(
                quantity_reserved=Inventory.quantity_reserved + quantity,
                updated_at=now,
            )
            .returning(Inventory.quantity_on_hand, Inventory.quantity_reserved)
            .execution_options(synchronize_session=False)
        )
    ).first()
    if reserved_row is None:
        return None
    quantity_on_hand, quantity_reserved = reserved_row
    return (
        quantity_on_hand - (quantity_reserved - quantity),
        quantity_on_hand - quantity_reserved,
    )


def _serialize_order(order: Order) -> dict[str, object]:
    delivery = json.loads(order.delivery_data_json or "{}")
    items = [
        {
            "id": str(item.id),
            "product_id": str(item.product_id) if item.product_id else None,
            "variant_id": str(item.variant_id) if item.variant_id else None,
            "product_name": item.product_name,
            "brand": item.brand_name,
            "product_slug": item.product_slug,
            "sku": item.sku,
            "color": item.color_name,
            "size": item.size_name,
            "unit_price": money(item.unit_price),
            "compare_at_price": money(item.compare_at_price),
            "quantity": item.quantity,
            "subtotal": money(item.subtotal),
            "image_url": item.image_url,
        }
        for item in order.items
    ]
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "status": order.status,
        "payment_status": order.payment_status,
        "delivery_status": order.delivery_status,
        "currency": order.currency,
        "subtotal": money(order.subtotal),
        "discount_total": money(order.discount_total),
        "delivery_total": money(order.delivery_total),
        "grand_total": money(order.grand_total),
        "contact": {
            "first_name": order.first_name,
            "last_name": order.last_name,
            "phone": order.phone,
            "email": order.email,
            "comment": order.comment,
        },
        "delivery": delivery,
        "reservation_expires_at": order.reservation_expires_at.isoformat(),
        "created_at": order.created_at.isoformat(),
        "items": items,
    }


def _cart_issues(cart_payload: dict[str, object]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    raw_items = cart_payload.get("items", [])
    if not isinstance(raw_items, list):
        return issues
    for raw_item in raw_items:
        item = raw_item if isinstance(raw_item, dict) else {}
        if item.get("price_changed"):
            issues.append(
                {
                    "item_id": item.get("id"),
                    "code": "CHECKOUT_PRICE_CHANGED",
                    "message": "Ціна товару змінилася. Підтвердьте нову ціну в кошику.",
                }
            )
        if not item.get("is_available", False):
            issues.append(
                {
                    "item_id": item.get("id"),
                    "code": item.get("unavailable_reason") or "CHECKOUT_ITEM_UNAVAILABLE",
                    "message": item.get("unavailable_message") or "Товар недоступний",
                }
            )
    return issues


async def validate_checkout(
    session: AsyncSession, user_id: UUID, payload: CheckoutValidateRequest
) -> dict[str, object]:
    cart = await get_cart(session, user_id)
    cart_payload = serialize_cart(cart)
    if not cart or not cart.items:
        raise AppError("CHECKOUT_CART_EMPTY", "Кошик порожній", 409)
    issues = _cart_issues(cart_payload)
    if issues:
        raise AppError(
            "CHECKOUT_CART_INVALID",
            "У кошику є позиції, які потрібно перевірити",
            409,
            {"issues": issues, "cart": cart_payload},
        )
    contact = payload.contact.model_dump() if payload.contact else None
    if contact:
        contact["phone"] = normalize_phone(str(contact["phone"]))
    return {
        "valid": True,
        "cart": cart_payload,
        "contact": contact,
        "delivery": delivery_payload(payload.delivery) if payload.delivery else None,
        "reservation_minutes": RESERVATION_MINUTES,
    }


async def _claim_idempotency(
    session: AsyncSession, user_id: UUID, key: str, request_hash: str
) -> tuple[IdempotencyKey, dict[str, object] | None]:
    if not key or len(key) > 120:
        raise AppError("IDEMPOTENCY_KEY_REQUIRED", "Потрібен Idempotency-Key", 400)
    existing = await session.scalar(
        select(IdempotencyKey)
        .where(IdempotencyKey.user_id == user_id, IdempotencyKey.key == key)
        .with_for_update()
    )
    if existing:
        if existing.operation != "checkout.confirm" or existing.request_hash != request_hash:
            raise AppError("IDEMPOTENCY_CONFLICT", "Ключ уже використано для іншого запиту", 409)
        if existing.response_json:
            return existing, json.loads(existing.response_json)
        raise AppError("IDEMPOTENCY_CONFLICT", "Запит уже виконується", 409)
    record = IdempotencyKey(
        user_id=user_id,
        key=key,
        operation="checkout.confirm",
        request_hash=request_hash,
        created_at=_now(),
    )
    session.add(record)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise AppError("IDEMPOTENCY_CONFLICT", "Запит уже виконується", 409) from exc
    return record, None


async def confirm_checkout(
    session: AsyncSession,
    user_id: UUID,
    payload: CheckoutConfirmRequest,
    idempotency_key: str,
) -> dict[str, object]:
    phone = normalize_phone(payload.contact.phone)
    request_hash = _request_hash(payload)
    idempotency, cached = await _claim_idempotency(session, user_id, idempotency_key, request_hash)
    if cached is not None:
        return cached

    cart = await get_cart(session, user_id, lock=True)
    if cart is None:
        raise AppError("CHECKOUT_CART_EMPTY", "Кошик порожній", 409)
    locked_cart_items = list(
        (
            await session.scalars(
                select(CartItem)
                .where(CartItem.cart_id == cart.id)
                .order_by(CartItem.id)
                .with_for_update()
            )
        ).all()
    )
    if not locked_cart_items:
        raise AppError("CHECKOUT_CART_EMPTY", "Кошик порожній", 409)

    variant_ids = sorted({item.variant_id for item in locked_cart_items}, key=str)
    locked_inventory = list(
        (
            await session.scalars(
                select(Inventory)
                .where(Inventory.variant_id.in_(variant_ids))
                .order_by(Inventory.variant_id)
                .with_for_update()
            )
        ).all()
    )
    inventory_by_variant = {inventory.variant_id: inventory for inventory in locked_inventory}
    await session.refresh(cart, attribute_names=["items"])
    for item in cart.items:
        await session.refresh(item, attribute_names=["variant"])
    # Load the same complete cart graph after locks were acquired.
    cart = await session.scalar(
        select(type(cart))
        .options(*CART_LOAD_OPTIONS)
        .where(type(cart).id == cart.id)
        .execution_options(populate_existing=True)
    )
    if cart is None:
        raise AppError("CHECKOUT_CART_EMPTY", "Кошик порожній", 409)

    cart_payload = serialize_cart(cart)
    issues = _cart_issues(cart_payload)
    if issues:
        raise AppError(
            "CHECKOUT_CART_INVALID",
            "У кошику є позиції, які потрібно перевірити",
            409,
            {"issues": issues, "cart": cart_payload},
        )

    now = _now()
    expires_at = now + timedelta(minutes=RESERVATION_MINUTES)
    subtotal = Decimal("0")
    discount_total = Decimal("0")
    order_items: list[OrderItem] = []
    reservations: list[InventoryReservation] = []
    currency = "UAH"

    for item in cart.items:
        variant: ProductVariant = item.variant
        product: Product = variant.product
        inventory = inventory_by_variant.get(variant.id)
        available = inventory.available_quantity if inventory else 0
        if available < item.quantity:
            raise AppError(
                "CHECKOUT_INSUFFICIENT_STOCK",
                f"Недостатньо товару «{product.name}»",
                409,
                {"item_id": str(item.id), "available_quantity": available},
            )
        current_price = variant_effective_price(product, variant)
        if current_price != item.unit_price_snapshot:
            raise AppError(
                "CHECKOUT_PRICE_CHANGED",
                f"Ціна товару «{product.name}» змінилася",
                409,
                {"item_id": str(item.id), "current_price": money(current_price)},
            )
        compare_at = variant_effective_compare(product, variant)
        line_subtotal = current_price * item.quantity
        subtotal += line_subtotal
        if compare_at and compare_at > current_price:
            discount_total += (compare_at - current_price) * item.quantity
        currency = product.currency
        media = next(
            (
                media
                for media in sorted(
                    product.media, key=lambda value: (not value.is_primary, value.sort_order)
                )
                if media.variant_id in {None, variant.id}
            ),
            product_primary_media(product),
        )
        order_items.append(
            OrderItem(
                product_id=product.id,
                variant_id=variant.id,
                product_name=product.name,
                brand_name=product.brand.name,
                product_slug=product.slug,
                sku=variant.sku,
                color_name=variant.color.name,
                size_name=variant.size.name,
                unit_price=current_price,
                compare_at_price=compare_at,
                quantity=item.quantity,
                subtotal=line_subtotal,
                image_url=media.url if media else None,
                created_at=now,
            )
        )

    order = Order(
        order_number=f"BW-{now:%Y%m%d}-{uuid4().hex[:8].upper()}",
        user_id=user_id,
        status="awaiting_payment",
        payment_status="not_started",
        delivery_status="not_created",
        currency=currency,
        subtotal=subtotal,
        discount_total=discount_total,
        delivery_total=Decimal("0"),
        grand_total=subtotal,
        first_name=payload.contact.first_name,
        last_name=payload.contact.last_name,
        phone=phone,
        email=payload.contact.email,
        comment=payload.contact.comment,
        delivery_method=payload.delivery.method,
        delivery_data_json=json.dumps(delivery_payload(payload.delivery), ensure_ascii=False),
        reservation_expires_at=expires_at,
    )
    session.add(order)
    await session.flush()

    for order_item, cart_item in zip(order_items, cart.items, strict=True):
        order_item.order_id = order.id
        session.add(order_item)
        inventory = inventory_by_variant[cart_item.variant_id]
        availability = await reserve_inventory_quantity(
            session, inventory.id, cart_item.quantity, now
        )
        if availability is None:
            raise AppError(
                "CHECKOUT_INSUFFICIENT_STOCK",
                f"Недостатньо товару «{cart_item.variant.product.name}»",
                409,
                {"item_id": str(cart_item.id), "available_quantity": 0},
            )
        before_available, after_available = availability
        inventory.quantity_reserved = inventory.quantity_on_hand - after_available
        inventory.updated_at = now
        reservation = InventoryReservation(
            order_id=order.id,
            variant_id=cart_item.variant_id,
            quantity=cart_item.quantity,
            status="active",
            expires_at=expires_at,
            created_at=now,
        )
        session.add(reservation)
        reservations.append(reservation)
        session.add(
            InventoryMovement(
                variant_id=cart_item.variant_id,
                movement_type="reservation",
                quantity_delta=-cart_item.quantity,
                quantity_before=before_available,
                quantity_after=after_available,
                reason=f"Резерв для замовлення {order.order_number}",
                created_by_user_id=user_id,
                created_at=now,
            )
        )

    await session.flush()
    await session.refresh(order, attribute_names=["items", "reservations"])
    response = _serialize_order(order)
    idempotency.response_json = json.dumps(response, ensure_ascii=False)
    idempotency.status_code = 200
    # Cart cleanup is part of the same atomic transaction and becomes visible only on commit.
    await session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
    await session.commit()
    return response


async def get_order(session: AsyncSession, user_id: UUID, order_id: UUID) -> dict[str, object]:
    order = await session.scalar(
        select(Order)
        .options(*ORDER_LOAD_OPTIONS)
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    if order is None:
        raise AppError("ORDER_NOT_FOUND", "Замовлення не знайдено", 404)
    return _serialize_order(order)


async def expire_reservations(session: AsyncSession, *, now: datetime | None = None) -> int:
    current = now or _now()
    reservations = list(
        (
            await session.scalars(
                select(InventoryReservation)
                .where(
                    InventoryReservation.status == "active",
                    InventoryReservation.expires_at <= current,
                )
                .order_by(InventoryReservation.expires_at, InventoryReservation.id)
                .with_for_update(skip_locked=True)
            )
        ).all()
    )
    if not reservations:
        return 0

    variant_ids = sorted({reservation.variant_id for reservation in reservations}, key=str)
    inventories = list(
        (
            await session.scalars(
                select(Inventory)
                .where(Inventory.variant_id.in_(variant_ids))
                .order_by(Inventory.variant_id)
                .with_for_update()
            )
        ).all()
    )
    inventory_by_variant = {inventory.variant_id: inventory for inventory in inventories}
    order_ids: set[UUID] = set()
    processed = 0
    for reservation in reservations:
        if reservation.status != "active":
            continue
        inventory = inventory_by_variant.get(reservation.variant_id)
        if inventory is None:
            continue
        before_available = inventory.available_quantity
        inventory.quantity_reserved = max(0, inventory.quantity_reserved - reservation.quantity)
        inventory.updated_at = current
        reservation.status = "expired"
        reservation.released_at = current
        order_ids.add(reservation.order_id)
        processed += 1
        session.add(
            InventoryMovement(
                variant_id=reservation.variant_id,
                movement_type="reservation_release",
                quantity_delta=reservation.quantity,
                quantity_before=before_available,
                quantity_after=inventory.available_quantity,
                reason=f"Автоматичне завершення резерву {reservation.order_id}",
                created_by_user_id=None,
                created_at=current,
            )
        )

    if order_ids:
        orders = list(
            (
                await session.scalars(
                    select(Order).where(Order.id.in_(order_ids)).with_for_update()
                )
            ).all()
        )
        for order in orders:
            if order.status == "awaiting_payment":
                order.status = "expired"
                order.payment_status = "cancelled"
    await session.commit()
    return processed
