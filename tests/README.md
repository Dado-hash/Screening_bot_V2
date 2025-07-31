# Tests directory

This directory contains test files for the Screening Bot V2 project.

## Running tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run tests with coverage
pytest --cov=.
```

## Test structure

- `test_update_historical_datas.py` - Tests for data update functionality
- `test_calculate_performance.py` - Tests for performance calculations
- `test_database.py` - Tests for database operations
