from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.catalog.models import ProductVariant


async def test_unique_sku(db, catalog_data) -> None:
    duplicate = ProductVariant(
        product_id=catalog_data["product"].id,
        color_id=catalog_data["colors"][0].id,
        size_id=catalog_data["sizes"][1].id,
        sku="NF-001-BLK-S",
        is_active=True,
    )
    db.add(duplicate)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()


def test_product_price_uses_decimal(catalog_data) -> None:
    assert catalog_data["product"].base_price == Decimal("3200.00")


async def test_unique_product_slug(db, catalog_data) -> None:
    from app.catalog.models import Product

    product = catalog_data["product"]
    duplicate = Product(
        category_id=product.category_id,
        brand_id=product.brand_id,
        name="Інший товар",
        slug=product.slug,
        model_code="NF-OTHER",
        base_price=Decimal("1000.00"),
        currency="UAH",
        status="draft",
        is_featured=False,
        is_new=False,
        version=1,
    )
    db.add(duplicate)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()


async def test_unique_variant_combination(db, catalog_data) -> None:
    duplicate = ProductVariant(
        product_id=catalog_data["product"].id,
        color_id=catalog_data["colors"][0].id,
        size_id=catalog_data["sizes"][0].id,
        sku="NF-001-SECOND-SKU",
        is_active=True,
    )
    db.add(duplicate)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()
