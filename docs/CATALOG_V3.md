# Catalog v3

## Scope

Version 0.3.0 is the cumulative foundation + Telegram auth + catalog release.

### Buyer

- Home aggregate endpoint and editorial home screen.
- Active categories and brands.
- Catalog pagination, search, filters and deterministic sorting.
- Stable product cards with cover image, NEW/SALE and availability.
- Product gallery, valid color/size combinations and stock read model.

### Admin

- Server-side session and role enforcement.
- Product draft creation, editing, publishing and soft archive.
- Category and brand creation/editing APIs.
- Variant creation/editing/archive.
- External HTTPS photo URL management and ordering API.
- Transactional inventory correction with row lock, movement and audit log.
- Optimistic product version check returning `409 CONCURRENT_UPDATE_CONFLICT`.

## Public API

- `GET /api/v1/home`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/brands`
- `GET /api/v1/catalog/meta`
- `GET /api/v1/products`
- `GET /api/v1/products/{slug}`

## Catalog query parameters

`page`, `limit`, `category`, `brand`, `color`, `size`, `min_price`, `max_price`, `only_available`, `sale`, `new`, `search`, `sort`.

Sort values: `popular`, `newest`, `price_asc`, `price_desc`, `discount`.

## Error codes

Implemented errors include:

- `CATEGORY_NOT_FOUND`
- `BRAND_NOT_FOUND`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_NOT_ACTIVE`
- `VARIANT_NOT_FOUND`
- `INVENTORY_NEGATIVE`
- `PRODUCT_SLUG_EXISTS`
- `PRODUCT_SKU_EXISTS`
- `ADMIN_ACCESS_REQUIRED`
- `CONCURRENT_UPDATE_CONFLICT`

## Seed

`python -m app.seed` is deterministic and idempotent. It does not delete admin-created data. It upserts the demo catalog by stable slugs/codes/SKUs.
