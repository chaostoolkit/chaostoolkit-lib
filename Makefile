.PHONY: install
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

.PHONY: install-dev
install-dev: install
	pip install -r requirements-dev.txt
	python3 setup.py develop

.PHONY: build
build:
	python3 setup.py build

.PHONY: lint
lint:
	flake8 chaoslib/ tests/
	isort --check-only --profile black chaoslib/ tests/
	black --check --diff chaoslib/ tests/

.PHONY: format
format:
	isort --profile black chaoslib/ tests/
	black chaoslib/ tests/

.PHONY: tests
tests:
	pytest
