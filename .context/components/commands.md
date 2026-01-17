---
component: Commands System
layer: Application
last_updated: 2026-01-17
maintainer: Core Team
---

# Commands Component

## Purpose

The commands component implements all CLI commands for FlutterCraft using a command registry pattern. Commands are self-contained, testable units that execute specific user actions.

## Public API

### Command Registry
```python
from fluttercraft.commands.core.registry import CommandRegistry
from fluttercraft.commands.core.executor import CommandExecutor

# Get command system
registry, executor = build_command_system()

# Register a command
registry.register(MyCommand())

# Execute a command
result = executor.execute("command-name", context)
```

### Base Command Class
```python
from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import CommandContext, CommandResult

class MyCommand(Command):
    name = "my-command"
    category = "custom"
    aliases = ["mc", "myc"]
    help_text = "Does something useful"
    
    def execute(self, context: CommandContext) -> CommandResult:
        # Implementation
        return CommandResult(success=True, message="Done!")
```

## Architecture

```
commands/
├── core/                   # Command infrastructure
│   ├── base.py            # Command ABC
│   ├── models.py          # Context, Result, Metadata
│   ├── registry.py        # CommandRegistry
│   └── executor.py        # CommandExecutor
├── bootstrap.py           # Build command system
├── start.py               # Interactive REPL
├── slash_commands.py      # /quit, /help, etc.
├── flutter/               # Flutter commands
│   ├── flutter_command.py # Flutter command aggregator
│   └── version.py         # Version checking
├── fvm/                   # FVM commands
│   ├── fvm_command.py     # FVM command aggregator
│   ├── install.py         # FVM installation
│   ├── uninstall.py       # FVM removal
│   ├── list.py            # List versions
│   ├── releases.py        # Available releases
│   └── version.py         # Version checking
└── help/                  # Help system
    ├── global_help.py     # Global help
    ├── fvm_help.py        # FVM help
    └── handler.py         # Help routing
```

## Dependencies

### Depends On:
- `utils.themed_display` - Display output
- `utils.terminal_utils` - Execute shell commands
- `utils.platform_utils` - Platform detection

### Depended By:
- `main.py` - CLI entry point
- `commands.start` - Interactive REPL

## Command Types

### 1. Slash Commands
Internal CLI commands starting with `/`:
- `/quit` - Exit CLI
- `/clear` - Clear screen
- `/help` - Show help
- `/about` - Show CLI info
- `/theme` - Theme selection

### 2. Flutter Commands
Interact with Flutter SDK:
- `flutter upgrade [--force|--verify-only|--continue|--verbose]`
- `flutter doctor` (coming soon)
- `flutter --version` (coming soon)

### 3. FVM Commands
Manage Flutter versions with FVM:
- `fvm install` - Install FVM
- `fvm uninstall` - Remove FVM
- `fvm list` - List installed versions
- `fvm releases [--channel stable|beta|dev|all]` - List available versions

## Design Patterns

### Command Pattern
Each command is a self-contained object with:
- **Name** - Primary command identifier
- **Aliases** - Alternative names
- **Category** - Grouping (slash, flutter, fvm)
- **Help Text** - User documentation
- **Execute Method** - Implementation

### Registry Pattern
`CommandRegistry` provides:
- Command registration
- Name/alias lookup
- Category filtering
- Metadata generation

### Executor Pattern
`CommandExecutor` handles:
- Command lookup
- Context creation
- Error handling
- Result processing

## Adding a New Command

### 1. Create Command Class

```python
# commands/my_category/my_command.py
from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import CommandContext, CommandResult

class MyCommand(Command):
    name = "my-command"
    category = "my-category"
    aliases = ["mc"]
    help_text = "Does something useful"
    
    def execute(self, context: CommandContext) -> CommandResult:
        # Your implementation
        console = context.console
        console.print("[green]Success![/]")
        return CommandResult(success=True)
```

### 2. Register Command

```python
# commands/bootstrap.py
from fluttercraft.commands.my_category.my_command import MyCommand

def build_command_system():
    registry = CommandRegistry()
    executor = CommandExecutor(registry)
    
    # ... existing commands ...
    registry.register(MyCommand())
    
    return registry, executor
```

### 3. Update Documentation

- Update `.context/components/commands.md` (this file)
- Update `.context/dependencies.yaml` if new dependencies
- Add entry to `CHANGELOG.md`

## Testing

### Unit Tests
Test each command in isolation:

```python
def test_my_command_success():
    cmd = MyCommand()
    context = create_test_context()
    result = cmd.execute(context)
    assert result.success is True
```

### Integration Tests
Test command via executor:

```python
def test_my_command_via_executor():
    registry, executor = build_command_system()
    context = create_test_context()
    result = executor.execute("my-command", context)
    assert result.success is True
```

## Error Handling

Commands should:
1. Catch specific exceptions
2. Return `CommandResult(success=False, message="Error details")`
3. Use Rich Console for user-friendly error messages
4. Log errors appropriately

Example:
```python
def execute(self, context: CommandContext) -> CommandResult:
    try:
        # Do something risky
        result = risky_operation()
        return CommandResult(success=True, message="Success!")
    except SpecificError as e:
        context.console.print(f"[red]Error: {e}[/]")
        return CommandResult(success=False, message=str(e))
    except Exception as e:
        context.console.print(f"[red]Unexpected error: {e}[/]")
        return CommandResult(success=False, message="An unexpected error occurred")
```

## Performance Considerations

- **Command Lookup**: O(1) via dict-based registry
- **Lazy Loading**: Commands are instantiated once at startup
- **Context Reuse**: CommandContext is reused across executions

## Change History

### 2026-01-17 (v0.1.3)
- Removed legacy `command_handler.py` (replaced by executor)
- Consolidated command system documentation
- Updated architecture patterns

### 2025-10-16 (v0.1.2)
- Added Flutter upgrade command
- Added FVM commands (install, uninstall, list, releases)
- Implemented command registry pattern

### 2025-06-15 (v0.1.0)
- Initial command system with slash commands

## Future Plans

See `.context/architecture.yaml` for FINAL architecture migration plan (v0.2.0+):
- Commands will move to `application/commands/`
- Separate domain logic from command handlers
- Enhanced testing framework
