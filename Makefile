# Makefile for project June

.PHONY: clean-pyc clean-build docs

# Variables for June


# Development
server:
	python manage.py runserver


database:
	python manage.py syncdb


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

# Git
github:
	git push origin django
