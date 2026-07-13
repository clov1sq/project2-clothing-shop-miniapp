# Project 2 changelog

## 0.4.1 — Session authentication fix

- Fixed cross-origin session cookie delivery by proxying `/api` through the frontend origin.
- Centralized `credentials: "include"` for every frontend API request.
- Added `POST /auth/telegram` → `GET /auth/me` bootstrap verification.
- Gated cart and favorites queries until authentication is confirmed.
- Added a single controlled session refresh and one protected-request retry on 401.
- Standardized the host-only `project2_session` cookie and logout deletion settings.
- Added session integration and frontend auth-flow tests.


## 0.4.0 — Favorites & Cart

- Added server-side favorites with idempotent add/remove operations.
- Added one active cart per user and unique cart item per variant.
- Added current price, stock and availability validation on every cart read and mutation.
- Added `Idempotency-Key` protection against double tap and network retries.
- Added price-change and out-of-stock states without silently deleting cart items.
- Added `/favorites` and `/cart`, favorite actions, quantity controls, cart summary and navigation badge.
- Added migration `0004_favorites_cart`, backend coverage and frontend commerce contract tests.
- Preserved the strict React/TypeScript production build fixed in `project2_v3_fix1`.

## 0.3.0-fix1

- Fixed React JSX type resolution during Railway production builds.
- Added pinned React type packages and regenerated the npm lock file.
- Kept strict TypeScript checks enabled and fixed catalog admin/variant selector typing.
- Updated the frontend production Docker build to install build dependencies and serve only `dist`.


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
