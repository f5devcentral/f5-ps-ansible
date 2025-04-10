.PHONY: clean clean-test clean-pyc clean-build docs help

BASE_DIR := $(shell pwd)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.ruff_cache' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -f coverage.xml
	rm -f coverage.lcov
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .ruff_cache
	find . -name '.mypy_cache' -exec rm -fr {} +
	rm -rf ansible_collections/f5_ps_ansible/f5os/tests/output

code-format:
	ruff check --select I --fix --exclude .venv
	ruff format --exclude .venv

doc: docs ## alias for docs

docs:
	python3 docs/f5os/ansible_module_autodoc.py

pytests:
	cd ansible_collections/f5_ps_ansible/f5os && PYTHONPATH=$(BASE_DIR) pytest tests/unit/plugins/module_utils/test_utils.py

tests: test

ansible:
	cp -f COPYING ansible_collections/f5_ps_ansible/f5os/COPYING
	cp -f SUPPORT.md ansible_collections/f5_ps_ansible/f5os/SUPPORT.md
	mkdir -p ./build
	ansible-galaxy collection build ansible_collections/f5_ps_ansible/f5os --output-path build/
