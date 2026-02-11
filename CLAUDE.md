# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FlutterCraft is a Python CLI tool for automating Flutter development workflows. It provides an interactive command-line interface for managing Flutter SDK versions, FVM (Flutter Version Manager), and future features like project creation and backend integration.

**Current Status**: The CLI is primarily supported on Windows. macOS and Linux support is planned.

## Development Commands

### Setup
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # macOS/Linux
pip install -e .
```

### Running the CLI
```bash
fluttercraft start        # Start interactive CLI
fluttercraft --help       # Show help
fluttercraft theme <name> # Change theme
```

### Linting
```bash
pip install flake8
flake8 fluttercraft/      # Uses .flake8 config
```

Configuration: `.flake8` - max line length 88, various ignores for alignment with code style

### Testing
No test framework is established yet. CI runs basic smoke tests (`fluttercraft --help`).

## Architecture

### Command System Architecture

The CLI uses a **modular command registry pattern** with three key components:

1. **Command Registry** (`fluttercraft/commands/core/registry.py`)
   - Central registry mapping command tokens to handler classes
   - Supports aliases and category grouping
   - Used to generate auto-completion metadata

2. **Command Executor** (`fluttercraft/commands/core/executor.py`)
   - Dispatches user input to registered commands
   - Handles token parsing and error recovery
   - Coordinates command lookup by name or alias

3. **Command Base Class** (`fluttercraft/commands/core/base.py`)
   - Abstract base requiring `execute(context, args) -> CommandResult`
   - Each command carries `CommandMetadata` (name, help_text, category, aliases, keywords)
   - Examples: `QuitSlashCommand`, `FVMCommand`, `FlutterCommand`

**Command Types**:
- **Slash commands** (`/quit`, `/clear`, `/help`, `/about`, `/theme`) - CLI control commands
- **FVM commands** (`fvm install`, `fvm list`, `fvm releases`) - Flutter Version Manager integration
- **Flutter commands** (`flutter upgrade`) - Direct Flutter SDK operations

**Command Registration** (`fluttercraft/commands/bootstrap.py`):
All commands are registered in `build_command_system()`, which creates the registry and returns a configured executor.

### Service Layer Architecture

The CLI uses a **service-oriented design** for cross-cutting concerns:

1. **ThemeDisplayService** (`fluttercraft/utils/themes/service.py`)
   - Central facade for all themed output rendering
   - Renders ASCII art with gradients
   - Provides semantic styling methods: `print_success()`, `print_error()`, `print_warning()`, `print_info()`
   - Manages welcome headers, help text, and about screens
   - Coordinates with ThemeManager for current theme state

2. **ThemeManager** (`fluttercraft/utils/themes/theme_manager.py`)
   - Manages theme persistence and switching
   - Loads/saves user theme preferences
   - Provides theme objects with semantic color mappings

3. **Theme Objects** (`fluttercraft/utils/themes/theme.py`)
   - Structured theme definitions with semantic naming
   - Contains gradient colors, semantic categories (status, text, etc.)
   - Used by service to get consistent color values

### Data Flow

**Startup Flow** (`fluttercraft/commands/start.py`):
1. Platform detection → show platform-not-supported if macOS/Linux
2. Display loading spinner while gathering system info
3. Silent checks: `check_flutter_version()`, `check_fvm_version()`
4. Build command system via `bootstrap.build_command_system()`
5. Create `CommandContext` with platform/flutter/fvm info
6. Enter REPL loop: prompt → executor.dispatch() → display result

**Command Execution Flow**:
```
User Input → CommandExecutor.dispatch()
           → Registry lookup (by name/alias)
           → Command.execute(context, args)
           → Returns CommandResult
           → Display result.message
```

**Context Object** (`CommandContext`):
- Carries runtime state: platform_info, flutter_info, fvm_info, console, prompt_history
- Passed to every command execution
- Commands can update context (e.g., refresh Flutter version after upgrade)

### UI/Theming System

The theming system has a layered architecture:

1. **Theme Definitions** - Color palettes and semantic mappings
2. **Gradient Engine** - Applies color gradients to ASCII art
3. **ThemeDisplayService** - High-level API for themed rendering
4. **CLI Components** - Use service methods for consistent styling

All themed output MUST go through `ThemeDisplayService` to ensure consistency. Direct Rich console calls should only be used for unthemed output.

### Project Structure

```
fluttercraft/
├── commands/
│   ├── core/           # Command infrastructure (base, registry, executor, models)
│   ├── fvm/            # FVM command implementations (install, list, releases, etc.)
│   ├── flutter/        # Flutter command implementations
│   ├── help/           # Help command implementations
│   ├── theme/          # Theme selection and management
│   ├── bootstrap.py    # Command registration
│   ├── start.py        # Main CLI entry point and REPL
│   └── *_command.py    # Individual command families
├── utils/
│   ├── themes/         # Theme system (service, manager, theme definitions, gradients)
│   ├── beautiful_prompt.py  # Bordered input prompt with auto-completion
│   ├── themed_display.py    # Legacy display utilities (being migrated to service)
│   └── *_utils.py      # Platform, terminal, system utilities
├── config/             # Configuration management (currently minimal)
└── main.py            # Typer app definition and CLI entry point
```

## Code Conventions

### Command Implementation Pattern

When adding new commands:
1. Create a command class inheriting from `Command`
2. Define `CommandMetadata` with name, help_text, category, aliases
3. Implement `execute(context: CommandContext, args: list[str]) -> CommandResult`
4. Register in `bootstrap.build_command_system()`
5. Use `ThemeDisplayService` methods for all output

### Import Organization

The codebase uses relative imports within packages and absolute imports across packages. Use `from __future__ import annotations` for type hints.

### Theme Usage

Always use `ThemeDisplayService` for themed output:
```python
service = ThemeDisplayService(console)
service.print_success("Operation completed")
service.print_error("Something went wrong")
```

Never hardcode colors - use semantic theme properties.

## Future Architecture Notes

The roadmap includes:
- Cross-platform support (macOS/Linux) - will require conditional platform handling
- Project creation wizard - likely new `create` command family
- Backend integration (Firebase/Supabase) - may need new service layer
- GitHub automation - git command integration
- More theme support - extensible theme system already in place
