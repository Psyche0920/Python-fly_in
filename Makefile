NAME = fly-in
PYTHON = python3
DEFAULT_MAP = default.txt

MY_FLAGS = --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run run-ui debug clean lint lint-strict

install:
    @echo "No external dependencies required."

run:
    $(PYTHON) main.py $(DEFAULT_MAP)

run-ui:
    $(PYTHON) main.py $(DEFAULT_MAP) --ui

debug:
    $(PYTHON) -m pdb main.py $(DEFAULT_MAP)

lint:
    flake8 .
    mypy . $(MYPY_FLAGS)

lint-strict:
    flake8 .
    mypy . --strict