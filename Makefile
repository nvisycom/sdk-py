# Makefile for Nvisy Python SDK

ifneq (,$(wildcard ./.env))
	include .env
	export
endif

# Environment variables with defaults
OPENAPI_ENDPOINT ?= https://api.nvisy.com/openapi.yaml
OPENAPI_OUTPUT_DIR ?= openapi
OPENAPI_FILENAME ?= nvisy-api.yaml
GENERATED_CODE_DIR ?= src/nvisy/generated
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
	@echo "  setup         - Complete project setup (install + pre-commit)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  format        - Format code with ruff"
	@echo "  lint          - Lint code with ruff"
	@echo "  type-check    - Run mypy type checking"
	@echo "  check         - Run all checks (format, lint, type-check)"
	@echo "  test          - Run tests with pytest"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  test-watch    - Run tests in watch mode"
	@echo ""
	@echo "$(YELLOW)OpenAPI:$(NC)"
	@echo "  openapi       - Download OpenAPI spec and generate client code"
	@echo "  download-spec - Download OpenAPI specification only"
	@echo ""
	@echo "$(YELLOW)Build & Deploy:$(NC)"
	@echo "  build         - Build package"
	@echo "  publish       - Publish to PyPI"
	@echo "  publish-test  - Publish to Test PyPI"
	@echo ""
	@echo "$(YELLOW)Maintenance:$(NC)"
	@echo "  clean         - Remove build artifacts and cache"
	@echo "  clean-all     - Deep clean including virtual environment"
	@echo "  update        - Update dependencies"

# Setup targets
.PHONY: install
install:
	$(call log,Installing dependencies with uv...)
	uv sync

.PHONY: install-dev
install-dev:
	$(call log,Installing development dependencies...)
	uv sync --dev

.PHONY: setup
setup: install-dev
	$(call log,Setting up pre-commit hooks...)
	uv run pre-commit install
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

.PHONY: test-watch
test-watch:
	$(call log,Running tests in watch mode...)
	uv run pytest --looponfail

.PHONY: test-verbose
test-verbose:
	$(call log,Running tests in verbose mode...)
	uv run pytest -v

# OpenAPI targets
.PHONY: download-spec
download-spec:
	$(call log,Creating output directory...)
	@mkdir -p $(OPENAPI_OUTPUT_DIR)
	$(call log,Downloading OpenAPI specification from $(OPENAPI_ENDPOINT)...)
	@curl -f -o $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME) $(OPENAPI_ENDPOINT) || \
		(echo "$(RED)Failed to download OpenAPI specification$(NC)" && exit 1)
	$(call log,OpenAPI specification downloaded to $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME))

.PHONY: generate-client
generate-client:
	$(call log,Generating Python client code from OpenAPI spec...)
	@mkdir -p $(GENERATED_CODE_DIR)
	# Use openapi-generator-cli or datamodel-code-generator
	uv run datamodel-codegen \
		--input $(OPENAPI_OUTPUT_DIR)/$(OPENAPI_FILENAME) \
		--output $(GENERATED_CODE_DIR)/models.py \
		--input-file-type openapi \
		--use-generic-container-types \
		--use-union-operator || \
		(echo "$(YELLOW)Code generation failed, please install datamodel-code-generator$(NC)" && true)
	$(call log,Client code generated in $(GENERATED_CODE_DIR))

.PHONY: openapi
openapi: download-spec generate-client
	$(call log,OpenAPI workflow completed!)

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
	$(call log,Running security checks...)
	uv run bandit -r src/ -f json -o bandit-report.json || true
	uv run safety check --json --output safety-report.json || true

# Documentation
.PHONY: docs
docs:
	$(call log,Building documentation...)
	uv run mkdocs build

.PHONY: docs-serve
docs-serve:
	$(call log,Serving documentation...)
	uv run mkdocs serve

# Pre-commit
.PHONY: pre-commit
pre-commit:
	$(call log,Running pre-commit hooks...)
	uv run pre-commit run --all-files

# Quick development cycle
.PHONY: dev
dev: format lint test
	$(call log,Development cycle completed!)
