from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str | None = Field(default=None, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    image_url: str | None = None
    parent_id: UUID | None = None
    sort_order: int = 100
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    slug: str | None = Field(default=None, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    image_url: str | None = None
    parent_id: UUID | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class BrandCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str | None = Field(default=None, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    logo_url: str | None = None
    is_active: bool = True


class BrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    slug: str | None = Field(default=None, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    logo_url: str | None = None
    is_active: bool | None = None


class ProductCreate(BaseModel):
    category_id: UUID
    brand_id: UUID
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    model_code: str = Field(min_length=2, max_length=100)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=12000)
    material: str | None = Field(default=None, max_length=2000)
    care_instructions: str | None = Field(default=None, max_length=2000)
    base_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    compare_at_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="UAH", min_length=3, max_length=3)
    is_featured: bool = False
    is_new: bool = False

    @model_validator(mode="after")
    def validate_prices(self):
        if self.compare_at_price is not None and self.compare_at_price <= self.base_price:
            raise ValueError("compare_at_price має бути більшою за base_price")
        return self


class ProductUpdate(BaseModel):
    expected_version: int = Field(ge=1)
    category_id: UUID | None = None
    brand_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    model_code: str | None = Field(default=None, min_length=2, max_length=100)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=12000)
    material: str | None = Field(default=None, max_length=2000)
    care_instructions: str | None = Field(default=None, max_length=2000)
    base_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    compare_at_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_featured: bool | None = None
    is_new: bool | None = None


class VariantCreate(BaseModel):
    color_id: UUID
    size_id: UUID
    sku: str = Field(min_length=2, max_length=120)
    barcode: str | None = Field(default=None, max_length=120)
    price_override: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    compare_at_price_override: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    is_active: bool = True
    initial_quantity: int = Field(default=0, ge=0)


class VariantUpdate(BaseModel):
    color_id: UUID | None = None
    size_id: UUID | None = None
    sku: str | None = Field(default=None, min_length=2, max_length=120)
    barcode: str | None = Field(default=None, max_length=120)
    price_override: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    compare_at_price_override: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    is_active: bool | None = None


class MediaCreate(BaseModel):
    variant_id: UUID | None = None
    url: HttpUrl
    thumbnail_url: HttpUrl | None = None
    alt_text: str | None = Field(default=None, max_length=500)
    sort_order: int = 100
    is_primary: bool = False


class MediaSortItem(BaseModel):
    id: UUID
    sort_order: int
    is_primary: bool = False


class MediaSortRequest(BaseModel):
    items: list[MediaSortItem]


class InventoryAdjust(BaseModel):
    quantity_on_hand: int = Field(ge=0)
    movement_type: str = Field(pattern="^(initial|manual_adjustment|correction)$")
    reason: str = Field(min_length=2, max_length=500)
