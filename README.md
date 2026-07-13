# Project2 Telegram Fashion Store — v4 Favorites & Cart

Повна накопичувальна версія Telegram fashion-магазину на базі стабільної `project2_v3_fix1`: foundation, Telegram auth, каталог, admin, обране і серверний кошик.

## Реалізовано

- FastAPI, PostgreSQL, SQLAlchemy Async та Alembic.
- Aiogram-бот із `/start`, `/shop`, `/admin` і Telegram menu button.
- Telegram `initData`, серверні сесії, ролі користувача й адміністратора.
- Категорії, бренди, товари, кольори, розміри, variants/SKU, фото та залишки.
- Головна, каталог, пошук, фільтри, сортування та сторінка товару.
- Обране з idempotent add/remove та підтримкою недоступних товарів.
- Серверний кошик із конкретним variant, quantity 1–10, актуальною ціною та перевіркою залишку.
- Захист додавання в кошик через `Idempotency-Key`.
- Виявлення зміни ціни й залишку без автоматичного видалення позицій.
- Badge кошика, mobile-first екрани `/favorites` і `/cart`, loading/empty/error states.
- Mobile-first admin routes, audit log, inventory movements і soft archive.
- Детермінований idempotent seed каталогу.

Не входять у v4: checkout, дані одержувача, доставка, замовлення, резервування, оплата, промокоди й бонуси.

## Railway

Структуру сервісів і чинні домени змінювати не потрібно:

- backend: Root Directory `/backend`;
- bot: Root Directory `/backend`;
- frontend: Root Directory `/frontend`;
- PostgreSQL: наявний Railway service.

Backend `Dockerfile` запускає `backend/start.sh`, який автоматично виконує:

1. `alembic upgrade head`;
2. idempotent seed;
3. Uvicorn на `$PORT`.

Bot service може залишатися з чинною Start Command:

```text
python -m app.bot.main
```

Frontend може залишатися з чинною Start Command:

```text
npm run start
```

Нових Railway variables для v4 немає.

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
SESSION_COOKIE_NAME=p2_session
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
make check
```

Або окремо:

```bash
cd backend
ruff check app tests migrations
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

- `0001_foundation` — system metadata;
- `0002_auth` — users, roles, sessions, audit log;
- `0003_catalog` — catalog, variants, media, inventory;
- `0004_favorites_cart` — favorites, carts, cart items та idempotency keys.

Докладніше: `docs/COMMERCE_V4.md`.

## Версія

`0.4.0`
