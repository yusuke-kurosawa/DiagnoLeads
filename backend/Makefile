# DiagnoLeads Backend Makefile

.PHONY: help seed seed-clean seed-test migrate upgrade downgrade test lint format

help:
	@echo "DiagnoLeads Backend Commands"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         - Create new migration"
	@echo "  make upgrade         - Run migrations"
	@echo "  make downgrade       - Rollback last migration"
	@echo ""
	@echo "Seeding:"
	@echo "  make seed            - Seed development data"
	@echo "  make seed-clean      - Clean and re-seed development data"
	@echo "  make seed-test       - Seed test data"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run tests"
	@echo "  make test-cov        - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linter"
	@echo "  make format          - Format code"
	@echo "  make type-check      - Run type checker"

# Database Migrations
migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

# Seeding
seed:
	python seed_database.py --env development

seed-clean:
	python seed_database.py --env development --clean --force

seed-test:
	python seed_database.py --env test

# Testing
test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

# Code Quality
lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy .
