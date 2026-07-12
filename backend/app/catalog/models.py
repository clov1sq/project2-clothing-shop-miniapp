from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_active_sort", "is_active", "sort_order"),
        Index("ix_categories_parent", "parent_id"),
    )

    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    parent: Mapped["Category | None"] = relationship(remote_side="Category.id")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Brand(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "brands"
    __table_args__ = (Index("ix_brands_active_name", "is_active", "name"),)

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class Color(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "colors"
    __table_args__ = (Index("ix_colors_active_sort", "is_active", "sort_order"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    hex_value: Mapped[str | None] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Size(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "sizes"
    __table_args__ = (Index("ix_sizes_active_sort", "is_active", "sort_order"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Product(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("base_price >= 0", name="ck_products_base_price_nonnegative"),
        CheckConstraint(
            "compare_at_price IS NULL OR compare_at_price >= 0",
            name="ck_products_compare_price_nonnegative",
        ),
        CheckConstraint("status IN ('draft','active','archived')", name="ck_products_status"),
        Index("ix_products_category_status", "category_id", "status"),
        Index("ix_products_brand_status", "brand_id", "status"),
        Index("ix_products_featured_published", "is_featured", "published_at"),
        Index("ix_products_new_published", "is_new", "published_at"),
    )

    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    model_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    material: Mapped[str | None] = mapped_column(Text)
    care_instructions: Mapped[str | None] = mapped_column(Text)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    compare_at_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="UAH", server_default="UAH")
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_new: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    category: Mapped[Category] = relationship(back_populates="products", lazy="selectin")
    brand: Mapped[Brand] = relationship(back_populates="products", lazy="selectin")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product", order_by="ProductVariant.created_at", lazy="selectin"
    )
    media: Mapped[list["ProductMedia"]] = relationship(
        back_populates="product", order_by="ProductMedia.sort_order", lazy="selectin"
    )


class ProductVariant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "color_id", "size_id", name="uq_product_variant_combination"
        ),
        CheckConstraint(
            "price_override IS NULL OR price_override >= 0",
            name="ck_variants_price_nonnegative",
        ),
        CheckConstraint(
            "compare_at_price_override IS NULL OR compare_at_price_override >= 0",
            name="ck_variants_compare_nonnegative",
        ),
        Index("ix_variants_product_active", "product_id", "is_active"),
        Index("ix_variants_color_size", "color_id", "size_id"),
    )

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    color_id: Mapped[UUID] = mapped_column(ForeignKey("colors.id"), nullable=False)
    size_id: Mapped[UUID] = mapped_column(ForeignKey("sizes.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(120), unique=True)
    price_override: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    compare_at_price_override: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    product: Mapped[Product] = relationship(back_populates="variants")
    color: Mapped[Color] = relationship(lazy="selectin")
    size: Mapped[Size] = relationship(lazy="selectin")
    inventory: Mapped["Inventory | None"] = relationship(
        back_populates="variant", uselist=False, lazy="selectin"
    )
    media: Mapped[list["ProductMedia"]] = relationship(back_populates="variant")


class ProductMedia(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "product_media"
    __table_args__ = (
        CheckConstraint("media_type IN ('image')", name="ck_product_media_type"),
        Index("ix_product_media_product_sort", "product_id", "sort_order"),
        Index("ix_product_media_variant", "variant_id"),
    )

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    media_type: Mapped[str] = mapped_column(String(20), default="image", server_default="image")
    url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text)
    alt_text: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product] = relationship(back_populates="media")
    variant: Mapped[ProductVariant | None] = relationship(back_populates="media")


class Inventory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_on_hand_nonnegative"),
        CheckConstraint("quantity_reserved >= 0", name="ck_inventory_reserved_nonnegative"),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand", name="ck_inventory_reserved_lte_on_hand"
        ),
    )

    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    quantity_reserved: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    variant: Mapped[ProductVariant] = relationship(back_populates="inventory")

    @property
    def available_quantity(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved


class InventoryMovement(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('initial','manual_adjustment','correction')",
            name="ck_inventory_movement_type",
        ),
        Index("ix_inventory_movements_variant_created", "variant_id", "created_at"),
    )

    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_before: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
