.PHONY: help install install-dev lint format type-check test test-unit test-integration \
        test-e2e coverage run clean pre-commit docker-up docker-down docker-build

# ---------------------------------------------------------------------------
# Default target
# ---------------------------------------------------------------------------
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
install: ## Install production dependencies
	pip install -e .

install-dev: ## Install all dependencies including dev and lint extras
	pip install -e ".[all]"
	pre-commit install

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------
lint: ## Run Ruff linter
	ruff check .

lint-fix: ## Run Ruff linter with auto-fix
	ruff check --fix .

format: ## Format code with Black and isort
	black .
	isort .

format-check: ## Check formatting without applying changes
	black --check .
	isort --check-only .

type-check: ## Run MyPy static type checker
	mypy .

check: lint format-check type-check ## Run all quality checks (no fixes)

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------
test: ## Run all tests
	pytest tests/

test-unit: ## Run unit tests only
	pytest tests/unit/ -m unit

test-integration: ## Run integration tests only
	pytest tests/integration/ -m integration

test-e2e: ## Run end-to-end tests only
	pytest tests/e2e/ -m e2e

coverage: ## Run tests with coverage report
	pytest --cov --cov-report=term-missing --cov-report=html tests/

coverage-report: ## Open HTML coverage report
	open htmlcov/index.html

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
run: ## Start the development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port $${APP_PORT:-8000}

run-dev: ## Start dev server with verbose logging
	uvicorn app.main:app --reload --host 0.0.0.0 --port $${APP_PORT:-8000} --log-level debug

# ---------------------------------------------------------------------------
# Pre-commit
# ---------------------------------------------------------------------------
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start Docker services
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## Tail Docker service logs
	docker compose logs -f

docker-reset: ## Stop services, remove volumes, rebuild
	docker compose down -v
	docker compose build
	docker compose up -d

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------
clean: ## Remove build artefacts, caches, and compiled files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete 2>/dev/null; true
	find . -type f -name "*.pyo" -delete 2>/dev/null; true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name ".coverage" -delete 2>/dev/null; true
	echo "Cleaned."
