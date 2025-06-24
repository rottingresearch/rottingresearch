#!/bin/bash

# Rotting Research Test Runner
# This script runs the complete test suite for the Rotting Research application

set -e

echo "🧪 Starting Rotting Research Test Suite"
echo "========================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected. Consider activating one."
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r tests/test-requirements.txt

# Set environment variables for testing
export FLASK_ENV=testing
export ENV=TEST
export REDIS_URL=redis://localhost:6379/0
export APP_SECRET_KEY=test-secret-key
export CAPTCHA_KEY_ID=test-key
export CAPTCHA_SECRET_KEY=test-secret

echo "🏃‍♂️ Running tests..."

# Run the full test suite
pytest tests/ \
    --verbose \
    --tb=short \
    --cov=app \
    --cov=tasks \
    --cov=utilites \
    --cov=celery_init \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-fail-under=70

echo ""
echo "✅ Test suite completed!"
echo "📊 Coverage report generated in htmlcov/ directory"
echo "🌐 Open htmlcov/index.html in a browser to view detailed coverage"
