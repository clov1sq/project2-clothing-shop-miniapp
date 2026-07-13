import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.catalog.models import Product, ProductVariant
from app.catalog.service import (
    PRODUCT_LOAD_OPTIONS,
    discount_percent,
    money,
    product_primary_media,
    serialize_product_card,
    variant_effective_compare,
    variant_effective_price,
)
from app.commerce.models import Cart, CartItem, Favorite, IdempotencyKey
from app.core.errors import AppError

MAX_VARIANT_QUANTITY = 10

CART_LOAD_OPTIONS = (
    selectinload(Cart.items)
    .selectinload(CartItem.variant)
    .selectinload(ProductVariant.product)
    .selectinload(Product.category),
    selectinload(Cart.items)
    .selectinload(CartItem.variant)
    .selectinload(ProductVariant.product)
    .selectinload(Product.brand),
    selectinload(Cart.items)
    .selectinload(CartItem.variant)
    .selectinload(ProductVariant.product)
    .selectinload(Product.media),
    selectinload(Cart.items).selectinload(CartItem.variant).selectinload(ProductVariant.color),
    selectinload(Cart.items).selectinload(CartItem.variant).selectinload(ProductVariant.size),
    selectinload(Cart.items).selectinload(CartItem.variant).selectinload(ProductVariant.inventory),
)


def _now() -> datetime:
    return datetime.now(UTC)


def _is_public_product(product: Product) -> bool:
    return (
        product.status == "active"
        and product.archived_at is None
        and product.published_at is not None
        and product.category.is_active
        and product.brand.is_active
    )


def _variant_unavailable_reason(variant: ProductVariant) -> tuple[str | None, str | None]:
    product = variant.product
    if not _is_public_product(product):
        return "CART_ITEM_UNAVAILABLE", "Товар більше недоступний"
    if not variant.is_active or variant.archived_at is not None:
        return "VARIANT_NOT_ACTIVE", "Обраний варіант більше недоступний"
    available = variant.inventory.available_quantity if variant.inventory else 0
    if available <= 0:
        return "VARIANT_OUT_OF_STOCK", "Немає в наявності"
    return None, None


def _available_quantity(variant: ProductVariant) -> int:
    if not _is_public_product(variant.product):
        return 0
    if not variant.is_active or variant.archived_at is not None:
        return 0
    return max(0, variant.inventory.available_quantity if variant.inventory else 0)


def serialize_cart(cart: Cart | None) -> dict[str, object]:
    if cart is None:
        return {
            "id": None,
            "items": [],
            "total_quantity": 0,
            "subtotal": "0.00",
            "discount_total": "0.00",
            "grand_total": "0.00",
            "currency": "UAH",
            "has_issues": False,
        }

    items_payload: list[dict[str, object]] = []
    subtotal = Decimal("0")
    discount_total = Decimal("0")
    total_quantity = 0
    has_issues = False
    currency = "UAH"

    for item in sorted(cart.items, key=lambda value: value.created_at):
        variant = item.variant
        product = variant.product
        currency = product.currency
        available = _available_quantity(variant)
        max_quantity = min(MAX_VARIANT_QUANTITY, available)
        reason_code, reason_message = _variant_unavailable_reason(variant)
        if reason_code is None and item.quantity > max_quantity:
            reason_code = "CART_QUANTITY_EXCEEDS_STOCK"
            reason_message = f"Доступно лише {max_quantity} шт."
        current_price = variant_effective_price(product, variant)
        compare_at = variant_effective_compare(product, variant)
        price_changed = current_price != item.unit_price_snapshot
        line_subtotal = current_price * item.quantity
        subtotal += line_subtotal
        if compare_at is not None and compare_at > current_price:
            discount_total += (compare_at - current_price) * item.quantity
        total_quantity += item.quantity
        has_issues = has_issues or reason_code is not None
        media = next(
            (
                value
                for value in sorted(product.media, key=lambda media_item: (not media_item.is_primary, media_item.sort_order))
                if value.variant_id in {None, variant.id}
            ),
            product_primary_media(product),
        )
        items_payload.append(
            {
                "id": str(item.id),
                "variant_id": str(variant.id),
                "product_id": str(product.id),
                "product_slug": product.slug,
                "product_name": product.name,
                "brand": product.brand.name,
                "color": {"name": variant.color.name, "code": variant.color.code},
                "size": {"name": variant.size.name, "code": variant.size.code},
                "sku": variant.sku,
                "image_url": media.url if media else None,
                "quantity": item.quantity,
                "unit_price": money(current_price),
                "unit_price_snapshot": money(item.unit_price_snapshot),
                "old_price": money(compare_at),
                "discount_percent": discount_percent(current_price, compare_at),
                "subtotal": money(line_subtotal),
                "available_quantity": available,
                "max_quantity": max_quantity,
                "is_available": reason_code is None,
                "price_changed": price_changed,
                "unavailable_reason": reason_code,
                "unavailable_message": reason_message,
            }
        )

    return {
        "id": str(cart.id),
        "items": items_payload,
        "total_quantity": total_quantity,
        "subtotal": money(subtotal),
        "discount_total": money(discount_total),
        "grand_total": money(subtotal),
        "currency": currency,
        "has_issues": has_issues,
    }


