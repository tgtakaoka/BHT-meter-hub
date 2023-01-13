PYTHON = python3
VENV ?= $(if $(VIRTUAL_ENV),$(notdir $(VIRTUAL_ENV)),.venv)

help:
	@echo "---- for developers"
	@test -z "$(VIRTUAL_ENV)" || return 0 && \
	 echo "make create_venv      create python virtual environment VENV (default $(VENV))"
	@test -n "$(VIRTUAL_ENV)" || return 0 && \
	 echo "make delete_venv      delete python virtual environment $(VENV)"
	@echo "make development      install this package to $(VENV) for development"
	@echo "make test             run unit test"
	@echo "---- for maintainers"
	@echo "make clean            clean backaups and caches"
	@echo "make dist             create distribution"
	@echo "make distclean        clean distribution artifacts"

in_venv:
	@test -n "$(VIRTUAL_ENV)" || \
	    { echo "Not in virtual environment, do 'source $(VENV)/bin/activate'"; return 1; }
not_in_venv:
	@test -z "$(VIRTUAL_ENV)" || \
	    { echo "In virtual environment, do 'deactivate'"; return 1; }

create_venv: not_in_venv
	$(PYTHON) -m venv $(VENV)

delete_venv: not_in_venv
	-rm -rf $(VENV)

development: in_venv
	$(PYTHON) -m pip install -e .[dev]

test: in_venv
	$(PYTHON) -m pytest

formatting:
	$(PYTHON) -m black src/bhtmeter tests
	$(PYTHON) -m isort src/bhtmeter tests
	$(PYTHON) -m pflake8 --color never src/bhtmeter tests

requirements.txt: pyproject.toml
	pip-compile pyproject.toml

dist: in_venv formatting requirements.txt
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

test-publish:
	$(PYTHON) -m twine upload -r testpypi dist/*
publish: dist
	$(PYTHON) -m twine upload dist/*

clean:
	find . -name '__pycache__' -o -name '.pytest_cache' -o -name '*~' | xargs rm -rf

distclean: in_venv clean
	find . -name '*.egg-info' | xargs rm -rf
	-rm -rf dist build $(VENV)

.PHONY: help in_venv not_in_env create_venv delete_venv
.PHONY: development test formatting test-publish publish clean distclean

# Local Variables:
# mode: makefile-gmake
# End:
# vim: set ft=make:
