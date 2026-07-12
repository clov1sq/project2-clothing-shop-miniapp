#!/bin/sh
set -eu
python -m alembic -c alembic.ini upgrade head
python -m app.seed
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
