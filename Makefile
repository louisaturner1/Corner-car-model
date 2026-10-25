.PHONY. all install test run clean # Define the default action when 'make' is typed alone
all: install test run

install:
  python -m pip install --upgrade pip
  pip install -r requirements.txt

test:
  pytest tests/ -v

run: # Execute the main vehicle suspension simulation pipeline
  python src/dynamic.py

clean: # Clean any generated artifacts, logs, and python cache files
  rm -rf data/processed/*.csv # rm is remove, -r is recursively go into directories, -f is force deletion
  rm -rf __pycache__
  rm -rf .pytest_cache
  find . -type d -name "__pycache__" -exec rm - rf {} +
