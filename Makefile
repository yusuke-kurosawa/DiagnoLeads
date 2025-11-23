# DiagnoLeads Project Makefile

.PHONY: help setup up down logs seed seed-clean test

help:
	@echo "DiagnoLeads Project Commands"
	@echo ""
	@echo "Docker:"
	@echo "  make setup           - Initial setup (build images)"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make logs            - View logs"
	@echo "  make restart         - Restart all services"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         - Run database migrations"
	@echo "  make seed            - Seed database with development data"
	@echo "  make seed-clean      - Clean and re-seed database"
	@echo "  make db-reset        - Reset database (migrate + seed)"
	@echo ""
	@echo "Development:"
	@echo "  make shell-backend   - Open backend shell"
	@echo "  make shell-frontend  - Open frontend shell"
	@echo "  make shell-db        - Open database shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests"

# Docker Commands
setup:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

# Database Commands
migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python seed_database.py --env development

seed-clean:
	docker compose exec backend python seed_database.py --env development --clean --force

db-reset: migrate seed
	@echo "✅ Database reset complete!"

# Development Shells
shell-backend:
	docker compose exec backend bash

shell-frontend:
	docker compose exec frontend sh

shell-db:
	docker compose exec postgres psql -U postgres -d diagnoleads

# Testing
test:
	docker compose exec backend pytest
	docker compose exec frontend npm test
