from app.db.session import get_session
from app.main import app


async def test_admin_creates_draft(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    response = await client.post(
        "/api/v1/admin/products",
        json={
            "category_id": str(catalog_data["category"].id),
            "brand_id": str(catalog_data["brand"].id),
            "name": "Новий жакет",
            "model_code": "NF-NEW-1",
            "base_price": "2500.00",
            "currency": "UAH",
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "draft"


async def test_admin_conflict_update(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    product_id = str(catalog_data["product"].id)
    response = await client.patch(
        f"/api/v1/admin/products/{product_id}",
        json={"expected_version": 999, "name": "Інша назва"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONCURRENT_UPDATE_CONFLICT"


async def test_inventory_cannot_go_below_reserved(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    variant_id = str(catalog_data["variants"][0].id)
    response = await client.patch(
        f"/api/v1/admin/variants/{variant_id}/inventory",
        json={"quantity_on_hand": 0, "movement_type": "correction", "reason": "Перевірка"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVENTORY_NEGATIVE"


async def test_publish_and_archive_product(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    product_id = str(catalog_data["product"].id)
    async with session_maker() as session:
        product = await session.get(type(catalog_data["product"]), catalog_data["product"].id)
        product.status = "draft"
        await session.commit()

    published = await client.post(f"/api/v1/admin/products/{product_id}/publish")
    assert published.status_code == 200
    assert published.json()["data"]["status"] == "active"

    archived = await client.post(f"/api/v1/admin/products/{product_id}/archive")
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"
    assert all(not item["is_active"] for item in archived.json()["data"]["variants"])


async def test_inventory_adjustment_writes_movement(client, session_maker, catalog_data) -> None:
    from sqlalchemy import select

    from app.catalog.models import InventoryMovement

    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    variant_id = str(catalog_data["variants"][0].id)
    response = await client.patch(
        f"/api/v1/admin/variants/{variant_id}/inventory",
        json={"quantity_on_hand": 8, "movement_type": "correction", "reason": "Перерахунок"},
    )
    assert response.status_code == 200
    async with session_maker() as session:
        movement = await session.scalar(select(InventoryMovement))
        assert movement is not None
        assert movement.quantity_before == 5
        assert movement.quantity_after == 8
        assert movement.quantity_delta == 3
