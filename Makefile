# Makefile for Nvisy Python SDK

ifneq (,$(wildcard ./.env))
	include .env
	export
endif

# Environment variables with defaults
OPENAPI_ENDPOINT ?= https://api.nvisy.com/openapi.json
OPENAPI_ENDPOINT_LOCAL ?= http://127.0.0.1:8080/api/openapi.json
OPENAPI_OUTPUT_DIR ?= openapi
OPENAPI_FILENAME ?= nvisy-api.json
GENERATED_MODELS ?= src/nvisy/datatypes.py
PYTHON_VERSION ?= 3.11

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Make-level logger
define log
	@echo "$(BLUE)[$(shell date '+%Y-%m-%d %H:%M:%S')] $(GREEN)[MAKE]$(NC) $(1)"
endef

.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	$(call log,Available targets:)
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  install       - Install dependencies with uv"
	@echo "  install-dev   - Install development dependencies"
	@echo "  setup         - Install development dependencies"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  format        - Format code with ruff"
	@echo "  lint          - Lint code with ruff"
	@echo "  type-check    - Run mypy type checking"
	@echo "  check         - Run all checks (format, lint, type-check)"
	@echo "  test          - Run tests with pytest"
	@echo "  test-cov      - Run tests with coverage report"
	@echo ""
	@echo "$(YELLOW)OpenAPI:$(NC)"
	@echo "  generate       - Download spec from production and generate datatypes"
	@echo "  generate-local - Download spec from local API server and generate datatypes"
	@echo "  check-remote   - Check connection to production API"
	@echo "  check-local    - Check connection to local API server"
	@echo "  download-spec  - Download OpenAPI specification only"
	@echo ""
	@echo "$(YELLOW)Build & Deploy:$(NC)"
	@echo "  build         - Build package"
	@echo "  publish       - Publish to PyPI"
	@echo "  publish-test  - Publish to Test PyPI"
	@echo ""
	@echo "$(YELLOW)Maintenance:$(NC)"
	@echo "  clean         - Remove build artifacts and cache"
	@echo "  clean-all     - Deep clean including virtual environment"
	@echo "  security      - Audit dependencies and run static analysis"
	@echo "  update        - Update dependencies"

# Setup targets
.PHONY: install
install:
	$(call log,Installing dependencies with uv...)
	uv sync

.PHONY: install-dev
install-dev:
	$(call log,Installing development dependencies...)
	uv sync --extra dev

.PHONY: setup
setup: install-dev
	$(call log,Project setup complete!)

# Code quality targets
.PHONY: format
format:
	$(call log,Formatting code with ruff...)
	uv run ruff format src tests

.PHONY: lint
lint:
	$(call log,Linting code with ruff...)
	uv run ruff check src tests

.PHONY: lint-fix
lint-fix:
	$(call log,Fixing linting issues with ruff...)
	uv run ruff check --fix src tests

.PHONY: type-check
type-check:
	$(call log,Running type checks with mypy...)
	uv run mypy src

.PHONY: check
check: format lint type-check
	$(call log,All checks completed!)

# Testing targets
.PHONY: test
test:
	$(call log,Running tests...)
	uv run pytest

.PHONY: test-cov
test-cov:
	$(call log,Running tests with coverage...)
	uv run pytest --cov=nvisy --cov-report=term-missing --cov-report=html

.PHONY: test-verbose
test-verbose:
	$(call log,Running tests in verbose mode...)
	uv run pytest -v

# OpenAPI targets
#
# The datatypes module is generated from the API's OpenAPI specification; the
# service classes wrapping it are hand-written, because the spec declares no
# operationIds to derive method names from.
.PHONY: check-remote
check-remote:
	$(call log,Checking connection to production API...)
	@curl -sf -o /dev/null $(OPENAPI_ENDPOINT) || \
		(echo "$(RED)Error: Cannot connect to $(OPENAPI_ENDPOINT)$(NC)" && exit 1)
	$(call log,Connection successful)

.PHONY: check-local
check-local:
	$(call log,Checking connection to local API server...)
	@curl -sf -o /dev/null $(OPENAPI_ENDPOINT_LOCAL) || \
		(echo "$(RED)Error: Cannot connect to $(OPENAPI_ENDPOINT_LOCAL)$(NC)" && exit 1)
	$(call log,Connection successful)

.PHONY: download-spec
download-spec:
	$(call log,Downloading OpenAPI specification from $(OPENAPI_ENDPOINT)...)
	@mkdir -p $(OPENAPI_OUTPUT_DIR)
	@curl -f -o $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME) $(OPENAPI_ENDPOINT) || \
		(echo "$(RED)Failed to download OpenAPI specification$(NC)" && exit 1)
	$(call log,Specification saved to $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME))

.PHONY: download-spec-local
download-spec-local:
	$(call log,Downloading OpenAPI specification from $(OPENAPI_ENDPOINT_LOCAL)...)
	@mkdir -p $(OPENAPI_OUTPUT_DIR)
	@curl -f -o $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME) $(OPENAPI_ENDPOINT_LOCAL) || \
		(echo "$(RED)Failed to download OpenAPI specification$(NC)" && exit 1)
	$(call log,Specification saved to $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME))

.PHONY: generate-models
generate-models:
	$(call log,Generating datatypes from OpenAPI specification...)
	@uv run datamodel-codegen \
		--input $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME) \
		--input-file-type openapi \
		--output $(GENERATED_MODELS) \
		--output-model-type pydantic_v2.BaseModel \
		--target-python-version $(PYTHON_VERSION) \
		--use-standard-collections \
		--use-union-operator \
		--snake-case-field \
		--use-field-description \
		--formatters ruff-format \
		--disable-timestamp
	$(call log,Datatypes generated in $(GENERATED_MODELS))

.PHONY: generate
generate: check-remote download-spec generate-models
	$(call log,Type generation complete)

.PHONY: generate-local
generate-local: check-local download-spec-local generate-models
	$(call log,Type generation complete)

# Build and publish targets
.PHONY: build
build:
	$(call log,Building package...)
	uv build

.PHONY: publish-test
publish-test: build
	$(call log,Publishing to Test PyPI...)
	uv run twine upload --repository testpypi dist/*

.PHONY: publish
publish: build
	$(call log,Publishing to PyPI...)
	uv run twine upload dist/*

# Maintenance targets
.PHONY: clean
clean:
	$(call log,Cleaning build artifacts...)
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf $(OPENAPI_OUTPUT_DIR)/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	$(call log,Clean completed!)

.PHONY: clean-all
clean-all: clean
	$(call log,Deep cleaning including virtual environment...)
	@rm -rf .venv/
	@rm -rf .uv/
	$(call log,Deep clean completed!)

.PHONY: update
update:
	$(call log,Updating dependencies...)
	uv lock --upgrade
	uv sync

# Security checks
.PHONY: security
security:
	$(call log,Auditing runtime dependencies...)
	@uv export --frozen --no-dev --no-emit-project --format requirements-txt >requirements.txt
	@uv tool run pip-audit --requirement requirements.txt --no-deps --disable-pip --strict
	@rm -f requirements.txt
	$(call log,Running bandit...)
	@uv run bandit -c pyproject.toml -r src --severity-level medium
	$(call log,Security checks complete)

# Quick development cycle
.PHONY: dev
dev: format lint test
	$(call log,Development cycle completed!)
