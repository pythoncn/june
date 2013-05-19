# Makefile for project June
.PHONY: clean-pyc clean-build docs

# Development
all:
	@pip install -r etc/reqs-dev.txt
	@cp etc/githooks/* .git/hooks/
	@chmod -R +x .git/hooks/


server:
	@python manager.py runserver


database:
	@python manager.py createdb


# translate
babel-extract:
	@pybabel extract -F etc/babel.cfg -o data/messages.pot .

language = zh
babel-init:
	@pybabel init -i data/messages.pot -d i18n -l ${language}

babel-compile:
	@pybabel compile -d i18n

babel-update: babel-extract
	@pybabel update -i data/messages.pot -d i18n

# Common Task
clean: clean-build clean-pyc
	@rm -fr cover/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info


clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +


june_files := $(shell find june -name '*.py' ! -path "*__init__.py")
test_files := $(shell find tests -name '*.py' ! -path "*__init__.py")
lint:
	@flake8 ${june_files}
	@flake8 ${test_files}

test:
	@nosetests -s

coverage:
	@rm -f .coverage
	@nosetests --with-coverage --cover-package=june --cover-html

# Sphinx Documentation
docs:
	@$(MAKE) -C docs html
