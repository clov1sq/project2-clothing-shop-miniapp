from decimal import Decimal

import pytest
from sqlalchemy import select

from app.catalog.models import Inventory, Product, ProductVariant
from app.commerce.models import CartItem, Favorite


@pytest.mark.asyncio
async def test_favorite_is_idempotent_and_private(client, catalog_data, db, admin_identity):
    product = catalog_data["product"]
    first = await client.post(f"/api/v1/favorites/{product.id}")
    second = await client.post(f"/api/v1/favorites/{product.id}")
    assert first.status_code == 200
    assert second.status_code == 200

    rows = (
        await db.scalars(
            select(Favorite).where(
                Favorite.user_id == admin_identity.user.id,
                Favorite.product_id == product.id,
            )
        )
    ).all()
    assert len(rows) == 1

    response = await client.get("/api/v1/favorites")
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["is_favorite"] is True

    removed = await client.delete(f"/api/v1/favorites/{product.id}")
    repeated = await client.delete(f"/api/v1/favorites/{product.id}")
    assert removed.status_code == 200
    assert repeated.status_code == 200


@pytest.mark.asyncio
async def test_product_response_contains_favorite_state(client, catalog_data):
    product = catalog_data["product"]
    await client.post(f"/api/v1/favorites/{product.id}")
    response = await client.get(f"/api/v1/products/{product.slug}")
    assert response.status_code == 200
    assert response.json()["data"]["is_favorite"] is True


@pytest.mark.asyncio
async def test_cart_add_repeat_and_idempotency(client, catalog_data, db):
    variant = catalog_data["variants"][0]
    headers = {"Idempotency-Key": "test-add-1"}
    response = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers=headers,
    )
    repeated = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers=headers,
    )
    assert response.status_code == 200
    assert repeated.status_code == 200
    assert response.json()["data"]["total_quantity"] == 1
    assert repeated.json()["data"]["total_quantity"] == 1

    another = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers={"Idempotency-Key": "test-add-2"},
    )
    assert another.json()["data"]["total_quantity"] == 2
    items = (await db.scalars(select(CartItem))).all()
    assert len(items) == 1
    assert items[0].quantity == 2


@pytest.mark.asyncio
async def test_cart_validates_stock_and_inactive_variant(client, catalog_data, db):
    available_variant = catalog_data["variants"][0]
    too_many = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(available_variant.id), "quantity": 5},
        headers={"Idempotency-Key": "stock-limit"},
    )
    assert too_many.status_code == 409
    assert too_many.json()["error"]["code"] == "CART_QUANTITY_EXCEEDS_STOCK"

    unavailable_variant = catalog_data["variants"][1]
    unavailable = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(unavailable_variant.id), "quantity": 1},
        headers={"Idempotency-Key": "out-of-stock"},
    )
    assert unavailable.status_code == 409
    assert unavailable.json()["error"]["code"] == "VARIANT_OUT_OF_STOCK"

    available_variant.is_active = False
    await db.commit()
    inactive = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(available_variant.id), "quantity": 1},
        headers={"Idempotency-Key": "inactive"},
    )
    assert inactive.status_code == 409
    assert inactive.json()["error"]["code"] == "VARIANT_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_cart_price_change_and_clear(client, catalog_data, db):
    product: Product = catalog_data["product"]
    variant: ProductVariant = catalog_data["variants"][0]
    added = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers={"Idempotency-Key": "price-change"},
    )
    assert added.status_code == 200
    item_id = added.json()["data"]["items"][0]["id"]

    product.base_price = Decimal("2999.00")
    await db.commit()
    current = await client.get("/api/v1/cart")
    assert current.json()["data"]["items"][0]["price_changed"] is True

    refreshed = await client.post("/api/v1/cart/refresh")
    assert refreshed.json()["data"]["items"][0]["price_changed"] is False

    updated = await client.patch(
        f"/api/v1/cart/items/{item_id}", json={"quantity": 2}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["total_quantity"] == 2

    cleared = await client.delete("/api/v1/cart")
    assert cleared.status_code == 200
    assert cleared.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_cart_requires_idempotency_key(client, catalog_data):
    variant = catalog_data["variants"][0]
    response = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"

@pytest.mark.asyncio
async def test_cart_rejects_invalid_quantity(client, catalog_data):
    variant = catalog_data["variants"][0]
    response = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 0},
        headers={"Idempotency-Key": "invalid-quantity"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CART_QUANTITY_INVALID"


@pytest.mark.asyncio
async def test_cart_marks_existing_item_when_stock_disappears(client, catalog_data, db):
    variant = catalog_data["variants"][0]
    added = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 2},
        headers={"Idempotency-Key": "stock-disappears"},
    )
    assert added.status_code == 200
    inventory = await db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    assert inventory is not None
    inventory.quantity_on_hand = inventory.quantity_reserved
    await db.commit()

    response = await client.get("/api/v1/cart")
    item = response.json()["data"]["items"][0]
    assert item["quantity"] == 2
    assert item["is_available"] is False
    assert item["unavailable_reason"] == "VARIANT_OUT_OF_STOCK"


@pytest.mark.asyncio
async def test_archived_product_cannot_be_added_to_favorites_or_cart(client, catalog_data, db):
    product = catalog_data["product"]
    variant = catalog_data["variants"][0]
    product.status = "archived"
    await db.commit()

    favorite = await client.post(f"/api/v1/favorites/{product.id}")
    cart = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers={"Idempotency-Key": "archived-product"},
    )
    assert favorite.status_code == 409
    assert favorite.json()["error"]["code"] == "PRODUCT_NOT_ACTIVE"
    assert cart.status_code == 409
    assert cart.json()["error"]["code"] == "CART_ITEM_UNAVAILABLE"


@pytest.mark.asyncio
async def test_idempotency_key_conflict_is_rejected(client, catalog_data):
    first_variant, second_variant = catalog_data["variants"]
    first = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(first_variant.id), "quantity": 1},
        headers={"Idempotency-Key": "same-key-different-payload"},
    )
    conflict = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(second_variant.id), "quantity": 1},
        headers={"Idempotency-Key": "same-key-different-payload"},
    )
    assert first.status_code == 200
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"

@pytest.mark.asyncio
async def test_users_cannot_see_each_others_favorites_or_cart(
    client, catalog_data, db, admin_identity
):
    from app.auth.dependencies import Identity, get_current_identity, get_optional_identity
    from app.auth.models import User
    from app.main import app

    product = catalog_data["product"]
    variant = catalog_data["variants"][0]
    await client.post(f"/api/v1/favorites/{product.id}")
    await client.post(
        "/api/v1/cart/items",
        json={"variant_id": str(variant.id), "quantity": 1},
        headers={"Idempotency-Key": "owner-private-cart"},
    )

    other_user = User(telegram_id=2002, first_name="Other", username="other")
    db.add(other_user)
    await db.commit()
    other_identity = Identity(user=other_user, role=None)

    async def override_other():
        return other_identity

    app.dependency_overrides[get_current_identity] = override_other
    app.dependency_overrides[get_optional_identity] = override_other
    try:
        favorites = await client.get("/api/v1/favorites")
        cart = await client.get("/api/v1/cart")
        assert favorites.status_code == 200
        assert favorites.json()["data"]["items"] == []
        assert cart.status_code == 200
        assert cart.json()["data"]["items"] == []
    finally:
        async def override_owner():
            return admin_identity

        app.dependency_overrides[get_current_identity] = override_owner
        app.dependency_overrides[get_optional_identity] = override_owner
