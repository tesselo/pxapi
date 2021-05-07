.PHONY: install dev_install upgrade_dependencies

install:
	pip install -r requirements.txt
	pip install -U git+ssh://git@github.com/tesselo/pixels.git --force-reinstall --no-deps

dev_install: install
	pip install -r dev_requirements.txt

upgrade_dependencies: dev_install
	pip install pip-tools
	pip-compile --upgrade --output-file ./requirements.txt requirements.in
	pip-compile --upgrade --output-file ./dev_requirements.txt dev_requirements.in
