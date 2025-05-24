.PHONY: help install-dev setup-db run-sample test coverage lint clean

UV = uv
PYTHON = python3
PRECOMMIT = pre-commit

help:
	@echo "Available commands:"
	@echo "  sync-deps       - Install/sync dependencies using uv (from pyproject.toml)"
	@echo "  setup-db        - (Re)Initializes the database schema"
	@echo "  create-product  - Example: make create-product name=\"Awesome Gadget\" qty=10 price=99.99"
	@echo "  create-order    - Example: make create-order items=\"1,2;3,1\""
	@echo "  list-products   - List all products"
	@echo "  test            - Run tests using uv (pytest)"
	@echo "  coverage        - Run tests with coverage report using uv (pytest-cov)"
	@echo "  lint            - Run linters using uv (ruff)"
	@echo "  format          - Run formatter using uv (ruff format)"
	@echo "  clean           - Clean up cache files and .coverage"

sync-deps:
	$(UV) sync --all-groups # Устанавливаем основные + dev зависимости
	@echo "Dependencies (including dev) installed/updated."
	@echo "If you use pre-commit, ensure hooks are installed: pre-commit install"


create-product:
	@# Example: make create-product name="Awesome Gadget" qty=10 price=99.99
	$(PYTHON) main.py create-product --name="$(name)" --quantity=$(qty) --price=$(price)

create-order:
	@# Example: make create-order items="1,2;3,1" (product_id,quantity;...)
	$(PYTHON) main.py create-order --items="$(items)"

list-products:
	$(PYTHON) main.py list-products

test:
	$(PYTEST)

coverage:
	$(PYTEST) --cov=. --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	$(RUFF) check --fix .

format:
	$(RUFF) format .

clean:
	@rm -rf .pytest_cache
	@rm -f .coverage
	@rm -rf htmlcov
	@find . -name '__pycache__' -type d -exec rm -r {} +
	@find . -name '*.pyc' -delete
	@echo "Cleaned up cache and coverage files."
