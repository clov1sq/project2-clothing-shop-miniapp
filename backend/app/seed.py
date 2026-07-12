import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.auth import models as auth_models  # noqa: F401
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
from app.db.base import AppMetadata
from app.db.session import get_sessionmaker

CATEGORIES = [
    ("Новинки", "new", "Свіжі силуети й сезонні акценти", 10),
    ("Одяг", "clothing", "Базові та акцентні речі на щодень", 20),
    ("Взуття", "shoes", "Міські пари для активного ритму", 30),
    ("Аксесуари", "accessories", "Деталі, що завершують образ", 40),
    ("Спорт", "sport", "Функціональний одяг і взуття", 50),
    ("Sale", "sale", "Обрані моделі зі знижками", 60),
]
BRANDS = [
    ("North Form", "north-form"),
    ("Aster Line", "aster-line"),
    ("Urban Loom", "urban-loom"),
    ("Mono Field", "mono-field"),
    ("Pace Studio", "pace-studio"),
    ("Cobalt Room", "cobalt-room"),
]
COLORS = [
    ("Чорний", "black", "#15171A"),
    ("Молочний", "ivory", "#F0EBDD"),
    ("Графіт", "graphite", "#4A4D52"),
    ("Синій", "cobalt", "#1747D1"),
    ("Бежевий", "sand", "#C9B89F"),
    ("Оливковий", "olive", "#6E7352"),
    ("Бордовий", "wine", "#742B3A"),
    ("Сірий", "grey", "#A7ABB1"),
]
SIZES = [
    ("XS", "xs"),
    ("S", "s"),
    ("M", "m"),
    ("L", "l"),
    ("XL", "xl"),
    ("36", "36"),
    ("37", "37"),
    ("38", "38"),
    ("39", "39"),
    ("40", "40"),
    ("41", "41"),
    ("42", "42"),
    ("One size", "one-size"),
]
IMAGES = [
    "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1551232864-3f0890e580d9?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?auto=format&fit=crop&w=900&q=82",
    "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=82",
]
PRODUCT_NAMES = [
    "Пальто прямого крою",
    "Куртка міська легка",
    "Сорочка структурна",
    "Джемпер із м’якої пряжі",
    "Штани широкого силуету",
    "Сукня мінімалістична",
    "Жакет укорочений",
    "Худі базове",
    "Спідниця плісирована",
    "Футболка щільна",
    "Тренч водовідштовхувальний",
    "Кардиган фактурний",
    "Кросівки міські",
    "Кеди шкіряні",
    "Черевики демісезонні",
    "Лофери лаконічні",
    "Сумка геометрична",
    "Рюкзак компактний",
    "Шарф м’який",
    "Кепка структурна",
    "Костюм тренувальний",
    "Легінси спортивні",
    "Топ функціональний",
    "Вітровка бігова",
    "Світшот relaxed",
    "Шорти технічні",
    "Поло трикотажне",
    "Бомбер сучасний",
    "Комбінезон міський",
    "Жилет утеплений",
]


async def get_or_create(session, model, lookup: dict, defaults: dict):
    item = await session.scalar(select(model).filter_by(**lookup))
    if item is None:
        item = model(**lookup, **defaults)
        session.add(item)
        await session.flush()
    else:
        for key, value in defaults.items():
            setattr(item, key, value)
    return item