async def favorite_product_ids(
    session: AsyncSession, user_id: UUID, product_ids: list[UUID]
) -> set[UUID]:
    if not product_ids:
        return set()
    values = await session.scalars(
        select(Favorite.product_id).where(
            Favorite.user_id == user_id, Favorite.product_id.in_(product_ids)
        )
    )
    return set(values.all())


async def list_favorites(
    session: AsyncSession, user_id: UUID, page: int, limit: int
) -> dict[str, object]:
    statement = (
        select(Favorite)
        .options(selectinload(Favorite.product).options(*PRODUCT_LOAD_OPTIONS))
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    favorites = list((await session.scalars(statement)).unique().all())
    from sqlalchemy import func

    total = int(
        await session.scalar(select(func.count(Favorite.id)).where(Favorite.user_id == user_id))
        or 0
    )
    items: list[dict[str, object]] = []
    for favorite in favorites:
        product = favorite.product
        payload = serialize_product_card(product, is_favorite=True)
        available = _is_public_product(product)
        payload.update(
            {
                "favorite_created_at": favorite.created_at.isoformat(),
                "is_active": available,
                "unavailable_message": None if available else "Товар більше недоступний",
            }
        )
        items.append(payload)
    return {
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
            "has_next": page * limit < total,
        },
    }


