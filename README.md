# Project2 Telegram Clothing Store — v1 Foundation

Clean v2 foundation for a Telegram Mini App clothing store. This repository intentionally does not reuse legacy Project 2 code.

## What is included in v1

- FastAPI backend shell.
- Aiogram 3 bot shell.
- PostgreSQL async infrastructure.
- SQLAlchemy 2.x Async + Alembic.
- React + TypeScript + Vite frontend shell.
- Basic Telegram Mini App integration wrapper.
- Docker Compose local stack.
- Health checks, structured JSON logging, seed infrastructure and tests.

Not included yet: Telegram auth, catalog, cart, checkout, payments, orders and admin business flows.

## Quick start

1. Copy environment file:

```bash
cp .env.example .env
```

2. Start local services:

```bash
docker compose up --build
```

3. Apply migrations:

```bash
docker compose run --rm backend alembic -c alembic.ini upgrade head
```

4. Seed minimal foundation data:

```bash
docker compose run --rm backend python -m app.seed
```

5. Open services:

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health/live
- Backend readiness: http://localhost:8000/health/ready

## Make shortcuts

```bash
make up
make down
make logs
make migrate
make seed
make test
make lint
make check
```

## Windows / PowerShell commands

`make` is optional. Use Docker Compose directly:

```powershell
Copy-Item .env.example .env

docker compose up --build

docker compose run --rm backend alembic -c alembic.ini upgrade head

docker compose run --rm backend python -m app.seed

docker compose run --rm backend pytest -q

docker compose run --rm frontend npm run typecheck
```

## Telegram bot token

`TELEGRAM_BOT_TOKEN` is intentionally empty in `.env.example`.

- Without a token, the bot container exits cleanly with a clear warning.
- With a token, the bot starts polling.
- Telegram auth and production webhook mode are planned for v2/v9.

## Environment variables

See `.env.example`. Do not commit a real `.env`.

## Database

Alembic migrations are stored in `backend/migrations`.

Foundation migration:

- `0001_foundation.py` creates `app_metadata`.

## Version

Current version: `0.1.0`.
