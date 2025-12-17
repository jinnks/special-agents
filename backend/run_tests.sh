#!/bin/bash
# Test runner script for Special Agents
# Run this to execute all tests with coverage

set -e

echo "🧪 Special Agents Test Suite"
echo "============================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies if needed
echo "📦 Checking dependencies..."
pip install -q pytest pytest-cov pytest-mock pytest-flask coverage faker 2>/dev/null || true

echo ""
echo "🔍 Running tests..."
echo ""

# Run tests with coverage
pytest tests/ \
    --verbose \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=80 \
    --tb=short \
    -ra

EXIT_CODE=$?

echo ""
echo "============================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report saved to: htmlcov/index.html"
    echo "   Open it with: open htmlcov/index.html"
else
    echo "❌ Some tests failed!"
    echo ""
    echo "Run specific test:"
    echo "  pytest tests/test_security.py::TestInputValidator::test_validate_username_valid -v"
    echo ""
    echo "Run with more details:"
    echo "  pytest tests/ -vv --tb=long"
fi

exit $EXIT_CODE
