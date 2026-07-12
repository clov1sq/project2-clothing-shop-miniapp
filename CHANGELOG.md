# Project 2 changelog

## 0.3.0-fix1

- Fixed React JSX type resolution during Railway production builds.
- Added pinned React type packages and regenerated the npm lock file.
- Kept strict TypeScript checks enabled and fixed catalog admin/variant selector typing.
- Updated the frontend production Docker build to install build dependencies and serve only `dist`.

# Changelog

## 0.3.0 — Catalog

### Added
- Telegram `initData` HMAC validation, auth-age validation, users, roles and DB sessions.
- `/start`, `/shop`, `/admin`, menu button and Mini App authorization bootstrap.
- Categories, brands, products, colors, sizes, variants, media and inventory models.
- Public home/catalog/product APIs with search, filters, sorting and pagination.
- Product detail variant-combination logic and availability read model.
- Mobile-first buyer UI: home, two-column catalog, filter/sort sheets and product gallery.
- Admin catalog CRUD, draft/publish/archive, media URLs, variants and inventory adjustments.
- Inventory movement journal, audit log and optimistic product version conflicts.
- Idempotent seed with 30 demo products and catalog tests.

### Database migrations
- `0002_auth`
- `0003_catalog`

### Compatibility
- Existing `BOT_TOKEN` remains supported.
- Both `VITE_API_URL` and `VITE_API_BASE_URL` are supported.
- Plain URL and JSON-like values are accepted for `BACKEND_CORS_ORIGINS`.

### Known limitations
- v3 intentionally excludes favorites, cart, checkout, orders, payments and delivery.
- Media management uses external HTTPS image URLs; persistent file upload storage is deferred.
