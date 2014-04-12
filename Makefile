# Makefile for project June

.PHONY: server
server:
	@python manager.py runserver

.PHONY: upgrade
upgrade:
	@alembic upgrade head

.PHONY: assets
staticdir = june/public/static
assets:
	@$(MAKE) -C assets build

.PHONY: static
static:
	@$(MAKE) -C assets compile
	@uglifyjs ${staticdir}/app.js -m -o ${staticdir}/app.js

# translate
.PHONY: babel-extract
babel-extract:
	@python setup.py extract_messages -o messages.pot

language = zh
i18n = june/translations
.PHONY: babel-init
babel-init:
	@python setup.py init_catalog -i messages.pot -d ${i18n} -l ${language}

.PHONY: babel-compile
babel-compile:
	@python setup.py compile_catalog -d ${i18n}

.PHONY: babel-update
babel-update: babel-extract
	@python setup.py update_catalog -i messages.pot -d ${i18n}

# Common Task
.PHONY: clean
clean: clean-build clean-pyc
	@rm -fr cover/

.PHONY: clean-build
clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

.PHONY: clean-pyc
clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

.PHONY: lint
lint:
	@flake8 june
	@flake8 tests

.PHONY: test
test:
	@nosetests -s

.PHONY: coverage
coverage:
	@rm -f .coverage
	@nosetests --with-coverage --cover-package=june --cover-html

# Sphinx Documentation
.PHONY: docs
docs:
	@$(MAKE) -C docs html
