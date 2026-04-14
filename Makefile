NAME = fly-in
PYTHON = python3
DEFAULT_MAP = default.txt
VENV_DIR = .venv

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run run-ui debug clean lint lint-strict gitignore venv

install:
	@echo "No external dependencies required."

run:
	$(PYTHON) main.py $(DEFAULT_MAP)

run-ui:
	$(PYTHON) main.py $(DEFAULT_MAP) --ui

debug:
	$(PYTHON) -m pdb main.py $(DEFAULT_MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 . --exclude=.venv,__pycache__,.mypy_cache,.pytest_cache
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 . --exclude=.venv,__pycache__,.mypy_cache,.pytest_cache
	mypy . --strict

gitignore:
	printf "%s\n" \
	"__pycache__/" \
	"*.pyc" \
	".mypy_cache/" \
	".pytest_cache/" \
	".venv/" > .gitignore
	@echo ".gitignore created."

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"