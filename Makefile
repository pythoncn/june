# Makefile for project June
.PHONY: clean-pyc clean-build docs

server:
	@python manager.py runserver

upgrade:
	@alembic upgrade head

staticdir = june/public/static
assets:
	@$(MAKE) -C assets build

static:
	@$(MAKE) -C assets compile
	@uglifyjs ${staticdir}/app.js -m -o ${staticdir}/app.js

# translate
babel-extract:
	@python setup.py extract_messages -o messages.pot

language = zh
i18n = june/translations
babel-init:
	@python setup.py init_catalog -i messages.pot -d ${i18n} -l ${language}

babel-compile:
	@python setup.py compile_catalog -d ${i18n}

babel-update: babel-extract
	@python setup.py update_catalog -i messages.pot -d ${i18n}

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


lint:
	@flake8 june
	@flake8 tests

test:
	@nosetests -s

coverage:
	@rm -f .coverage
	@nosetests --with-coverage --cover-package=june --cover-html

# Sphinx Documentation
docs:
	@$(MAKE) -C docs html
