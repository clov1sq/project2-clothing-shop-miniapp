from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.catalog.models import Inventory, InventoryMovement, Product
from app.checkout.models import InventoryReservation, Order, OrderItem
from app.checkout.service import expire_reservations, normalize_phone

CONTACT = {
    "first_name": "Іван",
    "last_name": "Петренко",
    "phone": "067 123 45 67",
    "email": "ivan@example.com",
    "comment": "Зателефонуйте перед видачею",
}
DELIVERY = {"method": "branch", "city": "Львів", "branch": "Відділення №3", "address": None}


async def add_item(client, variant_id, *, key="checkout-cart", quantity=1):
    return await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant_id), "quantity": quantity},
        headers={"Idempotency-Key": key},
    )


@pytest.mark.asyncio
async def test_checkout_validate_confirm_snapshot_and_idempotency(
    client, catalog_data, db, admin_identity
):
    variant = catalog_data["variants"][0]
    product = catalog_data["product"]
    added = await add_item(client, variant.id)
    assert added.status_code == 200

    validation = await client.post("/api/v1/checkout/validate", json={})
    assert validation.status_code == 200
    assert validation.json()["data"]["valid"] is True

    payload = {"contact": CONTACT, "delivery": DELIVERY}
    confirmed = await client.post(
        "/api/v1/checkout/confirm",
        json=payload,
        headers={"Idempotency-Key": "checkout-confirm-1"},
    )
    assert confirmed.status_code == 200, confirmed.text
    order_data = confirmed.json()["data"]
    assert order_data["status"] == "awaiting_payment"
    assert order_data["contact"]["phone"] == "+380671234567"
    assert order_data["items"][0]["product_name"] == product.name
    assert order_data["items"][0]["sku"] == variant.sku

    repeated = await client.post(
        "/api/v1/checkout/confirm",
        json=payload,
        headers={"Idempotency-Key": "checkout-confirm-1"},
    )
    assert repeated.status_code == 200
    assert repeated.json()["data"]["id"] == order_data["id"]

    orders = (await db.scalars(select(Order))).all()
    items = (await db.scalars(select(OrderItem))).all()
    reservations = (await db.scalars(select(InventoryReservation))).all()
    assert len(orders) == 1
    assert len(items) == 1
    assert len(reservations) == 1
    assert reservations[0].status == "active"

    inventory = await db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    assert inventory is not None
    assert inventory.quantity_reserved == 2
    cart = await client.get("/api/v1/cart")
    assert cart.json()["data"]["items"] == []

    detail = await client.get(f"/api/v1/checkout/orders/{order_data['id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["order_number"] == order_data["order_number"]


@pytest.mark.asyncio
async def test_checkout_rejects_empty_price_change_and_insufficient_stock(client, catalog_data, db):
    empty = await client.post("/api/v1/checkout/validate", json={})
    assert empty.status_code == 409
    assert empty.json()["error"]["code"] == "CHECKOUT_CART_EMPTY"

    variant = catalog_data["variants"][0]
    product: Product = catalog_data["product"]
    await add_item(client, variant.id, key="price-cart")
    product.base_price = Decimal("2999.00")
    await db.commit()

    price = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "price-confirm"},
    )
    assert price.status_code == 409
    assert price.json()["error"]["code"] in {"CHECKOUT_CART_INVALID", "CHECKOUT_PRICE_CHANGED"}

    await client.post("/api/v1/cart/refresh")
    inventory = await db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    assert inventory is not None
    inventory.quantity_on_hand = inventory.quantity_reserved
    await db.commit()
    stock = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "stock-confirm"},
    )
    assert stock.status_code == 409
    assert stock.json()["error"]["code"] in {"CHECKOUT_CART_INVALID", "CHECKOUT_INSUFFICIENT_STOCK"}


