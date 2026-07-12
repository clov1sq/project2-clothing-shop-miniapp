from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.audit.service import write_audit
from app.auth.dependencies import Identity, require_admin
from app.catalog.models import (
    Brand,
    Category,
    Color,
    Inventory,
    InventoryMovement,
    Product,
    ProductMedia,
    ProductVariant,
    Size,
)
from app.catalog.schemas import (
    BrandCreate,
    BrandUpdate,
    CategoryCreate,
    CategoryUpdate,
    InventoryAdjust,
    MediaCreate,
    MediaSortRequest,
    ProductCreate,
    ProductUpdate,
    VariantCreate,
    VariantUpdate,
)
from app.catalog.service import (
    PRODUCT_LOAD_OPTIONS,
    get_admin_product,
    serialize_brand,
    serialize_category,
    serialize_product_detail,
    slugify,
)
from app.core.errors import AppError
from app.db.session import get_session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


async def _require_category(session: AsyncSession, category_id: UUID) -> Category:
    item = await session.get(Category, category_id)
    if item is None:
        raise AppError("CATEGORY_NOT_FOUND", "Категорію не знайдено", 404)
    return item


async def _require_brand(session: AsyncSession, brand_id: UUID) -> Brand:
    item = await session.get(Brand, brand_id)
    if item is None:
        raise AppError("BRAND_NOT_FOUND", "Бренд не знайдено", 404)
    return item


