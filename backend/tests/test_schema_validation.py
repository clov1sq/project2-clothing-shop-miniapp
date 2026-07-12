from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.catalog.schemas import ProductCreate, VariantCreate


def test_product_compare_price_must_be_higher() -> None:
    with pytest.raises(ValidationError):
        ProductCreate(
            category_id=uuid4(),
            brand_id=uuid4(),
            name="Товар",
            model_code="MODEL-1",
            base_price=Decimal("1000"),
            compare_at_price=Decimal("900"),
        )


def test_variant_initial_quantity_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        VariantCreate(
            color_id=uuid4(),
            size_id=uuid4(),
            sku="SKU-1",
            initial_quantity=-1,
        )
