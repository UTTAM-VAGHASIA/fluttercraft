# Code Style Rules

## Overview

FlutterCraft follows strict code style guidelines to ensure consistency, readability, and maintainability across the codebase.

## Formatting

### Black (Required)
- **Line Length**: 88 characters maximum
- **String Quotes**: Double quotes `"` preferred
- **Trailing Commas**: Use in multi-line structures
- **Format Command**: `black fluttercraft/ tests/`

### Flake8 (Required)
- **Max Line Length**: 88 (Black compatible)
- **Ignored Rules**:
  - `E203` - Whitespace before ':' (Black compatibility)
  - `W503` - Line break before binary operator (Black compatibility)
  - `F821` - Undefined name (handled by mypy)
- **Per-File Ignores**:
  - `__init__.py:F401` - Unused imports (re-exports)

## Import Organization

**Order** (enforced):
1. Standard library imports
2. Third-party package imports
3. Local application imports

**Within each group**:
- `import` statements first
- `from ... import ...` statements second
- Alphabetically sorted

**Example:**
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party packages
import typer
from rich.console import Console
from rich.panel import Panel

# Local imports
from fluttercraft.commands.core import Command, CommandContext
from fluttercraft.utils.terminal_utils import run_with_loading
```

## Type Hints

### Required
- All function signatures must have type hints
- All class attributes should have type hints
- Return types are mandatory

### Modern Syntax
- Use `from __future__ import annotations` for forward references
- Prefer modern syntax: `list[str]` over `List[str]` (Python 3.10+)
- Use `|` for Union types: `str | None` over `Optional[str]`

**Example:**
```python
from __future__ import annotations

from typing import Any

def process_data(
    items: list[str],
    config: dict[str, Any],
    max_count: int | None = None
) -> tuple[int, str]:
    """Process data items."""
    pass
```

## Naming Conventions

### Functions and Methods
- **Style**: `snake_case`
- **Descriptive**: Use clear, descriptive names
- **Verbs**: Start with action verbs

```python
def check_flutter_version() -> dict[str, Any]:
    pass

def run_with_loading(cmd: list[str]) -> subprocess.CompletedProcess:
    pass
```

### Classes
- **Style**: `PascalCase`
- **Nouns**: Use descriptive nouns
- **Suffixes**: Use standard suffixes (`Service`, `Manager`, `Command`, etc.)

```python
class CommandRegistry:
    pass

class ThemeDisplayService:
    pass

class FVMCommand(Command):
    pass
```

### Constants
- **Style**: `UPPER_SNAKE_CASE`
- **Module Level**: Define at module level
- **Descriptive**: Clear purpose

```python
MAX_LINE_LENGTH = 88
DEFAULT_THEME = "gradient"
TIMEOUT_SECONDS = 30
```

### Private Members
- **Style**: `_leading_underscore`
- **Internal**: Not part of public API

```python
class MyClass:
    def __init__(self) -> None:
        self._internal_state = {}
    
    def _helper_method(self) -> None:
        pass
```

### Module Names
- **Style**: `snake_case.py`
- **Lowercase**: All lowercase
- **Descriptive**: Clear purpose

```
terminal_utils.py
theme_manager.py
command_registry.py
```

## Docstrings

### Style
- **Format**: Google-style docstrings
- **Quotes**: Triple double-quotes `"""`
- **Required For**: All public functions, classes, and modules

### Module Docstrings
```python
"""Utility functions for terminal operations.

