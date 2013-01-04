# Makefile for project June
.PHONY: clean-pyc clean-build docs

all: install
	@cp scripts/githooks/* .git/hooks/
	@chmod -R +x .git/hooks/

# Development
install:
	@pip install -r dev-reqs.txt

server:
	@python manager.py runserver


database:
	@python manager.py createdb

# translate
babel-extract:
	@pybabel extract -F babel.cfg -o messages.pot .

babel-init:
	@pybabel init -i messages.pot -d june/translations -l zh

babel-compile:
	@pybabel compile -d june/translations

babel-update: babel-extract
	@pybabel update -i messages.pot -d june/translations

# Common Task
clean: clean-build clean-pyc

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info


clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

files := $(shell find . -name '*.py' ! -path "*__init__.py*" ! -path "*docs/*")
lint:
	@flake8 ${files}

# Sphinx Documentation
docs:
	@$(MAKE) -C docs html


# Deployment

# Git
github:
	@git push origin flask

testing:
	@nosetests -v
