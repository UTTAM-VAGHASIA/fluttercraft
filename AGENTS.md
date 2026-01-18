# AGENTS.md - FlutterCraft Development Guide

This guide is for AI coding agents and developers working on FlutterCraft.

## 🔄 Standard Development Workflow (CRITICAL)

**This is the mandatory workflow for all features/fixes. Follow it strictly:**

### Step 1: Implementation
1. **Read the spec** from `.specs/features/` or `.specs/fixes/`
2. **Create TODO list** using TodoWrite tool to track tasks
3. **Implement the feature/fix**
   - Make code changes
   - Update relevant files
4. **Syntax check** with `python -m py_compile <file>`
5. **Mark TODOs as completed** as you finish each task

### Step 2: User Testing (DO NOT SKIP!)
1. **Present implementation** to user with:
   - Summary of changes
   - Files modified
   - Test instructions
2. **User tests** the implementation
3. **If issues found**:
   - Fix the issues
   - Go back to Step 2 (iterate until approved)
4. **Wait for user approval** - User will say "looks good", "perfect", etc.

### Step 3: Documentation Update (ONLY AFTER APPROVAL)
1. **Update CHANGELOG.md**:
   - Add entry for the feature/fix under appropriate version
   - Use Keep a Changelog format
   - Include Added/Changed/Fixed sections as needed
   - Reference the commit/feature clearly
2. **Update relevant documentation**:
   - `.specs/features/<feature>/implementation.md` - Mark tasks complete
   - `.context/components/*.md` - If public APIs changed
   - `.context/dependencies.yaml` - If dependencies added/changed
   - `README.md` - If user-facing features added (major changes only)
3. **Verify completeness**:
   - All TODOs marked as completed
   - Progress tracking updated
   - No placeholder text left

### Step 4: Code Quality (ONLY AFTER DOCUMENTATION)
1. **Activate virtual environment**:
   ```bash
   source .venv/Scripts/activate  # macOS/Linux
   .\.venv\Scripts\activate       # Windows (if using cmd)
   source .venv/Scripts/activate  # Windows (if using bash)
   ```
2. **Run Black formatter**:
   ```bash
   black fluttercraft/
   ```
3. **Run Flake8 linter**:
   ```bash
   flake8 fluttercraft/
   ```
   (E203 errors are expected and ignored per .flake8 config)

### Step 4: Code Quality (ONLY AFTER DOCUMENTATION)
1. **Activate virtual environment**:
   ```bash
   source .venv/Scripts/activate  # macOS/Linux
   .\.venv\Scripts\activate       # Windows (if using cmd)
   source .venv/Scripts/activate  # Windows (if using bash)
   ```
2. **Run Black formatter**:
   ```bash
   black fluttercraft/
   ```
3. **Run Flake8 linter**:
   ```bash
   flake8 fluttercraft/
   ```
   (E203 errors are expected and ignored per .flake8 config)

### Step 5: Commit (ONLY AFTER BLACK/FLAKE8)
1. **Stage files** (including documentation):
   ```bash
   git add <files> CHANGELOG.md
   ```
2. **Create comprehensive commit**:
   - Follow Conventional Commits format
   - Include detailed description of changes
   - Reference spec and progress
   - Add user feedback quote
3. **Verify commit**:
   ```bash
   git log --oneline -1
   ```

### Step 5: Commit (ONLY AFTER BLACK/FLAKE8)
1. **Stage files** (including documentation):
   ```bash
   git add <files> CHANGELOG.md
   ```
2. **Create comprehensive commit**:
   - Follow Conventional Commits format
   - Include detailed description of changes
   - Reference spec and progress
   - Add user feedback quote
3. **Verify commit**:
   ```bash
   git log --oneline -1
   ```

### Step 6: Push (ONLY IF USER REQUESTS)
- User will explicitly say "push it" or "push this commit"
- **Never auto-push** without user request
- Command: `git push origin <branch-name>`

---

## ⚠️ Critical Rules

### NEVER Do These:
- ❌ **DO NOT commit immediately** after implementation
- ❌ **DO NOT run Black/Flake8** during iteration or before documentation
- ❌ **DO NOT push** without explicit user request
- ❌ **DO NOT skip user testing**
- ❌ **DO NOT skip documentation updates**
- ❌ **DO NOT batch multiple features** in one commit
- ❌ **DO NOT forget to update CHANGELOG.md**

