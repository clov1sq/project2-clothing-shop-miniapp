"""checkout orders and inventory reservations

Revision ID: 0005_checkout_reservations
Revises: 0004_favorites_cart
Create Date: 2026-07-13 13:30:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_checkout_reservations"
down_revision = "0004_favorites_cart"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_sessions", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_number", sa.String(length=40), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("payment_status", sa.String(length=30), nullable=False),
        sa.Column("delivery_status", sa.String(length=30), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("delivery_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("grand_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("delivery_method", sa.String(length=30), nullable=False),
        sa.Column("delivery_data_json", sa.Text(), nullable=False),
        sa.Column("reservation_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("status IN ('awaiting_payment','cancelled','expired')", name="ck_orders_status"),
        sa.CheckConstraint(
            "payment_status IN ('not_started','pending','cancelled')",
            name="ck_orders_payment_status",
        ),
        sa.CheckConstraint("delivery_status IN ('not_created')", name="ck_orders_delivery_status"),
        sa.CheckConstraint(
            "delivery_method IN ('pickup','branch','courier')",
            name="ck_orders_delivery_method",
        ),
        sa.CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_nonnegative"),
        sa.CheckConstraint("discount_total >= 0", name="ck_orders_discount_nonnegative"),
        sa.CheckConstraint("delivery_total >= 0", name="ck_orders_delivery_nonnegative"),
        sa.CheckConstraint("grand_total >= 0", name="ck_orders_grand_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_number", name="uq_orders_order_number"),
    )
    op.create_index("ix_orders_user_created", "orders", ["user_id", "created_at"])
    op.create_index("ix_orders_status_expiry", "orders", ["status", "reservation_expires_at"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=True),
        sa.Column("variant_id", sa.Uuid(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("brand_name", sa.String(length=180), nullable=False),
        sa.Column("product_slug", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=120), nullable=False),
        sa.Column("color_name", sa.String(length=100), nullable=False),
        sa.Column("size_name", sa.String(length=100), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("compare_at_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_order_items_price_nonnegative"),
        sa.CheckConstraint("subtotal >= 0", name="ck_order_items_subtotal_nonnegative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_order", "order_items", ["order_id"])
    op.create_index("ix_order_items_variant", "order_items", ["variant_id"])

    op.create_table(
        "inventory_reservations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_reservations_quantity_positive"),
        sa.CheckConstraint(
            "status IN ('active','released','expired','consumed')",
            name="ck_inventory_reservations_status",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", "variant_id", name="uq_reservations_order_variant"),
    )
    op.create_index(
        "ix_reservations_status_expiry", "inventory_reservations", ["status", "expires_at"]
    )
    op.create_index(
        "ix_reservations_variant_active", "inventory_reservations", ["variant_id", "status"]
    )

    with op.batch_alter_table("inventory_movements") as batch_op:
        batch_op.drop_constraint("ck_inventory_movement_type", type_="check")
        batch_op.create_check_constraint(
            "ck_inventory_movement_type",
            "movement_type IN ('initial','manual_adjustment','correction','reservation','reservation_release')",
        )


def downgrade() -> None:
    with op.batch_alter_table("inventory_movements") as batch_op:
        batch_op.drop_constraint("ck_inventory_movement_type", type_="check")
        batch_op.create_check_constraint(
            "ck_inventory_movement_type",
            "movement_type IN ('initial','manual_adjustment','correction')",
        )
    op.drop_index("ix_reservations_variant_active", table_name="inventory_reservations")
    op.drop_index("ix_reservations_status_expiry", table_name="inventory_reservations")
    op.drop_table("inventory_reservations")
    op.drop_index("ix_order_items_variant", table_name="order_items")
    op.drop_index("ix_order_items_order", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_status_expiry", table_name="orders")
    op.drop_index("ix_orders_user_created", table_name="orders")
    op.drop_table("orders")
    op.drop_column("user_sessions", "last_used_at")
