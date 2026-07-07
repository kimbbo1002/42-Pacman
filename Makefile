PYTHON = python3
MAIN = pac-man.py
CONFIG = config.json

install:
	uv sync

run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	uv run flake8 . --exclude .venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf uv.lock
	rm -rf .venv

.PHONY: install run debug lint lint-strict clean fclean