# Makefile for project June

.PHONY: clean-pyc clean-build docs

# Development
install:
	pip install -r dev-requirements.txt

server:
	python june/app.py


database:
	python syncdb.py


# Common Task
clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

# Sphinx Documentation
docs:
	$(MAKE) -C docs html


# Deployment

# Git
github:
	git push origin flask

testing:
	nosetests -v