@pytest.mark.asyncio
async def test_checkout_idempotency_conflict(client, catalog_data):
    variant = catalog_data["variants"][0]
    await add_item(client, variant.id, key="conflict-cart")
    first = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "checkout-conflict"},
    )
    assert first.status_code == 200
    changed = {**CONTACT, "comment": "Інший payload"}
    conflict = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": changed, "delivery": DELIVERY},
        headers={"Idempotency-Key": "checkout-conflict"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


@pytest.mark.asyncio
async def test_reservation_expiry_is_idempotent(client, catalog_data, db):
    variant = catalog_data["variants"][0]
    await add_item(client, variant.id, key="expiry-cart")
    response = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "expiry-confirm"},
    )
    assert response.status_code == 200
    reservation = await db.scalar(select(InventoryReservation))
    order = await db.scalar(select(Order))
    inventory = await db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    assert reservation and order and inventory
    reserved_before = inventory.quantity_reserved

    first = await expire_reservations(db, now=reservation.expires_at + timedelta(seconds=1))
    second = await expire_reservations(db, now=reservation.expires_at + timedelta(minutes=1))
    await db.refresh(reservation)
    await db.refresh(order)
    await db.refresh(inventory)
    assert first == 1
    assert second == 0
    assert reservation.status == "expired"
    assert order.status == "expired"
    assert inventory.quantity_reserved == reserved_before - reservation.quantity
    movements = (
        await db.scalars(
            select(InventoryMovement).where(
                InventoryMovement.movement_type == "reservation_release"
            )
        )
    ).all()
    assert len(movements) == 1


def test_phone_normalization():
    assert normalize_phone("+380 67 123 45 67") == "+380671234567"
    assert normalize_phone("0671234567") == "+380671234567"


@pytest.mark.asyncio
async def test_last_units_are_reserved_once_and_order_is_private(
    client, catalog_data, db, admin_identity
):
    from app.auth.dependencies import Identity, get_current_identity, get_optional_identity
    from app.auth.models import User
    from app.main import app

    variant = catalog_data["variants"][0]
    other_user = User(telegram_id=3003, first_name="Other", username="other-checkout")
    db.add(other_user)
    await db.commit()
    other_identity = Identity(user=other_user, role=None)

    async def use_identity(identity):
        async def override():
            return identity

        app.dependency_overrides[get_current_identity] = override
        app.dependency_overrides[get_optional_identity] = override

    await use_identity(admin_identity)
    first_cart = await add_item(client, variant.id, key="last-owner-cart", quantity=4)
    assert first_cart.status_code == 200

    await use_identity(other_identity)
    second_cart = await add_item(client, variant.id, key="last-other-cart", quantity=1)
    assert second_cart.status_code == 200

    await use_identity(admin_identity)
    first = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "last-owner-confirm"},
    )
    assert first.status_code == 200
    order_id = first.json()["data"]["id"]

    await use_identity(other_identity)
    second = await client.post(
        "/api/v1/checkout/confirm",
        json={"contact": CONTACT, "delivery": DELIVERY},
        headers={"Idempotency-Key": "last-other-confirm"},
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] in {
        "CHECKOUT_CART_INVALID",
        "CHECKOUT_INSUFFICIENT_STOCK",
    }
    чужий = await client.get(f"/api/v1/checkout/orders/{order_id}")
    assert чужий.status_code == 404

    inventory = await db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    assert inventory is not None
    assert inventory.quantity_reserved == inventory.quantity_on_hand

    await use_identity(admin_identity)


@pytest.mark.asyncio
async def test_parallel_inventory_reservation_guard_allows_only_one_winner(tmp_path):
    import asyncio
    from datetime import UTC, datetime
    from uuid import uuid4

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.checkout.service import reserve_inventory_quantity
    from app.db.base import Base

    database_path = tmp_path / "parallel-reservation.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path}", connect_args={"timeout": 10}
    )
    maker = async_sessionmaker(engine, expire_on_commit=False)
    inventory_id = uuid4()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with maker() as session:
        session.add(
            Inventory(
                id=inventory_id,
                variant_id=uuid4(),
                quantity_on_hand=1,
                quantity_reserved=0,
                updated_at=datetime.now(UTC),
            )
        )
        await session.commit()

    async def attempt():
        async with maker() as session:
            result = await reserve_inventory_quantity(session, inventory_id, 1, datetime.now(UTC))
            await session.commit()
            return result

    try:
        results = await asyncio.gather(attempt(), attempt())
        assert sum(result is not None for result in results) == 1
        async with maker() as session:
            inventory = await session.get(Inventory, inventory_id)
            assert inventory is not None
            assert inventory.quantity_reserved == 1
            assert inventory.available_quantity == 0
    finally:
        await engine.dispose()
