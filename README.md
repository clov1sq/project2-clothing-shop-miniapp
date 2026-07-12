# Project2 Telegram Fashion Store — v2 Visual Foundation

Нова самостійна візуальна версія Telegram Mini App для fashion e-commerce. Інтерфейс не використовує дизайн, компоненти чи UX старого Project 2.

## Що є у v2

- нова світла fashion design system на CSS variables;
- branded header і wordmark;
- editorial hero;
- preview-категорії та 6 локальних mock-товарів;
- нові product cards;
- каталог, кошик, профіль і admin preview;
- auth loading/error screens;
- skeleton, toast, status badge, empty state;
- Telegram safe area, Back Button і light haptics;
- адаптація 320–760 px і темна Telegram theme;
- FastAPI backend, PostgreSQL foundation та health checks.

Preview-товари не підключені до бази даних у v2.

## Railway

### Backend

- Root Directory: `/backend`
- Build Command: порожньо
- Start Command: порожньо

Railway використає `backend/Dockerfile`.

Backend variables:

```env
APP_ENV=production
SHOP_NAME=BlueWear
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
BACKEND_CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN.up.railway.app
MINI_APP_URL=https://YOUR-FRONTEND-DOMAIN.up.railway.app
TELEGRAM_BOT_TOKEN=
```

`BACKEND_CORS_ORIGINS` приймає як одну URL-адресу, так і JSON-масив.

### Frontend

- Root Directory: `/frontend`
- Build Command: `npm run build`
- Start Command: `npm run start`

Frontend variables:

```env
VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN.up.railway.app
VITE_SHOP_NAME=BlueWear
```

## Перевірка

Backend:

- `/health/live`
- `/health/ready`
- `/api/meta`

Frontend:

- `#/home`
- `#/catalog`
- `#/cart`
- `#/profile`
- `#/admin`
- `?auth=error` — preview auth error screen

## Local

```bash
cd frontend
npm ci
npm run build
npm run dev
```

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
