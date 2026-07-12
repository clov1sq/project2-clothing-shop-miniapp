# Railway deployment

No new Railway project is required.

## Services

### backend

- Root Directory: `/backend`
- Uses `backend/Dockerfile`
- Build Command: empty when Dockerfile detection is enabled
- Start Command: empty so Docker `CMD` runs

`start.sh` automatically migrates, seeds and starts Uvicorn on `$PORT`.

### bot

- Root Directory: `/backend`
- Existing Start Command: `python -m app.bot.main`

### frontend

- Root Directory: `/frontend`
- Existing Build Command may stay `npm run build`
- Existing Start Command may stay `npm run start`

## Health checks

- `/health/live`
- `/health/ready`
- `/health/db`

## Deployment order

A normal Git push is enough. The backend migration is additive: `0002_auth` then `0003_catalog`. Seed is safe to repeat.
