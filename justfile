# Blog + Newsletter Platform — Justfile
# Install `just` first: https://github.com/casey/just

set shell := ["bash", "-c"]

# Default recipe — shows all available commands
help:
    @just --list --unsorted

# ─────────────────────────────────────────────────────────────────────────────
# Environment & Dependencies
# ─────────────────────────────────────────────────────────────────────────────

# Create .env file from template
env:
    cp -n .env.example .env 2>/dev/null || echo ".env already exists"

# Install all Python + Node dependencies
install:
    source .venv/bin/activate && uv sync --frozen
    cd frontend && npm ci

# ─────────────────────────────────────────────────────────────────────────────
# Local Development (requires PostgreSQL running on localhost:5432)
# ─────────────────────────────────────────────────────────────────────────────

# Start PostgreSQL via Docker (if you don't have it running natively)
db:
    docker run -d --name blog-db \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=blog \
        -p 5432:5432 \
        postgres:16-alpine 2>/dev/null || docker start blog-db

# Run database migrations (local)
migrate:
    source .venv/bin/activate && alembic upgrade head

# Run database migrations (Docker dev)
migrate-docker:
    docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Start backend dev server (http://localhost:8000)
back:
    source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Start frontend dev server (http://localhost:5173)
front:
    cd frontend && npm run dev

# ─────────────────────────────────────────────────────────────────────────────
# Docker Compose (recommended — no local PostgreSQL needed)
# ─────────────────────────────────────────────────────────────────────────────

# Start full dev stack (Nginx on http://localhost)
dev:
    docker compose -f docker-compose.dev.yml up --build

# Start full dev stack in background
dev-up:
    docker compose -f docker-compose.dev.yml up --build -d

# View logs for dev stack
dev-logs:
    docker compose -f docker-compose.dev.yml logs -f

# Stop dev stack
dev-down:
    docker compose -f docker-compose.dev.yml down

# Stop dev stack and remove all data (volumes)
dev-clean:
    docker compose -f docker-compose.dev.yml down -v
    docker rm -f blog-db 2>/dev/null || true

# Start production stack
prod:
    docker compose -f docker-compose.prod.yml up --build

# ─────────────────────────────────────────────────────────────────────────────
# Testing & Quality
# ─────────────────────────────────────────────────────────────────────────────

# Run backend tests (pytest)
test:
    source .venv/bin/activate && pytest tests/ -v

# Run backend tests with coverage
test-cov:
    source .venv/bin/activate && pytest tests/ -v --cov=app --cov-report=term-missing

# Run frontend tests (Vitest)
test-front:
    cd frontend && npm test

# ─────────────────────────────────────────────────────────────────────────────
# Database Operations
# ─────────────────────────────────────────────────────────────────────────────

# Generate a new Alembic migration (requires models to be imported in alembic/env.py)
migration name:
    source .venv/bin/activate && alembic revision --autogenerate -m "{{name}}"

# Reset database (drop all tables and re-run migrations)
db-reset:
    source .venv/bin/activate && alembic downgrade base
    just migrate

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

# Build frontend for production
build-front:
    cd frontend && npm run build

# Clean generated files
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name '*.pyc' -delete 2>/dev/null || true
    rm -rf frontend/dist 2>/dev/null || true
