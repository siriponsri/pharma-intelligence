.PHONY: help setup install install-dev install-all test lint format clean \
        download-orange-book build-index query \
        generate-mock sarimax-baseline sarimax-exog

help:
	@echo "Setup:"
	@echo "  make setup              - Create venv, install deps, copy .env.example"
	@echo "  make install-dev        - pip install -e '.[dev]' (no Jupyter)"
	@echo "  make install-notebook   - pip install -e '.[dev,notebook]' (with Jupyter)"
	@echo "  make install-all        - pip install -e '.[dev,notebook,forecasting]' (everything)"
	@echo ""
	@echo "Code quality:"
	@echo "  make test               - Run pytest"
	@echo "  make lint               - Run ruff + mypy"
	@echo "  make format             - Run black + ruff --fix"
	@echo "  make clean              - Remove caches"
	@echo ""
	@echo "IS2 — Intelligence (RAG):"
	@echo "  make download-orange-book  - Fetch FDA Orange Book ZIP"
	@echo "  make build-index           - Embed + index cardiometabolic drugs"
	@echo "  make query Q='question'    - Ask the RAG system"
	@echo ""
	@echo "IS1 — Forecasting:"
	@echo "  make generate-mock         - Generate mock demand panel"
	@echo "  make sarimax-baseline      - Fit SARIMAX baseline (no exog)"
	@echo "  make sarimax-exog          - Fit SARIMAX with exogenous features"

setup:
	python3.12 -m venv .venv || python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev,forecasting]"
	[ -f .env ] || cp .env.example .env
	@echo ""
	@echo "✅ Setup complete (without Jupyter). Edit .env to add THAILLM_API_KEY"
	@echo "   If you want Jupyter: run 'make install-notebook' after"
	@echo "   Then: source .venv/bin/activate"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-notebook:
	pip install -e ".[dev,notebook]"

install-all:
	pip install -e ".[dev,notebook,forecasting]"

test:
	pytest -v

lint:
	ruff check src tests scripts
	mypy src

format:
	black src tests scripts
	ruff check --fix src tests scripts

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true

# IS2 — Intelligence (RAG)
download-orange-book:
	python scripts/download_orange_book.py

build-index:
	python scripts/build_index.py

query:
	python scripts/query_rag.py "$(Q)"

# IS1 — Forecasting
generate-mock:
	python scripts/generate_mock_demand.py

sarimax-baseline:
	python scripts/run_sarimax_baseline.py --output data/processed/sarimax_baseline_results.json

sarimax-exog:
	python scripts/run_sarimax_baseline.py --with-exog --output data/processed/sarimax_exog_results.json
