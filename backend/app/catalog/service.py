import re
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

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
from app.core.errors import AppError

PRODUCT_LOAD_OPTIONS = (
    selectinload(Product.category),
    selectinload(Product.brand),
    selectinload(Product.media),
    selectinload(Product.variants).selectinload(ProductVariant.color),
    selectinload(Product.variants).selectinload(ProductVariant.size),
    selectinload(Product.variants).selectinload(ProductVariant.inventory),
)


def slugify(value: str) -> str:
    value = value.strip().lower()
    translit = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ie",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ь": "",
        "ю": "iu",
        "я": "ia",
    }
    value = "".join(translit.get(char, char) for char in value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def discount_percent(price: Decimal, compare_at_price: Decimal | None) -> int | None:
    if compare_at_price is None or compare_at_price <= price or compare_at_price <= 0:
        return None
    return int(((compare_at_price - price) / compare_at_price * 100).quantize(Decimal("1")))


def product_primary_media(product: Product) -> ProductMedia | None:
    active_media = sorted(product.media, key=lambda item: (not item.is_primary, item.sort_order))
    return active_media[0] if active_media else None


def variant_effective_price(product: Product, variant: ProductVariant) -> Decimal:
    return variant.price_override if variant.price_override is not None else product.base_price


def variant_effective_compare(product: Product, variant: ProductVariant) -> Decimal | None:
    return (
        variant.compare_at_price_override
        if variant.compare_at_price_override is not None
        else product.compare_at_price
    )


def serialize_category(category: Category) -> dict[str, object]:
    return {
        "id": str(category.id),
        "parent_id": str(category.parent_id) if category.parent_id else None,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "image_url": category.image_url,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


def serialize_brand(brand: Brand) -> dict[str, object]:
    return {
        "id": str(brand.id),
        "name": brand.name,
        "slug": brand.slug,
        "description": brand.description,
        "logo_url": brand.logo_url,
        "is_active": brand.is_active,
    }


def serialize_product_card(product: Product) -> dict[str, object]:
    media = product_primary_media(product)
    active_variants = [
        variant for variant in product.variants if variant.is_active and variant.archived_at is None
    ]
    is_available = any(
        variant.inventory is not None and variant.inventory.available_quantity > 0
        for variant in active_variants
    )
    color_map = {
        variant.color.code: {
            "code": variant.color.code,
            "name": variant.color.name,
            "hex_value": variant.color.hex_value,
        }
        for variant in active_variants
        if variant.color.is_active
    }
    return {
        "id": str(product.id),
        "slug": product.slug,
        "brand": {"name": product.brand.name, "slug": product.brand.slug},
        "category": {"name": product.category.name, "slug": product.category.slug},
        "name": product.name,
        "model_code": product.model_code,
        "short_description": product.short_description,
        "price": money(product.base_price),
        "compare_at_price": money(product.compare_at_price),
        "discount_percent": discount_percent(product.base_price, product.compare_at_price),
        "currency": product.currency,
        "image_url": media.url if media else None,
        "thumbnail_url": media.thumbnail_url if media else None,
        "is_new": product.is_new,
        "is_featured": product.is_featured,
        "is_sale": discount_percent(product.base_price, product.compare_at_price) is not None,
        "is_available": is_available,
        "colors": list(color_map.values()),
    }


def serialize_product_detail(product: Product, admin: bool = False) -> dict[str, object]:
    media = [
        {
            "id": str(item.id),
            "variant_id": str(item.variant_id) if item.variant_id else None,
            "url": item.url,
            "thumbnail_url": item.thumbnail_url,
            "alt_text": item.alt_text,
            "sort_order": item.sort_order,
            "is_primary": item.is_primary,
        }
        for item in sorted(product.media, key=lambda item: item.sort_order)
    ]
    variants = []
    colors: dict[str, dict[str, object]] = {}
    sizes: dict[str, dict[str, object]] = {}
    for variant in product.variants:
        if not admin and (not variant.is_active or variant.archived_at is not None):
            continue
        available = variant.inventory.available_quantity if variant.inventory else 0
        price = variant_effective_price(product, variant)
        compare = variant_effective_compare(product, variant)
        variant_payload: dict[str, object] = {
            "id": str(variant.id),
            "color_id": str(variant.color_id),
            "size_id": str(variant.size_id),
            "color_code": variant.color.code,
            "size_code": variant.size.code,
            "sku": variant.sku,
            "barcode": variant.barcode if admin else None,
            "price": money(price),
            "compare_at_price": money(compare),
            "discount_percent": discount_percent(price, compare),
            "available_quantity": available,
            "is_available": available > 0 and variant.is_active,
            "is_active": variant.is_active,
            "archived_at": variant.archived_at.isoformat() if variant.archived_at else None,
        }
        if admin:
            variant_payload.update(
                {
                    "quantity_on_hand": (
                        variant.inventory.quantity_on_hand if variant.inventory else 0
                    ),
                    "quantity_reserved": (
                        variant.inventory.quantity_reserved if variant.inventory else 0
                    ),
                }
            )
        variants.append(variant_payload)
        colors[variant.color.code] = {
            "id": str(variant.color.id),
            "code": variant.color.code,
            "name": variant.color.name,
            "hex_value": variant.color.hex_value,
            "sort_order": variant.color.sort_order,
        }
        sizes[variant.size.code] = {
            "id": str(variant.size.id),
            "code": variant.size.code,
            "name": variant.size.name,
            "sort_order": variant.size.sort_order,
        }

    payload = serialize_product_card(product)
    payload.update(
        {
            "description": product.description,
            "material": product.material,
            "care_instructions": product.care_instructions,
            "status": product.status if admin else "active",
            "version": product.version if admin else None,
            "published_at": product.published_at.isoformat() if product.published_at else None,
            "archived_at": product.archived_at.isoformat() if product.archived_at else None,
            "media": media,
            "colors": sorted(
                colors.values(),
                key=lambda item: item["sort_order"] if isinstance(item["sort_order"], int) else 0,
            ),
            "sizes": sorted(
                sizes.values(),
                key=lambda item: item["sort_order"] if isinstance(item["sort_order"], int) else 0,
            ),
            "variants": variants,
        }
    )
    return payload


def _public_conditions(
    *,
    category: str | None,
    brand: str | None,
    color: str | None,
    size: str | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    only_available: bool,
    sale: bool,
    new: bool,
    search: str | None,
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = [
        Product.status == "active",
        Product.archived_at.is_(None),
        Category.is_active.is_(True),
        Brand.is_active.is_(True),
    ]
    if category:
        conditions.append(Category.slug == category)
    if brand:
        conditions.append(Brand.slug == brand)
    if min_price is not None:
        conditions.append(Product.base_price >= min_price)
    if max_price is not None:
        conditions.append(Product.base_price <= max_price)
    if sale:
        conditions.append(
            and_(
                Product.compare_at_price.is_not(None), Product.compare_at_price > Product.base_price
            )
        )
    if new:
        conditions.append(Product.is_new.is_(True))
    if search and len(search.strip()) >= 2:
        query = f"%{search.strip()}%"
        conditions.append(
            or_(
                Product.name.ilike(query),
                Product.model_code.ilike(query),
                Brand.name.ilike(query),
            )
        )
    if color:
        conditions.append(
            exists()
            .where(ProductVariant.product_id == Product.id)
            .where(ProductVariant.is_active.is_(True))
            .where(ProductVariant.archived_at.is_(None))
            .where(ProductVariant.color_id == Color.id)
            .where(Color.code == color)
        )
    if size:
        conditions.append(
            exists()
            .where(ProductVariant.product_id == Product.id)
            .where(ProductVariant.is_active.is_(True))
            .where(ProductVariant.archived_at.is_(None))
            .where(ProductVariant.size_id == Size.id)
            .where(Size.code == size)
        )
    if only_available:
        conditions.append(
            exists()
            .where(ProductVariant.product_id == Product.id)
            .where(ProductVariant.is_active.is_(True))
            .where(ProductVariant.archived_at.is_(None))
            .where(Inventory.variant_id == ProductVariant.id)
            .where(Inventory.quantity_on_hand - Inventory.quantity_reserved > 0)
        )
    return conditions


async def list_products(
    session: AsyncSession,
    *,
    page: int,
    limit: int,
    category: str | None = None,
    brand: str | None = None,
    color: str | None = None,
    size: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    only_available: bool = False,
    sale: bool = False,
    new: bool = False,
    search: str | None = None,
    sort: str = "popular",
) -> dict[str, object]:
    conditions = _public_conditions(
        category=category,
        brand=brand,
        color=color,
        size=size,
        min_price=min_price,
        max_price=max_price,
        only_available=only_available,
        sale=sale,
        new=new,
        search=search,
    )
    base = select(Product).join(Product.category).join(Product.brand).where(*conditions)
    if sort == "newest":
        base = base.order_by(Product.published_at.desc().nullslast(), Product.created_at.desc())
    elif sort == "price_asc":
        base = base.order_by(Product.base_price.asc(), Product.name.asc())
    elif sort == "price_desc":
        base = base.order_by(Product.base_price.desc(), Product.name.asc())
    elif sort == "discount":
        discount_expr = (Product.compare_at_price - Product.base_price) / func.nullif(
            Product.compare_at_price, 0
        )
        base = base.order_by(discount_expr.desc().nullslast(), Product.published_at.desc())
    else:
        base = base.order_by(
            Product.is_featured.desc(), Product.published_at.desc().nullslast(), Product.name.asc()
        )

    total = await session.scalar(
        select(func.count(Product.id))
        .select_from(Product)
        .join(Product.category)
        .join(Product.brand)
        .where(*conditions)
    )
    statement = base.options(*PRODUCT_LOAD_OPTIONS).offset((page - 1) * limit).limit(limit)
    products = list((await session.scalars(statement)).unique().all())
    total_value = int(total or 0)
    return {
        "items": [serialize_product_card(product) for product in products],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_value,
            "pages": (total_value + limit - 1) // limit,
            "has_next": page * limit < total_value,
        },
    }


async def get_public_product(session: AsyncSession, slug: str) -> Product:
    statement = (
        select(Product)
        .options(*PRODUCT_LOAD_OPTIONS)
        .join(Product.category)
        .join(Product.brand)
        .where(
            Product.slug == slug,
            Product.status == "active",
            Product.archived_at.is_(None),
            Category.is_active.is_(True),
            Brand.is_active.is_(True),
        )
    )
    product = await session.scalar(statement)
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "Товар не знайдено", 404)
    return product


async def get_admin_product(session: AsyncSession, product_id: UUID, lock: bool = False) -> Product:
    statement = select(Product).options(*PRODUCT_LOAD_OPTIONS).where(Product.id == product_id)
    if lock:
        statement = statement.with_for_update()
    product = await session.scalar(statement)
    if product is None:
        raise AppError("PRODUCT_NOT_FOUND", "Товар не знайдено", 404)
    return product
