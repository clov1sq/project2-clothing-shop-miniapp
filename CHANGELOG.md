# Changelog

## 0.1.0 — Foundation

### Added
- Monorepo foundation with backend, frontend, infra, docs and tests.
- FastAPI application shell with health endpoints.
- Aiogram 3 bot process shell with safe no-token behavior.
- PostgreSQL async infrastructure with SQLAlchemy 2.x and Alembic.
- React/TypeScript/Vite Mini App shell with base navigation, design tokens and error boundary.
- Docker Compose local stack for PostgreSQL, backend API, bot and frontend.
- Makefile shortcuts and Windows-compatible README commands.
- Seed infrastructure without full catalog data.
- GitHub Actions CI workflow draft for backend and frontend checks.

### Changed
- New clean v2 architecture; no legacy Project 2 code is used.

### Fixed
- Not applicable in first release.

### Database migrations
- `0001_foundation`: creates `app_metadata` for foundation/system metadata.

### New environment variables
- `APP_ENV`
- `LOG_LEVEL`
- `SHOP_NAME`
- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `MINI_APP_URL`
- `FRONTEND_PORT`

### Known limitations
- Telegram auth, catalog, cart, checkout, payments and orders are intentionally not implemented in v1.
- Bot requires `TELEGRAM_BOT_TOKEN` to start polling; without it the bot process exits with a clear warning.
- Frontend shows shell screens and placeholders only.
