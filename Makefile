.PHONY: clean-build clean-pyc clean

VERSION := $(shell python setup.py --version)

all:
	@echo

version:
	@echo "fsm_admim.__version__ == $(VERSION)"

help:
	@echo " Make targets"
	@echo
	@echo " * clean       - runs clean-build & clean-pyc"
	@echo " * clean-build - remove build artifacts"
	@echo " * clean-pyc   - remove Python file artifacts"
	@echo " * dist        - package"
	@echo " * help        - print this targets list"
	@echo " * release     - package and upload a release"
	@echo " * version     - print the current value of fsm_admin.__version__"
	@echo

clean: clean-build clean-pyc

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

dist: clean
	@python setup.py -q sdist
	@twine check dist/django-fsm-admin-${VERSION}.tar.gz

release: clean
	@python setup.py -q sdist
	@twine check dist/django-fsm-admin-${VERSION}.tar.gz
	@twine upload dist/django-fsm-admin-$(VERSION).tar.gz
