# Makefile for project June
.PHONY: clean-pyc clean-build docs

server:
	@python manager.py runserver

database:
	@alembic upgrade head

staticdir = public/static

static-js:
	@cat ${staticdir}/js/bootstrap.js > ${staticdir}/app.min.js
	@cat ${staticdir}/js/site.js >> ${staticdir}/app.min.js

static-css:
	@cat ${staticdir}/css/bootstrap.css > ${staticdir}/app.min.css
	@cat ${staticdir}/css/bootstrap-responsive.css >> ${staticdir}/app.min.css
	@cat ${staticdir}/css/pygments.css >> ${staticdir}/app.min.css
	@cat ${staticdir}/css/site.css >> ${staticdir}/app.min.css

static-compile:
	@uglifyjs ${staticdir}/app.min.js -m -o ${staticdir}/app.min.js

static: static-js static-css static-compile

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