### ALWAYS Do These:
- ✅ **ALWAYS activate .venv** before running Python commands
- ✅ **ALWAYS use TodoWrite** to track implementation tasks
- ✅ **ALWAYS wait for user approval** before formatting/committing
- ✅ **ALWAYS update CHANGELOG.md** after user approval
- ✅ **ALWAYS update relevant documentation** before formatting
- ✅ **ALWAYS test syntax** with `python -m py_compile`
- ✅ **ALWAYS provide clear test instructions** to user

### Virtual Environment (CRITICAL):
```bash
# Activate BEFORE any Python command (pip, black, flake8, pytest, etc.)
source .venv/Scripts/activate

# Examples:
source .venv/Scripts/activate && black fluttercraft/
source .venv/Scripts/activate && flake8 fluttercraft/
source .venv/Scripts/activate && pip install <package>
```

---

## 📋 Example Session Flow

```
1. User: "Implement feature X"
2. Agent: [Reads spec, creates TODOs, implements]
3. Agent: "Implementation complete! Here's what I did... Test it by..."
4. User: [Tests and finds issue Y]
5. Agent: [Fixes issue Y]
6. Agent: "Fixed issue Y. Test again?"
7. User: "Perfect, it's working!"
8. Agent: [Updates CHANGELOG.md and relevant docs]
9. Agent: "Documentation updated. Running Black/Flake8..."
10. Agent: [Runs Black + Flake8, commits with details]
11. User: "Push it"
12. Agent: [Pushes to remote]
```

---

## Project Overview

FlutterCraft is a Python CLI tool for automating Flutter development workflows. Built with Typer, Rich, and Prompt Toolkit, it provides an interactive command-line interface with beautiful theming, FVM integration, and Flutter command automation.

- **Language**: Python 3.10+
- **Main Framework**: Typer (CLI), Rich (UI)
- **Architecture**: Command registry pattern with modular services
- **Entry Point**: `fluttercraft/main.py`

---

## Build, Lint, and Test Commands

### Development Setup
```bash
# Clone and setup
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft.git
cd fluttercraft
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -e .
```

### Running the CLI
```bash
# Start interactive CLI
fluttercraft start
python -m fluttercraft start

# Show help
fluttercraft --help
python -m fluttercraft --help
```

### Linting
```bash
# Install flake8
pip install flake8

# Lint entire codebase
flake8 fluttercraft/

# Lint specific file
flake8 fluttercraft/commands/start.py
```

**Flake8 Configuration** (`.flake8`):
- Max line length: 88 (Black compatible)
- Ignored: `E203, W503, F821`
- Per-file ignores: `__init__.py:F401`

### Testing
```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests (when available)
pytest tests/

# Run specific test file
pytest tests/unit/test_validation.py -v

# Run specific test
pytest tests/unit/test_validation.py::TestClass::test_method -v

# Run with coverage
pytest --cov=fluttercraft --cov-report=html
```

### Formatting
```bash
# Install black
pip install black

# Format code
black fluttercraft/ tests/

# Check formatting
black --check fluttercraft/
```

### CI/CD
GitHub Actions workflow in `.github/workflows/cli-check.yml`:
- Runs on: Ubuntu (Python 3.10)
- Steps: Install deps → Lint with flake8 → Run CLI help

---

## Code Style Guidelines

### Import Organization

**Order**: Standard library → Third-party → Local

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Third-party packages
import typer
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt

# Local imports
from fluttercraft.commands.core import Command, CommandContext, CommandResult
from fluttercraft.utils.terminal_utils import run_with_loading
```

### Type Hints

- **Always use type hints** for function signatures
- Use `from __future__ import annotations` for forward references
- Prefer modern syntax where possible (Python 3.10+)

```python
from __future__ import annotations

from typing import Dict, Optional

def check_version(silent: bool = False) -> Dict[str, Any]:
    """Check Flutter version."""
    pass

class CommandRegistry:
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
```

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`
- **Modules**: `snake_case.py`

```python
# Constants
MAX_LINE_LENGTH = 88
DEFAULT_THEME = "gradient"

# Classes
class CommandRegistry:
    pass

# Functions
def run_with_loading(cmd: list[str]) -> subprocess.CompletedProcess:
    pass

# Private
def _parse_output(output: str) -> dict:
    pass
```

### Docstrings