async def seed() -> None:
    maker = get_sessionmaker()
    async with maker() as session:
        now = datetime.now(UTC)
        categories = {}
        for name, slug, description, order in CATEGORIES:
            categories[slug] = await get_or_create(
                session,
                Category,
                {"slug": slug},
                {
                    "name": name,
                    "description": description,
                    "image_url": IMAGES[order // 10 - 1],
                    "sort_order": order,
                    "is_active": True,
                    "parent_id": None,
                },
            )
        brands = {}
        for _index, (name, slug) in enumerate(BRANDS):
            brands[slug] = await get_or_create(
                session,
                Brand,
                {"slug": slug},
                {
                    "name": name,
                    "description": "Незалежний demo-бренд із сучасною міською естетикою.",
                    "logo_url": None,
                    "is_active": True,
                },
            )
        colors = {}
        for index, (name, code, hex_value) in enumerate(COLORS):
            colors[code] = await get_or_create(
                session,
                Color,
                {"code": code},
                {"name": name, "hex_value": hex_value, "sort_order": index * 10, "is_active": True},
            )
        sizes = {}
        for index, (name, code) in enumerate(SIZES):
            sizes[code] = await get_or_create(
                session,
                Size,
                {"code": code},
                {"name": name, "sort_order": index * 10, "is_active": True},
            )

        category_cycle = [
            "clothing",
            "clothing",
            "clothing",
            "clothing",
            "shoes",
            "accessories",
            "sport",
        ]
        brand_slugs = [slug for _, slug in BRANDS]
        apparel_sizes = ["xs", "s", "m", "l", "xl"]
        shoe_sizes = ["37", "38", "39", "40", "41", "42"]
        for index, name in enumerate(PRODUCT_NAMES):
            category_slug = category_cycle[index % len(category_cycle)]
            if index < 5:
                category_slug = "new"
            if index in {4, 9, 14, 19, 24, 29}:
                category_slug = "sale"
            brand_slug = brand_slugs[index % len(brand_slugs)]
            slug = f"{category_slug}-{index + 1:02d}"
            base_price = Decimal(1190 + (index % 10) * 310)
            compare = base_price + Decimal(700 + (index % 4) * 250) if index % 3 == 0 else None
            status = "active"
            archived_at = None
            published_at: datetime | None = now - timedelta(days=index)
            if index in {26, 27, 28}:
                status = "draft"
                published_at = None
            if index == 29:
                status = "archived"
                archived_at = now - timedelta(days=1)
            product = await get_or_create(
                session,
                Product,
                {"slug": slug},
                {
                    "category_id": categories[category_slug].id,
                    "brand_id": brands[brand_slug].id,
                    "name": name,
                    "model_code": f"BW-{index + 1:04d}",
                    "short_description": "Чистий силует, комфортна посадка та продумані деталі.",
                    "description": "Модель створена для щоденного міського гардероба. Лаконічна форма легко поєднується з базовими речами та акцентними аксесуарами.",
                    "material": "Комбінований текстиль преміальної щільності.",
                    "care_instructions": "Делікатне прання або професійне чищення згідно з етикеткою.",
                    "base_price": base_price,
                    "compare_at_price": compare,
                    "currency": "UAH",
                    "status": status,
                    "is_featured": index % 4 == 0,
                    "is_new": index < 10,
                    "version": 1,
                    "published_at": published_at,
                    "archived_at": archived_at,
                },
            )
            existing_media = await session.scalar(
                select(ProductMedia).where(
                    ProductMedia.product_id == product.id, ProductMedia.is_primary.is_(True)
                )
            )
            if existing_media is None:
                session.add(
                    ProductMedia(
                        product_id=product.id,
                        variant_id=None,
                        media_type="image",
                        url=IMAGES[index % len(IMAGES)],
                        thumbnail_url=IMAGES[index % len(IMAGES)],
                        alt_text=name,
                        sort_order=10,
                        is_primary=True,
                        created_at=now,
                    )
                )
                session.add(
                    ProductMedia(
                        product_id=product.id,
                        variant_id=None,
                        media_type="image",
                        url=IMAGES[(index + 3) % len(IMAGES)],
                        thumbnail_url=IMAGES[(index + 3) % len(IMAGES)],
                        alt_text=f"{name}, інший ракурс",
                        sort_order=20,
                        is_primary=False,
                        created_at=now,
                    )
                )
            product_size_codes = shoe_sizes if category_slug == "shoes" else apparel_sizes
            if category_slug == "accessories":
                product_size_codes = ["one-size"]
            color_codes = [COLORS[index % len(COLORS)][1], COLORS[(index + 3) % len(COLORS)][1]]
            combinations = []
            for color_code in color_codes:
                for size_code in product_size_codes[:2]:
                    combinations.append((color_code, size_code))
            for variant_index, (color_code, size_code) in enumerate(combinations):
                sku = f"BW-{index + 1:04d}-{color_code[:3].upper()}-{size_code.upper()}"
                variant = await session.scalar(
                    select(ProductVariant).where(ProductVariant.sku == sku)
                )
                if variant is None:
                    variant = ProductVariant(
                        product_id=product.id,
                        color_id=colors[color_code].id,
                        size_id=sizes[size_code].id,
                        sku=sku,
                        barcode=None,
                        price_override=None,
                        compare_at_price_override=None,
                        is_active=status != "archived",
                        archived_at=archived_at,
                    )
                    session.add(variant)
                    await session.flush()
                inventory = await session.scalar(
                    select(Inventory).where(Inventory.variant_id == variant.id)
                )
                quantity = (
                    0
                    if (index + variant_index) % 9 == 0
                    else (
                        2
                        if (index + variant_index) % 7 == 0
                        else 8 + ((index + variant_index) % 13)
                    )
                )
                if inventory is None:
                    inventory = Inventory(
                        variant_id=variant.id,
                        quantity_on_hand=quantity,
                        quantity_reserved=0,
                        updated_at=now,
                    )
                    session.add(inventory)
                    session.add(
                        InventoryMovement(
                            variant_id=variant.id,
                            movement_type="initial",
                            quantity_delta=quantity,
                            quantity_before=0,
                            quantity_after=quantity,
                            reason="Seed catalog",
                            created_by_user_id=None,
                            created_at=now,
                        )
                    )

        metadata = await session.get(AppMetadata, "seed_version")
        if metadata is None:
            session.add(AppMetadata(key="seed_version", value="catalog-v3"))
        else:
            metadata.value = "catalog-v3"
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
