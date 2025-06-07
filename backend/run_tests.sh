#!/bin/bash

# Install the package in development mode
pip install -e .

# Install test dependencies
pip install -r requirements-test.txt

# Run the tests with coverage
pytest --cov=app --cov-report=term-missing 