async def add_favorite(session: AsyncSession, user_id: UUID, product_id: UUID) -> dict[str, object]:
    product = await session.scalar(
        select(Product).options(*PRODUCT_LOAD_OPTIONS).where(Product.id == product_id)
    )
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "Товар не знайдено", 404)
    if not _is_public_product(product):
        raise AppError("PRODUCT_NOT_ACTIVE", "Цей товар зараз недоступний", 409)
    existing = await session.scalar(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    if existing is None:
        session.add(Favorite(user_id=user_id, product_id=product_id, created_at=_now()))
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
    return {"product_id": str(product_id), "is_favorite": True}


async def remove_favorite(
    session: AsyncSession, user_id: UUID, product_id: UUID
) -> dict[str, object]:
    await session.execute(
        delete(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    await session.commit()
    return {"product_id": str(product_id), "is_favorite": False}


async def get_cart(session: AsyncSession, user_id: UUID, *, lock: bool = False) -> Cart | None:
    statement = (
        select(Cart)
        .options(*CART_LOAD_OPTIONS)
        .where(Cart.user_id == user_id)
        .execution_options(populate_existing=True)
    )
    if lock:
        statement = statement.with_for_update()
    return await session.scalar(statement)


async def _get_or_create_cart(session: AsyncSession, user_id: UUID) -> Cart:
    cart = await get_cart(session, user_id, lock=True)
    if cart is not None:
        return cart
    cart = Cart(user_id=user_id)
    try:
        async with session.begin_nested():
            session.add(cart)
            await session.flush()
    except IntegrityError:
        existing = await get_cart(session, user_id, lock=True)
        if existing is None:
            raise
        return existing
    return cart


async def _load_variant(session: AsyncSession, variant_id: UUID, *, lock: bool = False) -> ProductVariant:
    statement = (
        select(ProductVariant)
        .options(
            selectinload(ProductVariant.product).selectinload(Product.category),
            selectinload(ProductVariant.product).selectinload(Product.brand),
            selectinload(ProductVariant.product).selectinload(Product.media),
            selectinload(ProductVariant.color),
            selectinload(ProductVariant.size),
            selectinload(ProductVariant.inventory),
        )
        .where(ProductVariant.id == variant_id)
    )
    if lock:
        statement = statement.with_for_update()
    variant = await session.scalar(statement)
    if variant is None:
        raise AppError("VARIANT_NOT_FOUND", "Варіант товару не знайдено", 404)
    return variant


def _validate_variant_for_cart(variant: ProductVariant, requested_quantity: int) -> int:
    if requested_quantity < 1 or requested_quantity > MAX_VARIANT_QUANTITY:
        raise AppError(
            "CART_QUANTITY_INVALID",
            f"Кількість має бути від 1 до {MAX_VARIANT_QUANTITY}",
            422,
        )
    if not _is_public_product(variant.product):
        raise AppError("CART_ITEM_UNAVAILABLE", "Товар більше недоступний", 409)
    if not variant.is_active or variant.archived_at is not None:
        raise AppError("VARIANT_NOT_ACTIVE", "Варіант товару неактивний", 409)
    available = _available_quantity(variant)
    if available <= 0:
        raise AppError("VARIANT_OUT_OF_STOCK", "Цього варіанта немає в наявності", 409)
    maximum = min(MAX_VARIANT_QUANTITY, available)
    if requested_quantity < 1 or requested_quantity > maximum:
        raise AppError(
            "CART_QUANTITY_EXCEEDS_STOCK",
            f"Можна додати не більше {maximum} шт.",
            409,
            {"max_quantity": maximum, "available_quantity": available},
        )
    return maximum


def _request_hash(operation: str, payload: dict[str, object]) -> str:
    encoded = json.dumps({"operation": operation, "payload": payload}, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


async def _claim_idempotency(
    session: AsyncSession,
    user_id: UUID,
    key: str,
    operation: str,
    payload: dict[str, object],
) -> tuple[IdempotencyKey, dict[str, object] | None]:
    if not key or len(key) > 120:
        raise AppError("IDEMPOTENCY_KEY_REQUIRED", "Потрібен коректний Idempotency-Key", 400)
    request_hash = _request_hash(operation, payload)
    existing = await session.scalar(
        select(IdempotencyKey).where(IdempotencyKey.user_id == user_id, IdempotencyKey.key == key)
    )
    if existing is not None:
        if existing.operation != operation or existing.request_hash != request_hash:
            raise AppError("IDEMPOTENCY_CONFLICT", "Цей ключ уже використано для іншої дії", 409)
        if existing.response_json:
            return existing, json.loads(existing.response_json)
        raise AppError("IDEMPOTENCY_CONFLICT", "Такий запит уже виконується", 409)

    record = IdempotencyKey(
        user_id=user_id,
        key=key,
        operation=operation,
        request_hash=request_hash,
        created_at=_now(),
    )
    try:
        async with session.begin_nested():
            session.add(record)
            await session.flush()
    except IntegrityError as exc:
        concurrent = await session.scalar(
            select(IdempotencyKey).where(
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == key,
            )
        )
        if concurrent is not None:
            if concurrent.operation != operation or concurrent.request_hash != request_hash:
                raise AppError(
                    "IDEMPOTENCY_CONFLICT",
                    "Цей ключ уже використано для іншої дії",
                    409,
                ) from exc
            if concurrent.response_json:
                return concurrent, json.loads(concurrent.response_json)
        raise AppError("IDEMPOTENCY_CONFLICT", "Такий запит уже виконується", 409) from exc
    return record, None


async def add_cart_item(
    session: AsyncSession,
    user_id: UUID,
    variant_id: UUID,
    quantity: int,
    idempotency_key: str,
) -> dict[str, object]:
    record, cached = await _claim_idempotency(
        session,
        user_id,
        idempotency_key,
        "cart.add",
        {"variant_id": str(variant_id), "quantity": quantity},
    )
    if cached is not None:
        return cached

    variant = await _load_variant(session, variant_id, lock=True)
    cart = await _get_or_create_cart(session, user_id)
    existing = await session.scalar(
        select(CartItem)
        .where(CartItem.cart_id == cart.id, CartItem.variant_id == variant_id)
        .with_for_update()
    )
    target_quantity = quantity + (existing.quantity if existing else 0)
    _validate_variant_for_cart(variant, target_quantity)
    current_price = variant_effective_price(variant.product, variant)
    if existing is None:
        session.add(
            CartItem(
                cart_id=cart.id,
                variant_id=variant_id,
                quantity=target_quantity,
                unit_price_snapshot=current_price,
            )
        )
    else:
        existing.quantity = target_quantity
        existing.unit_price_snapshot = current_price
    await session.flush()
    refreshed_cart = await get_cart(session, user_id)
    payload = serialize_cart(refreshed_cart)
    record.response_json = json.dumps(payload)
    record.status_code = 200
    await session.commit()
    return payload


async def update_cart_item(
    session: AsyncSession, user_id: UUID, item_id: UUID, quantity: int
) -> dict[str, object]:
    cart = await get_cart(session, user_id, lock=True)
    if cart is None:
        raise AppError("CART_ITEM_NOT_FOUND", "Позицію кошика не знайдено", 404)
    item = await session.scalar(
        select(CartItem)
        .where(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .with_for_update()
    )
    if item is None:
        raise AppError("CART_ITEM_NOT_FOUND", "Позицію кошика не знайдено", 404)
    variant = await _load_variant(session, item.variant_id, lock=True)
    _validate_variant_for_cart(variant, quantity)
    item.quantity = quantity
    item.unit_price_snapshot = variant_effective_price(variant.product, variant)
    await session.commit()
    return serialize_cart(await get_cart(session, user_id))


async def delete_cart_item(
    session: AsyncSession, user_id: UUID, item_id: UUID
) -> dict[str, object]:
    cart = await get_cart(session, user_id)
    if cart is None:
        return serialize_cart(None)
    await session.execute(
        delete(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    await session.commit()
    return serialize_cart(await get_cart(session, user_id))


async def clear_cart(session: AsyncSession, user_id: UUID) -> dict[str, object]:
    cart = await get_cart(session, user_id)
    if cart is None:
        return serialize_cart(None)
    await session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
    await session.commit()
    return serialize_cart(await get_cart(session, user_id))


async def refresh_cart_prices(session: AsyncSession, user_id: UUID) -> dict[str, object]:
    cart = await get_cart(session, user_id, lock=True)
    if cart is None:
        return serialize_cart(None)
    for item in cart.items:
        item.unit_price_snapshot = variant_effective_price(item.variant.product, item.variant)
    await session.commit()
    return serialize_cart(await get_cart(session, user_id))
