DEFAULT_GOAL := help

PYTHON := python3
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
DEPS_STAMP := $(VENV_DIR)/.deps.stamp
REQ_FILES := requirements.txt requirements-dev.txt
REQ_PACKAGES := \
	behave \
	httpx \
	py-trello \
	pydantic \
	pytest \
	pytest-asyncio \
	python-dotenv

.PHONY: help venv deps test test-pytest test-behave clean-venv

help:
	@printf '%s\n' 'Available targets:'
	@printf '  %-14s %s\n' 'make venv' 'Create .venv if it does not exist'
	@printf '  %-14s %s\n' 'make deps' 'Ensure .venv exists and dependencies are installed'
	@printf '  %-14s %s\n' 'make test' 'Run pytest validation tests and the behave suite'
	@printf '  %-14s %s\n' 'make test-pytest' 'Run pytest validation tests only'
	@printf '  %-14s %s\n' 'make test-behave' 'Run behave suite only'
	@printf '  %-14s %s\n' 'make clean-venv' 'Remove the local virtual environment'

venv: $(VENV_PYTHON)

deps: $(DEPS_STAMP)

test: test-pytest test-behave

test-pytest: $(DEPS_STAMP)
	PYTHONPATH=src $(VENV_PYTHON) -m pytest -q tests/validation/

test-behave: $(DEPS_STAMP)
	PYTHONPATH=src $(VENV_PYTHON) -m behave -q

clean-venv:
	rm -rf $(VENV_DIR)

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV_DIR)

$(DEPS_STAMP): $(VENV_PYTHON) $(REQ_FILES)
	@if ! $(VENV_PYTHON) -m pip show $(REQ_PACKAGES) >/dev/null 2>&1; then \
		$(VENV_PIP) install -r requirements.txt -r requirements-dev.txt; \
	fi
	@touch $(DEPS_STAMP)
