.PHONY: help install test lint format clean run-update run-performance clean-db

help:
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  format        - Format code with black"
	@echo "  clean         - Clean cache and temp files"
	@echo "  run-update    - Run historical data update"
	@echo "  run-performance - Run performance calculation"
	@echo "  clean-db      - Clean database tables"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=.

lint:
	flake8 *.py --max-line-length=88 --extend-ignore=E203,W503

format:
	black *.py --line-length=88

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run-update:
	python update_historical_datas.py

run-performance:
	python calculate_performance.py

clean-db:
	python drop_tables.py
