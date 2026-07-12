SHELL := /bin/sh
COMPOSE := docker compose

.PHONY: up down logs migrate seed backend-test backend-lint backend-typecheck frontend-test frontend-typecheck frontend-build test lint check

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) run --rm backend python -m alembic -c alembic.ini upgrade head

seed:
	$(COMPOSE) run --rm backend python -m app.seed

backend-test:
	$(COMPOSE) run --rm backend pytest -q

backend-lint:
	$(COMPOSE) run --rm backend ruff check app tests migrations

backend-typecheck:
	$(COMPOSE) run --rm backend mypy app

frontend-test:
	$(COMPOSE) run --rm frontend npm test

frontend-typecheck:
	$(COMPOSE) run --rm frontend npm run typecheck

frontend-build:
	$(COMPOSE) run --rm frontend npm run build

test: backend-test frontend-test

lint: backend-lint backend-typecheck frontend-typecheck

check: lint test frontend-build
