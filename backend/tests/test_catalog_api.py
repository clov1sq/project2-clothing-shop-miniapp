from app.db.session import get_session
from app.main import app


async def test_catalog_filters(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    response = await client.get(
        "/api/v1/products",
        params={"category": "clothing", "color": "black", "only_available": True},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["slug"] == "straight-coat"
    assert data["items"][0]["discount_percent"] == 20


async def test_product_detail_has_valid_combinations(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    response = await client.get("/api/v1/products/straight-coat")
    assert response.status_code == 200
    product = response.json()["data"]
    assert len(product["variants"]) == 2
    assert product["variants"][0]["available_quantity"] in {0, 4}
    assert {variant["color_code"] for variant in product["variants"]} == {"black", "cobalt"}


async def test_inactive_product_hidden(client, session_maker, catalog_data) -> None:
    async with session_maker() as session:
        product = await session.get(type(catalog_data["product"]), catalog_data["product"].id)
        product.status = "draft"
        await session.commit()
    response = await client.get("/api/v1/products/straight-coat")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


async def test_catalog_search_and_price_sort(client, session_maker, catalog_data) -> None:
    async def override_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    response = await client.get(
        "/api/v1/products",
        params={"search": "North", "sort": "price_asc"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert [item["slug"] for item in items] == ["straight-coat"]


async def test_invalid_price_filter_rejected(client) -> None:
    response = await client.get("/api/v1/products", params={"min_price": 2000, "max_price": 1000})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_FILTER"
