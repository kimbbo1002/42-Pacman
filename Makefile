PYTHON = python3
MAIN = pac-man.py
CONFIG = config.json
DIST = dist/$(NAME)
NAME = pacman

install:
	uv sync

run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	uv run flake8 . --exclude .venv,build,dist
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

package:
	uv run pyinstaller --noconfirm --clean $(NAME).spec
	cp $(CONFIG) INSTRUCTIONS.txt $(DIST)/
	cd dist && zip -qr $(NAME)-linux.zip $(NAME)
	@echo "built $(DIST)/ and dist/$(NAME)-linux.zip"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf uv.lock
	rm -rf .venv
	rm -rf build dist

.PHONY: install run debug lint package clean fclean