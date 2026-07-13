# Railway deployment

Project2 remains split into backend, frontend, bot and PostgreSQL services.

No domains, Start Commands, BotFather settings or required variables change in v0.5.0.

A normal Git push is enough. Backend startup runs `alembic upgrade head`, which applies `0005_checkout_reservations` before Uvicorn starts. The frontend continues to proxy `/api` to the existing `VITE_API_URL`, preserving the fixed session-cookie flow in Telegram WebView.
