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


coverage:
	coverage run --source='.' manage.py test tests/

#
#   Code Checks
#
.PHONY: pre-commit check semgrep

pre-commit:
	pre-commit run -a

check: pre-commit coverage

#
#   Extended Reports
#
.PHONY: smells security complexity check-advanced check-extended

smells:
	semgrep --config=p/r2c-ci --config=p/python

security:
	bandit -r apps pxapi

complexity:
	wily build apps pxapi
	wily report apps
	wily report pxapi

doc-style:
	pydocstyle --match-dir="[^(\.|migrations)].*" apps pxapi

check-advanced: smells security
check-picky: complexity doc-style
check-extended: check check-advanced check-picky

#
#   Code Checks auto-fix
#
.PHONY: black

black:
	python -m black -tpy38 apps pxapi tests *.py