Use Google-style docstrings with triple quotes:

```python
def check_flutter_version(silent: bool = False) -> dict:
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
    """
    pass
```

### Error Handling

- Catch specific exceptions first
- Use Rich Console for user-facing errors
- Return structured results via `CommandResult`
- Log errors appropriately

```python
try:
    result = run_command(cmd)
    return CommandResult(success=True, message="Operation successful")
except FileNotFoundError:
    console.print("[red]Command not found[/]")
    return CommandResult(success=False, message="Command not found")
except Exception as e:
    console.print(f"[red]Error: {str(e)}[/]")
    return CommandResult(success=False, message=str(e))
```

### Formatting Standards

- **Line length**: 88 characters max (Black style)
- **Indentation**: 4 spaces
- **Quotes**: Use double quotes `"` for strings
- **Trailing commas**: Use in multi-line structures
- **Blank lines**: 2 before top-level classes/functions, 1 between methods

### Architecture Patterns

FlutterCraft uses a command registry architecture:

```python
# Commands inherit from base Command class
from fluttercraft.commands.core.base import Command

class MyCommand(Command):
    def execute(self, context: CommandContext) -> CommandResult:
        # Implementation
        return CommandResult(success=True)

# Register commands
from fluttercraft.commands.core.registry import CommandRegistry

registry = CommandRegistry()
registry.register(MyCommand())
```

**Core Components:**
- `CommandRegistry`: Central command dispatcher
- `Command`: Base class for all commands
- `CommandContext`: Runtime context (platform, Flutter, FVM info)
- `CommandResult`: Execution outcome (success, message, payload)
- `CommandMetadata`: Declarative command metadata

### Rich UI Guidelines

Use Rich for all terminal output:

```python
from rich.console import Console
from rich.panel import Panel

console = Console()

# Success messages
console.print("[green]✓[/] Operation successful")

# Error messages
console.print("[red]✗[/] Operation failed")

# Panels
console.print(Panel("Content", title="Title", border_style="cyan"))
```

---

## Project Structure

```
fluttercraft/
├── main.py                    # Entry point (Typer app)
├── __main__.py                # Python -m entry
├── commands/
│   ├── core/                  # Command registry & base classes
│   │   ├── registry.py        # CommandRegistry
│   │   ├── models.py          # CommandContext, CommandResult
│   │   ├── base.py            # Command base class
│   │   └── executor.py        # Command execution logic
│   ├── flutter/               # Flutter commands (version, upgrade)
│   ├── fvm/                   # FVM commands (install, list, releases)
│   ├── theme/                 # Theme selection commands
│   └── help/                  # Help system
├── utils/
│   ├── themes/                # Theming service layer
│   ├── terminal_utils.py      # Terminal operations
│   ├── system_utils.py        # System checks
│   └── display_utils.py       # Display helpers
└── config/                    # Configuration
```

---

## Development Workflow

### Branching Strategy
- Feature branches: `feature/<name>`
- Bug fixes: `fix/<name>`
- Always branch from `main`

### Commit Messages
Use Conventional Commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

```bash
git commit -m "feat: add FVM release listing command"
git commit -m "fix: resolve version check timeout issue"
```

### Pre-commit Checklist
1. Format code: `black fluttercraft/ tests/`
2. Lint code: `flake8 fluttercraft/`
3. Run tests: `pytest tests/` (if tests exist)
4. Update docs if needed
5. Test CLI manually: `fluttercraft start`

### Pull Request Guidelines
- Keep PRs focused and small
- Include clear description
- Update relevant documentation
- Ensure CI passes
- Add tests for new features (when test framework is established)

---

## Context Management System

FlutterCraft uses a comprehensive context management system for AI coding agents and developers.

### Before Making Changes

**Always load context first:**

```bash
# 1. Read the architecture
cat .context/architecture.yaml

# 2. Read dependency graph
cat .context/dependencies.yaml

# 3. Read relevant component docs
cat .context/components/commands.md   # For command changes
cat .context/components/themes.md     # For theme changes
cat .context/components/utils.md      # For utility changes

# 4. Review code style rules
cat .context/rules/code-style.md
```

### Directory Structure

```
.context/
├── README.md                   # Context system guide
├── architecture.yaml           # FINAL architecture specification
├── dependencies.yaml           # Complete dependency graph
├── components/                 # Component documentation
│   ├── commands.md            # Commands system
│   ├── themes.md              # Theming system
│   └── utils.md               # Utilities
└── rules/                      # Development rules
    └── code-style.md          # Code style enforcement
```

