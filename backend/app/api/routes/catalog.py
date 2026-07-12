from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Brand, Category, Color, Product, Size
from app.catalog.service import (
    PRODUCT_LOAD_OPTIONS,
    get_public_product,
    list_products,
    serialize_brand,
    serialize_category,
    serialize_product_card,
    serialize_product_detail,
)
from app.core.errors import AppError
from app.db.session import get_session

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get("/home")
async def home(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    categories = list(
        (
            await session.scalars(
                select(Category)
                .where(Category.is_active.is_(True))
                .order_by(Category.sort_order, Category.name)
                .limit(8)
            )
        ).all()
    )

    async def load_products(*conditions, limit: int = 8):
        statement = (
            select(Product)
            .options(*PRODUCT_LOAD_OPTIONS)
            .where(Product.status == "active", Product.archived_at.is_(None), *conditions)
            .order_by(Product.published_at.desc().nullslast(), Product.name)
            .limit(limit)
        )
        return [
            serialize_product_card(item)
            for item in (await session.scalars(statement)).unique().all()
        ]

    new_products = await load_products(Product.is_new.is_(True))
    sale_products = await load_products(
        and_(Product.compare_at_price.is_not(None), Product.compare_at_price > Product.base_price)
    )
    featured_products = await load_products(Product.is_featured.is_(True))
    return {
        "ok": True,
        "data": {
            "categories": [serialize_category(item) for item in categories],
            "new_products": new_products,
            "sale_products": sale_products,
            "featured_products": featured_products,
        },
    }


@router.get("/categories")
async def categories(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    items = list(
        (
            await session.scalars(
                select(Category)
                .where(Category.is_active.is_(True))
                .order_by(Category.sort_order, Category.name)
            )
        ).all()
    )
    return {"ok": True, "data": {"items": [serialize_category(item) for item in items]}}


@router.get("/categories/{slug}")
async def category_detail(
    slug: str, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    item = await session.scalar(
        select(Category).where(Category.slug == slug, Category.is_active.is_(True))
    )
    if item is None:
        raise AppError("CATEGORY_NOT_FOUND", "Категорію не знайдено", 404)
    return {"ok": True, "data": serialize_category(item)}


@router.get("/brands")
async def brands(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    items = list(
        (
            await session.scalars(
                select(Brand).where(Brand.is_active.is_(True)).order_by(Brand.name)
            )
        ).all()
    )
    return {"ok": True, "data": {"items": [serialize_brand(item) for item in items]}}


@router.get("/catalog/meta")
async def catalog_meta(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    categories_result = await session.scalars(
        select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order)
    )
    brands_result = await session.scalars(
        select(Brand).where(Brand.is_active.is_(True)).order_by(Brand.name)
    )
    colors_result = await session.scalars(
        select(Color).where(Color.is_active.is_(True)).order_by(Color.sort_order)
    )
    sizes_result = await session.scalars(
        select(Size).where(Size.is_active.is_(True)).order_by(Size.sort_order)
    )
    return {
        "ok": True,
        "data": {
            "categories": [serialize_category(item) for item in categories_result.all()],
            "brands": [serialize_brand(item) for item in brands_result.all()],
            "colors": [
                {
                    "id": str(item.id),
                    "name": item.name,
                    "code": item.code,
                    "hex_value": item.hex_value,
                }
                for item in colors_result.all()
            ],
            "sizes": [
                {"id": str(item.id), "name": item.name, "code": item.code}
                for item in sizes_result.all()
            ],
            "sorts": ["popular", "newest", "price_asc", "price_desc", "discount"],
        },
    }


@router.get("/products")
async def products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=60),
    category: str | None = None,
    brand: str | None = None,
    color: str | None = None,
    size: str | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    only_available: bool = False,
    sale: bool = False,
    new: bool = False,
    search: str | None = Query(default=None, max_length=120),
    sort: str = Query(
        default="popular", pattern="^(popular|newest|price_asc|price_desc|discount)$"
    ),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise AppError("INVALID_FILTER", "Мінімальна ціна не може перевищувати максимальну", 422)
    data = await list_products(
        session,
        page=page,
        limit=limit,
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
        sort=sort,
    )
    return {"ok": True, "data": data}


@router.get("/products/{slug}")
async def product_detail(
    slug: str, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    product = await get_public_product(session, slug)
    return {"ok": True, "data": serialize_product_detail(product)}
