.PHONY: install dev_install upgrade_dependencies

install:
	pip install -r requirements.txt

dev_install: install
	pip install -r dev_requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

upgrade_dependencies: dev_install
	pip install pip-tools
	pip-compile --upgrade --output-file ./requirements.txt requirements.in
	pip-compile --upgrade --output-file ./dev_requirements.txt dev_requirements.in

#
#   Extended Reports
#
.PHONY: coverage

coverage:
	coverage run --source='.' manage.py test tests/

#
#   Code Checks
#
.PHONY: pre-commit check semgrep

pre-commit:
	pre-commit run -a

check: pre-commit coverage

semgrep:
	semgrep --config=p/r2c-ci --config=p/django

check-extended: check semgrep

#
#   Code Checks auto-fix
#
.PHONY: black

black:
	python -m black -l79 -tpy38 apps pxapi tests *.py
