from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
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


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_orders_order_number"),
        CheckConstraint("status IN ('awaiting_payment','cancelled','expired')", name="ck_orders_status"),
        CheckConstraint(
            "payment_status IN ('not_started','pending','cancelled')",
            name="ck_orders_payment_status",
        ),
        CheckConstraint("delivery_status IN ('not_created')", name="ck_orders_delivery_status"),
        CheckConstraint(
            "delivery_method IN ('pickup','branch','courier')",
            name="ck_orders_delivery_method",
        ),
        CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_nonnegative"),
        CheckConstraint("discount_total >= 0", name="ck_orders_discount_nonnegative"),
        CheckConstraint("delivery_total >= 0", name="ck_orders_delivery_nonnegative"),
        CheckConstraint("grand_total >= 0", name="ck_orders_grand_nonnegative"),
        Index("ix_orders_user_created", "user_id", "created_at"),
        Index("ix_orders_status_expiry", "status", "reservation_expires_at"),
    )

    order_number: Mapped[str] = mapped_column(String(40), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="awaiting_payment")
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_started")
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_created")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="UAH")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    delivery_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(Text)
    delivery_method: Mapped[str] = mapped_column(String(30), nullable=False)
    delivery_data_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    reservation_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )
    reservations: Mapped[list["InventoryReservation"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )


class OrderItem(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_items_price_nonnegative"),
        CheckConstraint("subtotal >= 0", name="ck_order_items_subtotal_nonnegative"),
        Index("ix_order_items_order", "order_id"),
        Index("ix_order_items_variant", "variant_id"),
    )

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    variant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_name: Mapped[str] = mapped_column(String(180), nullable=False)
    product_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(120), nullable=False)
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    size_name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    compare_at_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")


class InventoryReservation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_inventory_reservations_quantity_positive"),
        CheckConstraint(
            "status IN ('active','released','expired','consumed')",
            name="ck_inventory_reservations_status",
        ),
        UniqueConstraint("order_id", "variant_id", name="uq_reservations_order_variant"),
        Index("ix_reservations_status_expiry", "status", "expires_at"),
        Index("ix_reservations_variant_active", "variant_id", "status"),
    )

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped[Order] = relationship(back_populates="reservations")
