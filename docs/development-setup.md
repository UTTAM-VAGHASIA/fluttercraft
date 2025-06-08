# FlutterCraft — Development Setup Guide

---

## 🚀 Quick Start for Contributors

This guide will help you set up a local development environment for FlutterCraft.

---

## 📋 Prerequisites

### Required Software
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Flutter SDK** - [Install Guide](https://docs.flutter.dev/get-started/install)
- **Code Editor** - VS Code, PyCharm, or your preferred editor

### Optional but Recommended
- **GitHub CLI** - [Install](https://cli.github.com/) (for testing GitHub integration)
- **FVM** - [Install](https://fvm.app/) (for testing Flutter version management)
- **Docker** - [Install](https://www.docker.com/) (for containerized testing)

---

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft.git
cd fluttercraft
```

### 2. Set Up Python Environment

#### Using venv (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### Using conda (Alternative)
```bash
conda create -n fluttercraft python=3.10
conda activate fluttercraft
```

### 3. Install Dependencies

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 4. Verify Installation

```bash
# Test CLI installation
python -m fluttercraft --help

# Run basic tests
pytest tests/unit/ -v
```

---

## 🧪 Testing Procedures

### Running Tests

#### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_validation.py -v

# Run with coverage
pytest tests/unit/ --cov=fluttercraft --cov-report=html
```

#### Integration Tests
```bash
# Run integration tests (requires Flutter)
pytest tests/integration/ -v

# Run CLI integration tests
pytest tests/integration/test_cli_flows.py -v
```

#### Full Test Suite
```bash
# Run all tests with coverage
pytest --cov=fluttercraft --cov-report=html --cov-report=term

# Generate coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Test Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Modules**: 95%+ (core.py, validation.py)

### Writing Tests

#### Test File Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_validation.py   # Validation utilities
│   ├── test_shell.py        # Shell utilities
│   └── test_core.py         # Core functionality
├── integration/             # Integration tests
│   ├── test_cli_flows.py    # End-to-end CLI tests
│   └── test_project_creation.py
└── fixtures/                # Test data and mocks
    ├── sample_configs/
    └── mock_responses/
```

#### Test Naming Convention
```python
class TestValidation:
    def test_valid_app_names(self):
        """Test that valid app names pass validation."""
        pass
    
    def test_invalid_app_names_raise_error(self):
        """Test that invalid app names raise appropriate errors."""
        pass
```

#### Mocking External Commands
```python
from unittest.mock import patch, MagicMock

@patch('fluttercraft.utils.shell.run_command')
def test_flutter_installation(mock_run_command):
    mock_run_command.return_value = MagicMock(success=True, stdout="Flutter installed")
    # Test implementation
```

---

## 🐛 Debugging Guidelines

### Logging Configuration

FlutterCraft uses `loguru` for logging. Configure debug logging:

```python
from loguru import logger

# Enable debug logging
logger.add("debug.log", level="DEBUG")

# In your code
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Common Debugging Scenarios

#### CLI Command Issues
```bash
# Run with verbose logging
python -m fluttercraft create --help

# Check log files
tail -f ~/.fluttercraft/fluttercraft.log
```

#### Template Rendering Issues
```python
# Test template rendering
from fluttercraft.utils.io import render_template_string

template = "Hello {{ name }}!"
context = {"name": "World"}
result = render_template_string(template, context)
print(result)  # Should print "Hello World!"
```

#### Shell Command Issues
```python
# Test shell commands
from fluttercraft.utils.shell import run_command

result = run_command("flutter --version")
print(f"Success: {result.success}")
print(f"Output: {result.stdout}")
print(f"Error: {result.stderr}")
```

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm Configuration
1. Set Python interpreter to `.venv/bin/python`
2. Enable pytest as test runner
3. Configure code style to use Black formatter
4. Enable type checking with mypy

---

## 📝 Code Style and Standards

### Formatting with Black
```bash
# Format all Python files
black fluttercraft/ tests/

# Check formatting without changes
black --check fluttercraft/ tests/
```

### Linting with Flake8
```bash
# Lint all Python files
flake8 fluttercraft/ tests/

# Configuration in setup.cfg or pyproject.toml
```

### Type Checking with MyPy
```bash
# Type check the codebase
mypy fluttercraft/

# Configuration in mypy.ini
```

### Code Style Guidelines

#### Function Documentation
```python
def validate_app_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Flutter app name according to Flutter conventions.
    
    Args:
        name: App name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Raises:
        ValidationError: If validation fails critically
    """
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Third-party imports
import typer
from loguru import logger
from rich.console import Console

# Local imports
from fluttercraft.utils import validate_app_name
from fluttercraft.config import DEFAULT_ORG_ID
```

#### Error Handling
```python
try:
    result = risky_operation()
    logger.info("Operation successful")
    return result
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError(f"Operation failed: {e}") from e
```

---

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-command

# Make changes and test
pytest tests/unit/ -v

# Format and lint
black fluttercraft/ tests/
flake8 fluttercraft/ tests/

# Commit changes
git add .
git commit -m "feat: add new command functionality"
```

### 2. Testing Changes
```bash
# Test CLI locally
python -m fluttercraft create --help

# Run full test suite
pytest --cov=fluttercraft

# Test with different Python versions (if available)
tox
```

### 3. Documentation Updates
```bash
# Update relevant documentation
# - README.md for user-facing changes
# - docs/ for detailed documentation
# - Docstrings for code changes

# Test documentation builds (if using Sphinx)
cd docs/
make html
```

### 4. Pull Request Preparation
```bash
# Ensure all tests pass
pytest

# Ensure code quality
black --check fluttercraft/ tests/
flake8 fluttercraft/ tests/
mypy fluttercraft/

# Update CHANGELOG.md if applicable
# Push changes and create PR
git push origin feature/new-command
```

---

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Reinstall in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures
```bash
# Run specific failing test with verbose output
pytest tests/unit/test_validation.py::TestAppNameValidation::test_valid_app_names -v -s

# Clear pytest cache
pytest --cache-clear
```

#### CLI Not Working
```bash
# Check installation
pip show fluttercraft

# Reinstall
pip uninstall fluttercraft
pip install -e .
```

### Getting Help

1. **Check the logs**: `~/.fluttercraft/fluttercraft.log`
2. **Run with debug**: Set `LOGURU_LEVEL=DEBUG`
3. **Search issues**: [GitHub Issues](https://github.com/UTTAM-VAGHASIA/fluttercraft/issues)
4. **Ask questions**: Create a new issue with the `question` label

---

## 📚 Additional Resources

- [Python Development Best Practices](https://docs.python-guide.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Typer CLI Framework](https://typer.tiangolo.com/)
- [Rich Terminal Library](https://rich.readthedocs.io/)

---

Happy coding! 🚀
