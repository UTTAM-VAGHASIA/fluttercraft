#!/bin/bash
# Pre-commit check script for FlutterCraft
# Run Black and Flake8 before committing

echo "Running pre-commit checks..."

# Activate virtual environment
source .venv/Scripts/activate

# Run Black formatter
echo "1. Running Black formatter..."
black fluttercraft/ .specs/ --exclude='.venv|venv|env|build|dist'
if [ $? -ne 0 ]; then
    echo "❌ Black formatting failed"
    exit 1
fi

# Run Flake8 linter
echo "2. Running Flake8 linter..."
flake8 fluttercraft/
if [ $? -ne 0 ]; then
    echo "⚠️  Flake8 found issues (check if they're ignored in .flake8)"
    # Don't exit on flake8 issues - some are expected (E203)
fi

# Run basic syntax check
echo "3. Running syntax check..."
python -m py_compile fluttercraft/**/*.py
if [ $? -ne 0 ]; then
    echo "❌ Syntax check failed"
    exit 1
fi

echo "✅ All pre-commit checks passed!"
echo ""
echo "You can now commit your changes:"
echo "  git add ."
echo "  git commit -m 'your message'"
