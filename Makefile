# Makefile for project June

.PHONY: clean-pyc clean-build docs

# Variables for June
CONFIG = tmp.config
PROJSERVER = linode.lepture.com:/home/lepture/project/june
STATIC = june/_static


# Development
server:
	june/app.py --settings=$(CONFIG)


database:
	june/tools.py --settings=$(CONFIG) createdb


admin:
	june/tools.py --settings=$(CONFIG) createuser

# Common Task
clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {rm} +
	find . -name '*~' -exec rm -f {} +

# Sphinx Documentation
docs:
	$(MAKE) -C docs html


# Deployment
upload:
	rsync -av --del --exclude=*.pyc june/* $(PROJSERVER)


# static, required livereload
install_static: install_image install_js install_css

install_js:
	livereload lib_js
	livereload site_js

install_css:
	livereload site_css

install_image:
	if [ ! -d $(STATIC)/img ]; then mkdir $(STATIC)/img; fi
	cp -r assets/img/* $(STATIC)/img/
