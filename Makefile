SHELL := /bin/sh
COMPOSE := docker compose

.PHONY: up down logs migrate seed test lint format check backend-test frontend-typecheck frontend-build

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) run --rm backend alembic -c alembic.ini upgrade head

seed:
	$(COMPOSE) run --rm backend python -m app.seed

backend-test:
	$(COMPOSE) run --rm backend pytest -q

frontend-typecheck:
	$(COMPOSE) run --rm frontend npm run typecheck

frontend-build:
	$(COMPOSE) run --rm frontend npm run build

test: backend-test frontend-typecheck

lint:
	$(COMPOSE) run --rm backend python -m compileall app tests
	$(COMPOSE) run --rm frontend npm run lint

format:
	$(COMPOSE) run --rm backend python -m compileall app tests
	$(COMPOSE) run --rm frontend npm run format

check: lint test frontend-build
