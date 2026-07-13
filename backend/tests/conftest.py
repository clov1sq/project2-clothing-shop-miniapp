from datetime import UTC, datetime
from decimal import Decimal

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import (
    Identity,
    get_current_identity,
    get_optional_identity,
    require_admin,
)
from app.auth.models import ShopMember, User
from app.catalog.models import (
    Brand,
    Category,
    Color,
    Inventory,
    Product,
    ProductMedia,
    ProductVariant,
    Size,
)
from app.db.base import Base
from app.db.session import get_session
from app.main import app


@pytest_asyncio.fixture
async def session_maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield maker
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db(session_maker):
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def catalog_data(db: AsyncSession):
    category = Category(name="Одяг", slug="clothing", sort_order=10, is_active=True)
    brand = Brand(name="North Form", slug="north-form", is_active=True)
    black = Color(name="Чорний", code="black", hex_value="#111111", sort_order=10, is_active=True)
    cobalt = Color(name="Синій", code="cobalt", hex_value="#1747D1", sort_order=20, is_active=True)
    small = Size(name="S", code="s", sort_order=10, is_active=True)
    medium = Size(name="M", code="m", sort_order=20, is_active=True)
    db.add_all([category, brand, black, cobalt, small, medium])
    await db.flush()
    product = Product(
        category_id=category.id,
        brand_id=brand.id,
        name="Пальто прямого крою",
        slug="straight-coat",
        model_code="NF-001",
        short_description="Лаконічне пальто",
        description="Опис",
        material="Вовна",
        care_instructions="Хімчистка",
        base_price=Decimal("3200.00"),
        compare_at_price=Decimal("4000.00"),
        currency="UAH",
        status="active",
        is_featured=True,
        is_new=True,
        version=1,
        published_at=datetime.now(UTC),
    )
    db.add(product)
    await db.flush()
    v1 = ProductVariant(
        product_id=product.id,
        color_id=black.id,
        size_id=small.id,
        sku="NF-001-BLK-S",
        is_active=True,
    )
    v2 = ProductVariant(
        product_id=product.id,
        color_id=cobalt.id,
        size_id=medium.id,
        sku="NF-001-COB-M",
        is_active=True,
    )
    db.add_all([v1, v2])
    await db.flush()
    db.add_all(
        [
            Inventory(
                variant_id=v1.id,
                quantity_on_hand=5,
                quantity_reserved=1,
                updated_at=datetime.now(UTC),
            ),
            Inventory(
                variant_id=v2.id,
                quantity_on_hand=0,
                quantity_reserved=0,
                updated_at=datetime.now(UTC),
            ),
            ProductMedia(
                product_id=product.id,
                url="https://example.com/coat.webp",
                thumbnail_url=None,
                alt_text="Пальто",
                sort_order=10,
                is_primary=True,
                media_type="image",
                created_at=datetime.now(UTC),
            ),
        ]
    )
    await db.commit()
    return {
        "category": category,
        "brand": brand,
        "colors": [black, cobalt],
        "sizes": [small, medium],
        "product": product,
        "variants": [v1, v2],
    }


@pytest_asyncio.fixture
async def admin_identity(db: AsyncSession):
    user = User(telegram_id=1001, first_name="Admin", username="admin")
    db.add(user)
    await db.flush()
    membership = ShopMember(user_id=user.id, role="owner", is_active=True)
    db.add(membership)
    await db.commit()
    await db.refresh(user, attribute_names=["membership"])
    return Identity(user=user, role="owner")


@pytest_asyncio.fixture
async def client(session_maker, admin_identity):
    async def override_session():
        async with session_maker() as session:
            yield session

    async def override_admin():
        return admin_identity

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[get_current_identity] = override_admin
    app.dependency_overrides[get_optional_identity] = override_admin
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()