This module provides functions for executing shell commands with loading
indicators and handling terminal I/O operations.
"""
```

### Function Docstrings
```python
def check_flutter_version(silent: bool = False) -> dict[str, Any]:
    """Check if Flutter is installed and get version information.

    Uses 'flutter upgrade --verify-only' to check both installation and updates.

    Args:
        silent: If True, suppress all loading indicators and output

    Returns:
        dict: {
            "installed": bool,
            "current_version": str or None,
            "latest_version": str or None,
            "update_available": bool
        }

    Raises:
        FileNotFoundError: If Flutter is not installed
        subprocess.TimeoutExpired: If command times out

    Example:
        >>> info = check_flutter_version()
        >>> print(info["current_version"])
        '3.19.0'
    """
    pass
```

### Class Docstrings
```python
class CommandRegistry:
    """Central registry for FlutterCraft commands.

    Maintains a mapping of command names and aliases to Command instances.
    Supports command lookup by name or alias, category filtering, and
    metadata generation.

    Attributes:
        _commands: Dict mapping command names/aliases to Command instances
        _by_category: Dict grouping commands by category

    Example:
        >>> registry = CommandRegistry()
        >>> registry.register(MyCommand())
        >>> cmd = registry.get("my-command")
    """
    pass
```

## Error Handling

### Specific Exceptions First
```python
try:
    result = risky_operation()
except FileNotFoundError as e:
    # Handle missing file
    console.print(f"[red]File not found: {e}[/]")
except PermissionError as e:
    # Handle permission issue
    console.print(f"[red]Permission denied: {e}[/]")
except Exception as e:
    # Handle any other error
    console.print(f"[red]Unexpected error: {e}[/]")
```

### User-Friendly Messages
```python
# Bad
raise ValueError("Invalid input")

# Good
raise ValueError(
    "Invalid Flutter version format. Expected 'X.Y.Z', got '{version}'"
)
```

### Return Safe Defaults
```python
def get_git_info() -> dict[str, Any]:
    """Get git info, or safe defaults on error."""
    try:
        # Try to get git info
        return {"branch": "main", "has_changes": True}
    except Exception:
        # Return safe defaults, don't crash
        return {"branch": "", "has_changes": False}
```

### Rich Console for Errors
```python
from rich.console import Console

console = Console()

try:
    result = operation()
except Exception as e:
    console.print(f"[red]✗[/] Operation failed: {e}")
    return CommandResult(success=False, message=str(e))
```

## Code Organization

### Blank Lines
- **2 blank lines** before top-level classes and functions
- **1 blank line** between methods
- **1 blank line** between logical sections within functions

```python
import os
import sys


class MyClass:
    def __init__(self) -> None:
        self.value = 0
    
    def method_one(self) -> None:
        pass
    
    def method_two(self) -> None:
        pass


def standalone_function() -> None:
    # Section 1
    setup()
    
    # Section 2
    process()
    
    # Section 3
    teardown()
```

### Line Length
- **Maximum**: 88 characters
- **Break Long Lines**: Use parentheses for line continuation

```python
# Good
result = some_function(
    argument_one,
    argument_two,
    argument_three,
    keyword_argument=value
)

# Good
message = (
    "This is a very long message that needs to be "
    "split across multiple lines for readability"
)
```

## Architecture Compliance

### Layer Dependencies
Follow the dependency rules in `.context/architecture.yaml`:

```python
# ✅ ALLOWED
from fluttercraft.commands.core import Command  # Application → Core
from fluttercraft.utils.terminal_utils import run_cmd  # Application → Infrastructure

# ❌ FORBIDDEN
from fluttercraft.presentation.cli import app  # Application → Presentation (wrong direction!)
```

### Component Boundaries
- Don't bypass facades
- Use public APIs only
- Respect abstraction layers

```python
# ✅ GOOD - Use facade
from fluttercraft.utils.themed_display import display
display.success("Done!")

# ❌ BAD - Bypass facade
from fluttercraft.utils.themes.service import ThemeDisplayService
service = ThemeDisplayService()
# ... complex direct usage
```

## Testing

### Test File Naming
- **Pattern**: `test_<module_name>.py`
- **Location**: Mirror source structure in `tests/`

```
fluttercraft/utils/terminal_utils.py
tests/unit/utils/test_terminal_utils.py
```

### Test Function Naming
- **Pattern**: `test_<what>_<condition>_<expected>`
- **Descriptive**: Clear what's being tested

```python
def test_command_execution_success_returns_output():
    """Test that successful command returns output."""
    pass

def test_command_execution_failure_raises_error():
    """Test that failed command raises appropriate error."""
    pass

def test_git_info_not_in_repo_returns_defaults():
    """Test that git info returns safe defaults when not in a repo."""
    pass
```

## Enforcement

### Pre-Commit Checks (Required)
```bash
# Format
black fluttercraft/ tests/

# Lint
flake8 fluttercraft/

# Type check (optional but recommended)
mypy fluttercraft/
```

### CI/CD Validation
All PRs must pass:
- Black formatting check
- Flake8 linting
- Type checking (if enabled)
- All tests

## Violations

### Common Violations to Avoid
1. **Missing type hints** on public functions
2. **Improper import order** (not grouped/sorted)
3. **Lines exceeding 88 characters**
4. **Missing docstrings** on public API
5. **Catching generic `Exception`** without specific exceptions first
6. **Using `pass` without comment** in empty methods
7. **Hardcoded paths/values** instead of constants

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Rules](https://flake8.pycqa.org/en/latest/user/error-codes.html)
- [PEP 8](https://peps.python.org/pep-0008/) - Python Style Guide
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

---

**Last Updated**: 2026-01-17  
**Version**: 1.0.0 (FINAL Architecture)