@router.get("/dashboard")
async def dashboard(
    _: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    status_rows = (
        await session.execute(
            select(Product.status, func.count(Product.id)).group_by(Product.status)
        )
    ).all()
    low_stock = await session.scalar(
        select(func.count(Inventory.id)).where(
            Inventory.quantity_on_hand - Inventory.quantity_reserved <= 3
        )
    )
    return {
        "ok": True,
        "data": {
            "products_by_status": {status: count for status, count in status_rows},
            "low_stock_variants": int(low_stock or 0),
        },
    }


@router.get("/products")
async def admin_products(
    q: str | None = None,
    status: str | None = Query(default=None, pattern="^(draft|active|archived)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=30, ge=1, le=100),
    _: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    conditions = []
    if status:
        conditions.append(Product.status == status)
    if q and len(q.strip()) >= 2:
        pattern = f"%{q.strip()}%"
        sku_exists = (
            select(ProductVariant.id)
            .where(ProductVariant.product_id == Product.id, ProductVariant.sku.ilike(pattern))
            .exists()
        )
        conditions.append(
            or_(Product.name.ilike(pattern), Product.model_code.ilike(pattern), sku_exists)
        )
    total = await session.scalar(select(func.count(Product.id)).where(*conditions))
    statement = (
        select(Product)
        .options(*PRODUCT_LOAD_OPTIONS)
        .where(*conditions)
        .order_by(Product.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = list((await session.scalars(statement)).unique().all())
    return {
        "ok": True,
        "data": {
            "items": [serialize_product_detail(item, admin=True) for item in items],
            "pagination": {"page": page, "limit": limit, "total": int(total or 0)},
        },
    }


@router.post("/products", status_code=201)
async def create_product(
    payload: ProductCreate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    await _require_category(session, payload.category_id)
    await _require_brand(session, payload.brand_id)
    slug = slugify(payload.slug or payload.name)
    product = Product(
        **payload.model_dump(exclude={"slug"}),
        slug=slug,
        status="draft",
        version=1,
    )
    session.add(product)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        message = str(exc.orig).lower()
        if "slug" in message:
            raise AppError("PRODUCT_SLUG_EXISTS", "Такий slug уже використовується", 409) from exc
        raise AppError("PRODUCT_MODEL_CODE_EXISTS", "Такий код моделі вже існує", 409) from exc
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="product.create",
        entity_type="product",
        entity_id=str(product.id),
        payload={"name": product.name},
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.get("/products/{product_id}")
async def admin_product_detail(
    product_id: UUID,
    _: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.patch("/products/{product_id}")
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    if product.version != payload.expected_version:
        raise AppError(
            "CONCURRENT_UPDATE_CONFLICT",
            "Товар уже змінено в іншому вікні. Оновіть дані",
            409,
            {"current_version": product.version},
        )
    updates = payload.model_dump(exclude_unset=True, exclude={"expected_version"})
    if "category_id" in updates:
        await _require_category(session, updates["category_id"])
    if "brand_id" in updates:
        await _require_brand(session, updates["brand_id"])
    if "slug" in updates and updates["slug"]:
        updates["slug"] = slugify(updates["slug"])
    next_base = updates.get("base_price", product.base_price)
    next_compare = updates.get("compare_at_price", product.compare_at_price)
    if next_compare is not None and next_compare <= next_base:
        raise AppError("PRICE_INVALID", "Стара ціна має бути більшою за поточну", 422)
    for key, value in updates.items():
        setattr(product, key, value)
    product.version += 1
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        message = str(exc.orig).lower()
        if "slug" in message:
            raise AppError("PRODUCT_SLUG_EXISTS", "Такий slug уже використовується", 409) from exc
        raise AppError("PRODUCT_MODEL_CODE_EXISTS", "Такий код моделі вже існує", 409) from exc
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="product.update",
        entity_type="product",
        entity_id=str(product.id),
        payload={"fields": sorted(updates)},
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.post("/products/{product_id}/publish")
async def publish_product(
    product_id: UUID,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    if not product.variants or not any(
        v.is_active and v.archived_at is None for v in product.variants
    ):
        raise AppError("PRODUCT_VARIANTS_REQUIRED", "Додайте хоча б один активний варіант", 422)
    if not product.media:
        raise AppError("PRODUCT_MEDIA_REQUIRED", "Додайте хоча б одне фото", 422)
    product.status = "active"
    product.archived_at = None
    product.published_at = product.published_at or datetime.now(UTC)
    product.version += 1
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="product.publish",
        entity_type="product",
        entity_id=str(product.id),
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.post("/products/{product_id}/archive")
async def archive_product(
    product_id: UUID,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    now = datetime.now(UTC)
    product.status = "archived"
    product.archived_at = now
    product.version += 1
    for variant in product.variants:
        variant.is_active = False
        variant.archived_at = now
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="product.archive",
        entity_type="product",
        entity_id=str(product.id),
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.get("/categories")
async def admin_categories(
    _: Identity = Depends(require_admin), session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    items = (
        await session.scalars(select(Category).order_by(Category.sort_order, Category.name))
    ).all()
    return {"ok": True, "data": {"items": [serialize_category(item) for item in items]}}


@router.post("/categories", status_code=201)
async def create_category(
    payload: CategoryCreate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    item = Category(
        **payload.model_dump(exclude={"slug"}), slug=slugify(payload.slug or payload.name)
    )
    session.add(item)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError("CATEGORY_SLUG_EXISTS", "Такий slug категорії вже існує", 409) from exc
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="category.create",
        entity_type="category",
        entity_id=str(item.id),
    )
    await session.commit()
    return {"ok": True, "data": serialize_category(item)}


@router.patch("/categories/{category_id}")
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    item = await _require_category(session, category_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, slugify(value) if key == "slug" and value else value)
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="category.update",
        entity_type="category",
        entity_id=str(item.id),
    )
    await session.commit()
    return {"ok": True, "data": serialize_category(item)}


@router.get("/brands")
async def admin_brands(
    _: Identity = Depends(require_admin), session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    items = (await session.scalars(select(Brand).order_by(Brand.name))).all()
    return {"ok": True, "data": {"items": [serialize_brand(item) for item in items]}}


@router.post("/brands", status_code=201)
async def create_brand(
    payload: BrandCreate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    item = Brand(**payload.model_dump(exclude={"slug"}), slug=slugify(payload.slug or payload.name))
    session.add(item)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError("BRAND_SLUG_EXISTS", "Такий slug бренду вже існує", 409) from exc
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="brand.create",
        entity_type="brand",
        entity_id=str(item.id),
    )
    await session.commit()
    return {"ok": True, "data": serialize_brand(item)}


@router.patch("/brands/{brand_id}")
async def update_brand(
    brand_id: UUID,
    payload: BrandUpdate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    item = await _require_brand(session, brand_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, slugify(value) if key == "slug" and value else value)
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="brand.update",
        entity_type="brand",
        entity_id=str(item.id),
    )
    await session.commit()
    return {"ok": True, "data": serialize_brand(item)}


@router.get("/options")
async def admin_options(
    _: Identity = Depends(require_admin), session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    colors = (await session.scalars(select(Color).order_by(Color.sort_order))).all()
    sizes = (await session.scalars(select(Size).order_by(Size.sort_order))).all()
    return {
        "ok": True,
        "data": {
            "colors": [
                {
                    "id": str(x.id),
                    "name": x.name,
                    "code": x.code,
                    "hex_value": x.hex_value,
                    "is_active": x.is_active,
                }
                for x in colors
            ],
            "sizes": [
                {"id": str(x.id), "name": x.name, "code": x.code, "is_active": x.is_active}
                for x in sizes
            ],
        },
    }


@router.post("/products/{product_id}/variants", status_code=201)
async def create_variant(
    product_id: UUID,
    payload: VariantCreate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    if (
        await session.get(Color, payload.color_id) is None
        or await session.get(Size, payload.size_id) is None
    ):
        raise AppError("INVALID_VARIANT_COMBINATION", "Некоректний колір або розмір", 422)
    variant = ProductVariant(
        product_id=product.id,
        **payload.model_dump(exclude={"initial_quantity"}),
    )
    session.add(variant)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        message = str(exc.orig).lower()
        if "sku" in message:
            raise AppError("PRODUCT_SKU_EXISTS", "Такий SKU вже використовується", 409) from exc
        raise AppError("INVALID_VARIANT_COMBINATION", "Такий варіант уже існує", 409) from exc
    now = datetime.now(UTC)
    inventory = Inventory(
        variant_id=variant.id,
        quantity_on_hand=payload.initial_quantity,
        quantity_reserved=0,
        updated_at=now,
    )
    session.add(inventory)
    session.add(
        InventoryMovement(
            variant_id=variant.id,
            movement_type="initial",
            quantity_delta=payload.initial_quantity,
            quantity_before=0,
            quantity_after=payload.initial_quantity,
            reason="Початковий залишок",
            created_by_user_id=identity.user.id,
            created_at=now,
        )
    )
    product.version += 1
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="variant.create",
        entity_type="variant",
        entity_id=str(variant.id),
        payload={"sku": variant.sku},
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.patch("/variants/{variant_id}")
async def update_variant(
    variant_id: UUID,
    payload: VariantUpdate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    variant = await session.scalar(
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .where(ProductVariant.id == variant_id)
        .with_for_update()
    )
    if variant is None:
        raise AppError("VARIANT_NOT_FOUND", "Варіант не знайдено", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(variant, key, value)
    variant.product.version += 1
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        message = str(exc.orig).lower()
        if "sku" in message:
            raise AppError("PRODUCT_SKU_EXISTS", "Такий SKU вже використовується", 409) from exc
        raise AppError("INVALID_VARIANT_COMBINATION", "Такий варіант уже існує", 409) from exc
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="variant.update",
        entity_type="variant",
        entity_id=str(variant.id),
    )
    await session.commit()
    product = await get_admin_product(session, variant.product_id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.post("/variants/{variant_id}/archive")
async def archive_variant(
    variant_id: UUID,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    variant = await session.get(ProductVariant, variant_id)
    if variant is None:
        raise AppError("VARIANT_NOT_FOUND", "Варіант не знайдено", 404)
    variant.is_active = False
    variant.archived_at = datetime.now(UTC)
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="variant.archive",
        entity_type="variant",
        entity_id=str(variant.id),
    )
    await session.commit()
    product = await get_admin_product(session, variant.product_id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.post("/products/{product_id}/media", status_code=201)
async def create_media(
    product_id: UUID,
    payload: MediaCreate,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    if payload.variant_id:
        variant = await session.get(ProductVariant, payload.variant_id)
        if variant is None or variant.product_id != product.id:
            raise AppError("VARIANT_NOT_FOUND", "Варіант не знайдено", 404)
    if payload.is_primary:
        await session.execute(
            update(ProductMedia)
            .where(ProductMedia.product_id == product.id)
            .values(is_primary=False)
        )
    media = ProductMedia(
        product_id=product.id,
        variant_id=payload.variant_id,
        media_type="image",
        url=str(payload.url),
        thumbnail_url=str(payload.thumbnail_url) if payload.thumbnail_url else None,
        alt_text=payload.alt_text or product.name,
        sort_order=payload.sort_order,
        is_primary=payload.is_primary or not product.media,
        created_at=datetime.now(UTC),
    )
    session.add(media)
    product.version += 1
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="media.create",
        entity_type="media",
        entity_id=str(media.id),
        payload={"product_id": str(product.id)},
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.patch("/products/{product_id}/media/sort")
async def sort_media(
    product_id: UUID,
    payload: MediaSortRequest,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    product = await get_admin_product(session, product_id, lock=True)
    item_ids = {item.id for item in payload.items}
    valid_ids = {item.id for item in product.media}
    if not item_ids.issubset(valid_ids):
        raise AppError("MEDIA_NOT_FOUND", "Одне з фото не знайдено", 404)
    primary_count = sum(1 for item in payload.items if item.is_primary)
    if primary_count > 1:
        raise AppError("MEDIA_PRIMARY_INVALID", "Основним може бути лише одне фото", 422)
    for payload_item in payload.items:
        media = next(item for item in product.media if item.id == payload_item.id)
        media.sort_order = payload_item.sort_order
        media.is_primary = payload_item.is_primary
    product.version += 1
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="media.sort",
        entity_type="product",
        entity_id=str(product.id),
    )
    await session.commit()
    product = await get_admin_product(session, product.id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.delete("/media/{media_id}")
async def delete_media(
    media_id: UUID,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    media = await session.get(ProductMedia, media_id)
    if media is None:
        raise AppError("MEDIA_NOT_FOUND", "Фото не знайдено", 404)
    product_id = media.product_id
    await session.delete(media)
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="media.delete",
        entity_type="media",
        entity_id=str(media_id),
    )
    await session.commit()
    product = await get_admin_product(session, product_id)
    return {"ok": True, "data": serialize_product_detail(product, admin=True)}


@router.patch("/variants/{variant_id}/inventory")
async def adjust_inventory(
    variant_id: UUID,
    payload: InventoryAdjust,
    identity: Identity = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    variant = await session.get(ProductVariant, variant_id)
    if variant is None:
        raise AppError("VARIANT_NOT_FOUND", "Варіант не знайдено", 404)
    inventory = await session.scalar(
        select(Inventory).where(Inventory.variant_id == variant_id).with_for_update()
    )
    now = datetime.now(UTC)
    if inventory is None:
        inventory = Inventory(
            variant_id=variant_id,
            quantity_on_hand=0,
            quantity_reserved=0,
            updated_at=now,
        )
        session.add(inventory)
        await session.flush()
    if payload.quantity_on_hand < inventory.quantity_reserved:
        raise AppError("INVENTORY_NEGATIVE", "Залишок не може бути меншим за резерв", 409)
    before = inventory.quantity_on_hand
    inventory.quantity_on_hand = payload.quantity_on_hand
    inventory.updated_at = now
    session.add(
        InventoryMovement(
            variant_id=variant_id,
            movement_type=payload.movement_type,
            quantity_delta=payload.quantity_on_hand - before,
            quantity_before=before,
            quantity_after=payload.quantity_on_hand,
            reason=payload.reason,
            created_by_user_id=identity.user.id,
            created_at=now,
        )
    )
    await write_audit(
        session,
        actor_user_id=identity.user.id,
        action="inventory.adjust",
        entity_type="variant",
        entity_id=str(variant_id),
        payload={"before": before, "after": payload.quantity_on_hand, "reason": payload.reason},
    )
    await session.commit()
    return {
        "ok": True,
        "data": {
            "variant_id": str(variant_id),
            "quantity_on_hand": inventory.quantity_on_hand,
            "quantity_reserved": inventory.quantity_reserved,
            "available_quantity": inventory.available_quantity,
        },
    }
