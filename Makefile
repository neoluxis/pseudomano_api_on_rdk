VENV=./.venv
PY=$(VENV)/bin/python

.PHONY: venv install run test

venv:
	python3 -m venv $(VENV)

install: venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) run.py

test:
	$(PY) -m pytest -q

dummy_infer:
	make -C cpp
