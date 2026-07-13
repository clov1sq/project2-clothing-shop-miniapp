# Project2 Telegram Fashion Store — v5 Checkout

Повна накопичувальна версія Telegram fashion-магазину на базі стабільної `project2_v4_fix1`.

## Реалізовано

- FastAPI, PostgreSQL, SQLAlchemy Async, Alembic і Aiogram 3.
- Telegram `initData`, серверні сесії та first-party `/api` proxy для cookie у Telegram WebView.
- Каталог, категорії, бренди, товари, variants/SKU, фото й залишки.
- Обране та серверний кошик із перевіркою актуальної ціни й доступності.
- Checkout: контакти, спосіб отримання, review, підтвердження та result screen.
- Замовлення зі snapshot товару, бренду, SKU, кольору, розміру, ціни та фото.
- Резервування залишків на 15 хвилин через PostgreSQL row locks.
- `Idempotency-Key` для захисту від double tap і повторного network retry.
- Background task у backend для ідемпотентного завершення прострочених резервів.
- Захист останньої одиниці: `SELECT ... FOR UPDATE` доповнено атомарним conditional update залишку.
- Візуальні виправлення badge, selected size, accordion і scroll restoration.

У v5 реальна онлайн-оплата ще не підключена. Створене замовлення має статус `awaiting_payment`, а резерв автоматично завершується через 15 хвилин.

## Checkout API

- `POST /api/v1/checkout/validate`
- `POST /api/v1/checkout/confirm` — обов’язковий `Idempotency-Key`
- `GET /api/v1/checkout/orders/{order_id}`

Користувач бачить лише власні замовлення.

## Railway

Структуру сервісів, домени та Start Commands змінювати не потрібно:

- backend: Root Directory `/backend`;
- bot: Root Directory `/backend`;
- frontend: Root Directory `/frontend`;
- PostgreSQL: чинний Railway service.

Backend `start.sh` автоматично виконує:

1. `alembic upgrade head`;
2. idempotent seed;
3. Uvicorn на `$PORT`.

Для v5 нових обов’язкових variables немає. Потрібна міграція `0005_checkout_reservations`, яка застосовується автоматично під час deployment backend.

## Production variables

### Backend і bot

```env
APP_ENV=production
SHOP_NAME=BlueWear
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
BACKEND_CORS_ORIGINS=https://YOUR-FRONTEND.up.railway.app
MINI_APP_URL=https://YOUR-FRONTEND.up.railway.app
BOT_TOKEN=YOUR_TELEGRAM_TOKEN
ADMIN_TELEGRAM_IDS=YOUR_TELEGRAM_ID
TELEGRAM_AUTH_MAX_AGE_SECONDS=86400
SESSION_COOKIE_NAME=project2_session
SESSION_TTL_DAYS=14
DEV_AUTH_ENABLED=false
```

### Frontend

```env
VITE_API_URL=https://YOUR-BACKEND.up.railway.app
VITE_API_BASE_URL=https://YOUR-BACKEND.up.railway.app
VITE_SHOP_NAME=BlueWear
```

## Локальний запуск

```bash
cp .env.example .env
docker compose up --build
```

Адреси:

- frontend: `http://localhost:5173`;
- API live: `http://localhost:8000/health/live`;
- database readiness: `http://localhost:8000/health/ready`;
- OpenAPI: `http://localhost:8000/docs`.

## Перевірки

```bash
cd backend
ruff check app tests
mypy app
pytest -q

cd ../frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

## Міграції

- `0001_foundation`
- `0002_auth`
- `0003_catalog`
- `0004_favorites_cart`
- `0005_checkout_reservations`

Докладніше: `docs/CHECKOUT_V5.md`.

## Версія

`0.5.0`
