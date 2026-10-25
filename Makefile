.PHONY. all install test run clean # Define the default action when 'make' is typed alone
all: install test run

install:
  python -m pip install --upgrade pip
  pip install -r requirements.txt

run: # Execute the main vehicle suspension simulation pipeline
  python src/dynamic.py
  python src/filter.py
  python src/evaluate.py

test:
  pytest tests/ -v

clean: # Clean any generated artifacts, logs, and python cache files
	rm -rf __pycache__ .pytest_cache src/__pycache__ tests/__pycache__
	rm -f data/processed/*.csv data/processed/*.png