## Spec-Driven Development

**Every change must start with a spec** (feature/fix/refactor).

### Creating a Spec

```bash
# For a new feature
mkdir -p .specs/features/<feature-name>
cp .specs/.templates/feature.md .specs/features/<feature-name>/spec.md
# Fill in the spec

# For a bug fix
mkdir -p .specs/fixes/<bug-id>
cp .specs/.templates/fix.md .specs/fixes/<bug-id>/spec.md
# Fill in the spec

# For refactoring
mkdir -p .specs/refactoring/<refactor-name>
cp .specs/.templates/refactor.md .specs/refactoring/<refactor-name>/spec.md
# Fill in the spec
```

### Spec Templates

Located in `.specs/.templates/`:
- `feature.md` - 17-section feature specification
- `fix.md` - 18-section bug fix specification
- `refactor.md` - 16-section refactoring specification

### Development Workflow

1. **Create Spec** - Document what you're building/fixing
2. **Load Context** - Read relevant component docs
3. **Implement** - Follow the spec strictly
4. **Update Context** - Update component docs if needed
5. **Update Dependencies** - Update `.context/dependencies.yaml` if needed
6. **Submit PR** - Reference the spec in PR description

### For AI Agents

**Required Files to Load:**
```bash
# Full context
.context/architecture.yaml
.context/dependencies.yaml
.context/components/<relevant>.md
.context/rules/code-style.md

# Spec (if exists)
.specs/<type>/<name>/spec.md
```

**Session Tracking:**
```bash
# Create session directory
mkdir .context/sessions/<session-id>

# Track your work
# - context.md: Session context
# - changes.md: Changes made
# - decisions.md: Decisions log
```

---

## Architecture Migration

FlutterCraft is migrating to FINAL architecture (Clean Architecture with 5 layers).

### Current State (v0.1.3)
- Command registry pattern
- Modular services
- Component-based organization

### Target State (v0.2.0+)

```
fluttercraft/
├── domain/              # Business logic (no dependencies)
│   ├── models/         # Domain entities
│   └── services/       # Business logic services
├── application/         # Use cases
│   ├── commands/       # Command implementations
│   └── handlers/       # Command orchestration
├── infrastructure/      # External dependencies
│   ├── terminal/       # Terminal I/O
│   ├── storage/        # Configuration
│   └── platform/       # Platform-specific code
├── presentation/        # UI Layer
│   ├── cli/            # CLI app
│   ├── ui/             # UI components
│   └── themes/         # Theming
└── core/               # Shared kernel
    ├── base/           # Abstract base classes
    └── common/         # Common utilities
```

See `.context/architecture.yaml` for complete migration plan.

---

## Quality Gates

### Pre-Commit (Required)
```bash
# 1. Format
black fluttercraft/ tests/

# 2. Lint
flake8 fluttercraft/

# 3. Type check (optional)
mypy fluttercraft/

# 4. Run affected tests
pytest tests/
```

### Pre-Push (Required)
- All tests pass
- Coverage >= 80%
- Documentation updated
- CHANGELOG.md updated

### Pull Request (Required)
- Spec provided and followed
- Component context updated (if public API changed)
- Dependencies.yaml updated (if dependencies changed)
- CI/CD passes
- Code review approved

---

## Additional Notes

- **Python Version**: Requires Python 3.10+ (uses modern type hints)
- **Dependencies**: typer[all], pyfiglet, colorama, rich, prompt_toolkit, pygments
- **Platform Support**: Currently Windows-only CLI (cross-platform planned)
- **Documentation**: See `docs/` for detailed guides and architecture
- **Contributing**: Read `CONTRIBUTING.md` and `docs/contributing.md`

### Key Documentation Files
- `AGENTS.md` - This file (AI agent development guide)
- `.context/architecture.yaml` - Complete architecture specification
- `.context/dependencies.yaml` - Dependency graph and impact analysis
- `.context/components/*.md` - Component-level documentation
- `.specs/README.md` - Spec-driven development workflow

---

**Last Updated**: 2026-01-17  
**Version**: 1.0.0 (FINAL Architecture)  
**For Questions**: See GitHub Issues or create new issue with `question` label
