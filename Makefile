.PHONY: help venv install build test run clean

PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
APP := $(VENV)/bin/backuper
LOCAL_BIN := $(HOME)/.local/bin
SHIM := $(LOCAL_BIN)/backuper

help:
	@echo "Usage: make [venv|install|build|test|run|clean]"
	@echo "  venv    Create the project virtual environment with dependencies"
	@echo "  install Create a user-local shim so backuper is available without activating venv"
	@echo "  build   Build the distributable package using the venv"
	@echo "  test    Run the test suite inside the venv"
	@echo "  run     Run the backuper CLI from the venv"
	@echo "  clean   Remove build artifacts and the virtual environment"

venv:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

install: venv
	@mkdir -p "$(LOCAL_BIN)"
	@printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' 'exec "$(CURDIR)/.venv/bin/python" -m backuper "$$@"' > "$(SHIM)"
	@chmod +x "$(SHIM)"

build: venv
	$(PY) -m build

test: venv
	$(PYTEST) -q

run: venv
	$(APP) --help

clean:
	rm -rf $(VENV) build dist *.egg-info .pytest_cache __pycache__ backuper/__pycache__ tests/__pycache__
	@rm -f "$(SHIM)"
