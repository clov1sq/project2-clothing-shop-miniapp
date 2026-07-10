# Foundation notes

## Scope

v1 creates the project foundation only. Business modules are intentionally empty or represented by safe extension points.

## Architecture

- Modular monolith.
- FastAPI backend and Aiogram bot live in the same Python codebase.
- React Mini App is a separate Vite frontend.
- PostgreSQL is the only required infrastructure dependency.

## Non-goals in v1

- Telegram auth.
- Product catalog.
- Cart and checkout.
- Payments.
- Admin workflows.
- Object storage.
