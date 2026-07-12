# Project checks

Backend tests live in `backend/tests`. Frontend catalog logic tests live in `frontend/tests`.

The CI workflow runs lint, Python typecheck, backend tests, migration upgrade/downgrade, idempotent seed, bot no-token startup, frontend typecheck, frontend tests and the Vite production build.
