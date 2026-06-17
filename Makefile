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
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf 'find . -type d -name "__pycache__"'
	rm -rf .mypy_cache

fclean: clean
	rm -rf uv.lock
	rm -rf .venv

.PHONY: install run debug lint lint-strict clean fclean