# Project2 Telegram Fashion Store — v3 Catalog

Повна накопичувальна версія Telegram fashion-магазину: foundation + Telegram auth + каталог + базове адміністрування каталогу.

## Реалізовано

- FastAPI, PostgreSQL, SQLAlchemy Async та Alembic.
- Aiogram-бот із `/start`, `/shop`, `/admin` і Telegram menu button.
- Перевірка Telegram `initData`, строку `auth_date`, серверні сесії та admin role.
- Категорії, бренди, товари, кольори, розміри, варіанти, фото й залишки.
- Головна, каталог, пошук, фільтри, сортування, pagination і сторінка товару.
- Mobile-first admin routes для товарів, категорій, брендів, фото та залишків.
- Audit log, inventory movements, soft archive та optimistic concurrency.
- Детермінований idempotent seed: 6 категорій, 6 брендів, 30 товарів, 114 варіантів.

Не входять у v3: кошик, обране, checkout, замовлення, оплата й доставка.

## Railway

Структуру сервісів змінювати не потрібно:

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

## Обов’язкові production variables

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

Після зміни frontend variables потрібен новий build frontend service.

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

`DEV_AUTH_ENABLED=true` дозволяє локально відкрити frontend без Telegram. У production він має бути `false`.

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
npm test
npm run build
```

## Міграції та seed

- `0001_foundation` — system metadata;
- `0002_auth` — users, roles, sessions, audit log;
- `0003_catalog` — catalog, variants, media, inventory та movements.

Seed запускається окремо від migration і є безпечним для повторного запуску:

```bash
cd backend
python -m app.seed
```

## Медіа у v3

Seed використовує зовнішні demo photo URLs. Адмін додає фото через HTTPS URL. Постійне S3-compatible file storage не вмикається автоматично, тому Railway ephemeral disk не використовується для збереження фото.

## Версія

`0.3.0`
