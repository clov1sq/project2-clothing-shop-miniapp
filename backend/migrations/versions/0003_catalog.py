"""catalog, variants, media and inventory

Revision ID: 0003_catalog
Revises: 0002_auth
Create Date: 2026-07-12 11:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_catalog"
down_revision = "0002_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="100", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)
    op.create_index("ix_categories_active_sort", "categories", ["is_active", "sort_order"])
    op.create_index("ix_categories_parent", "categories", ["parent_id"])

    op.create_table(
        "brands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_brands_slug", "brands", ["slug"], unique=True)
    op.create_index("ix_brands_active_name", "brands", ["is_active", "name"])

    op.create_table(
        "colors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("hex_value", sa.String(length=20), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="100", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_colors_active_sort", "colors", ["is_active", "sort_order"])

    op.create_table(
        "sizes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="100", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_sizes_active_sort", "sizes", ["is_active", "sort_order"])

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("brand_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("model_code", sa.String(length=100), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("material", sa.Text(), nullable=True),
        sa.Column("care_instructions", sa.Text(), nullable=True),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("compare_at_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), server_default="UAH", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_new", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("base_price >= 0", name="ck_products_base_price_nonnegative"),
        sa.CheckConstraint(
            "compare_at_price IS NULL OR compare_at_price >= 0",
            name="ck_products_compare_price_nonnegative",
        ),
        sa.CheckConstraint("status IN ('draft','active','archived')", name="ck_products_status"),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_code"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_category_status", "products", ["category_id", "status"])
    op.create_index("ix_products_brand_status", "products", ["brand_id", "status"])
    op.create_index("ix_products_featured_published", "products", ["is_featured", "published_at"])
    op.create_index("ix_products_new_published", "products", ["is_new", "published_at"])

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("color_id", sa.Uuid(), nullable=False),
        sa.Column("size_id", sa.Uuid(), nullable=False),
        sa.Column("sku", sa.String(length=120), nullable=False),
        sa.Column("barcode", sa.String(length=120), nullable=True),
        sa.Column("price_override", sa.Numeric(12, 2), nullable=True),
        sa.Column("compare_at_price_override", sa.Numeric(12, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "price_override IS NULL OR price_override >= 0", name="ck_variants_price_nonnegative"
        ),
        sa.CheckConstraint(
            "compare_at_price_override IS NULL OR compare_at_price_override >= 0",
            name="ck_variants_compare_nonnegative",
        ),
        sa.ForeignKeyConstraint(["color_id"], ["colors.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["size_id"], ["sizes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barcode"),
        sa.UniqueConstraint(
            "product_id", "color_id", "size_id", name="uq_product_variant_combination"
        ),
        sa.UniqueConstraint("sku"),
    )
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"], unique=True)
    op.create_index("ix_variants_product_active", "product_variants", ["product_id", "is_active"])
    op.create_index("ix_variants_color_size", "product_variants", ["color_id", "size_id"])

    op.create_table(
        "product_media",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=True),
        sa.Column("media_type", sa.String(length=20), server_default="image", nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("alt_text", sa.String(length=500), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="100", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("media_type IN ('image')", name="ck_product_media_type"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_media_product_sort", "product_media", ["product_id", "sort_order"])
    op.create_index("ix_product_media_variant", "product_media", ["variant_id"])

    op.create_table(
        "inventory",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), server_default="0", nullable=False),
        sa.Column("quantity_reserved", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_on_hand_nonnegative"),
        sa.CheckConstraint("quantity_reserved >= 0", name="ck_inventory_reserved_nonnegative"),
        sa.CheckConstraint(
            "quantity_reserved <= quantity_on_hand", name="ck_inventory_reserved_lte_on_hand"
        ),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("variant_id"),
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=False),
        sa.Column("movement_type", sa.String(length=40), nullable=False),
        sa.Column("quantity_delta", sa.Integer(), nullable=False),
        sa.Column("quantity_before", sa.Integer(), nullable=False),
        sa.Column("quantity_after", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "movement_type IN ('initial','manual_adjustment','correction')",
            name="ck_inventory_movement_type",
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inventory_movements_variant_created",
        "inventory_movements",
        ["variant_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_movements_variant_created", table_name="inventory_movements")
    op.drop_table("inventory_movements")
    op.drop_table("inventory")
    op.drop_index("ix_product_media_variant", table_name="product_media")
    op.drop_index("ix_product_media_product_sort", table_name="product_media")
    op.drop_table("product_media")
    op.drop_index("ix_variants_color_size", table_name="product_variants")
    op.drop_index("ix_variants_product_active", table_name="product_variants")
    op.drop_index("ix_product_variants_sku", table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_index("ix_products_new_published", table_name="products")
    op.drop_index("ix_products_featured_published", table_name="products")
    op.drop_index("ix_products_brand_status", table_name="products")
    op.drop_index("ix_products_category_status", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_sizes_active_sort", table_name="sizes")
    op.drop_table("sizes")
    op.drop_index("ix_colors_active_sort", table_name="colors")
    op.drop_table("colors")
    op.drop_index("ix_brands_active_name", table_name="brands")
    op.drop_index("ix_brands_slug", table_name="brands")
    op.drop_table("brands")
    op.drop_index("ix_categories_parent", table_name="categories")
    op.drop_index("ix_categories_active_sort", table_name="categories")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
