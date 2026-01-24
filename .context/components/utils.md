---
component: Utilities
layer: Infrastructure
last_updated: 2026-01-17
maintainer: Core Team
---

# Utilities Component

## Purpose

Provides shared utility functions for terminal operations, platform detection, system utilities, and display helpers. These are low-level functions used across the application.

## Public API

### Terminal Utilities
```python
from fluttercraft.utils.terminal_utils import run_with_loading, run_flutter_command

# Execute command with loading indicator
result = run_with_loading(
    ["flutter", "--version"],
    status_message="Checking Flutter version...",
    should_display_command=True,
    clear_on_success=True
)

# Execute Flutter-specific command
output = run_flutter_command(["upgrade", "--verify-only"])
```

### Platform Utilities
```python
from fluttercraft.utils.platform_utils import (
    get_platform_info,
    get_git_info,
    get_current_path,
    is_windows,
    is_macos,
    is_linux
)

# Get platform information
platform_info = get_platform_info()
# Returns: {"system": "Windows", "release": "10", ...}

# Get git information
git_info = get_git_info()
# Returns: {"branch": "main", "has_changes": True}

# Get current path (truncated for display)
path = get_current_path()
# Returns: "C:\\Users\\...\\fluttercraft"

# Platform checks
if is_windows():
    # Windows-specific code
    pass
```

### System Utilities
```python
from fluttercraft.utils.system_utils import check_chocolatey_installed

# Check if Chocolatey is installed (Windows)
choco_info = check_chocolatey_installed()
# Returns: {"installed": True, "version": "1.2.0"}
```

### Beautiful Prompt
```python
from fluttercraft.utils.beautiful_prompt import create_beautiful_prompt

# Create interactive prompt with auto-completion
user_input = create_beautiful_prompt(
    registry=command_registry,
    console=console,
    flutter_info=flutter_info,
    fvm_info=fvm_info,
    platform_info=platform_info
)
```

### Animations
```python
from fluttercraft.utils.animations.engine import AnimationEngine
from fluttercraft.utils.animations import effects

# Run an animation
engine = AnimationEngine()
engine.animate(
    renderable_factory=lambda t: Text(f"Progress: {t:.2f}"),
    duration=1.0,
    easing=effects.ease_out_cubic
)
```

## Architecture

```
utils/
├── terminal_utils.py       # Command execution, loading indicators
├── platform_utils.py       # Platform detection, git/path utilities
├── system_utils.py         # System checks (Chocolatey, etc.)
├── beautiful_prompt.py     # Advanced prompt with completions
├── beautiful_display.py    # Display utilities (legacy, to be refactored)
├── themed_display.py       # Facade to theme service
└── animations/             # Animation system
    ├── engine.py           # Animation driver
    └── effects.py          # Easing functions
```

## Dependencies

### Depends On:
- `rich` - Terminal formatting
- `subprocess` - Command execution
- `prompt_toolkit` - Interactive prompts
- `pygments` - Syntax highlighting

### Depended By:
- `commands/*` - All command implementations
- `presentation/*` - UI components

## Key Functions

### Terminal Utils

#### `run_with_loading(cmd, status_message, ...)`
Executes a subprocess command with a loading spinner.

**Parameters:**
- `cmd` (list[str]): Command and arguments
- `status_message` (str): Message to display during execution
- `should_display_command` (bool): Show command being executed
- `clear_on_success` (bool): Clear spinner on success
- `show_output_on_failure` (bool): Show stderr on failure

**Returns:**
- `subprocess.CompletedProcess`: Command result

**Example:**
```python
result = run_with_loading(
    ["git", "status"],
    status_message="Checking git status...",
    should_display_command=False,
    clear_on_success=True
)
```

#### `run_flutter_command(args, ...)`
Specialized wrapper for Flutter commands.

**Parameters:**
- `args` (list[str]): Flutter command arguments (without 'flutter')
- `show_output` (bool): Display output in real-time

**Returns:**
- `str`: Command output

**Example:**
```python
output = run_flutter_command(["doctor", "-v"])
```

### Platform Utils

#### `get_platform_info()`
Returns comprehensive platform information.

**Returns:**
```python
{
    "system": "Windows",  # Windows, Darwin, Linux
    "release": "10",
    "version": "10.0.19045",
    "machine": "AMD64",
    "processor": "Intel64 Family 6 Model 142",
    "python_version": "3.10.0",
    "shell": "C:\\Windows\\System32\\cmd.exe",
    "path": "C:\\Python310;..."
}
```

#### `get_git_info()`
Returns git branch and status.

**Returns:**
```python
{
    "branch": "main",        # Current branch name or ""
    "has_changes": True      # True if uncommitted changes
}
```

**Error Handling:**
Returns `{"branch": "", "has_changes": False}` if:
- Not in a git repository
- Git not installed
- Timeout (> 2 seconds)

#### `get_current_path()`
Returns current working directory, truncated for display.

**Returns:**
```python
"C:\\Users\\username\\projects\\fluttercraft"
# or if path is long:
"C:\\...\\projects\\fluttercraft"
```

**Truncation:**
- Max length: 50 characters
- Shows first and last parts of path
- Uses `...` for middle

#### Platform Check Functions

```python
is_windows()  # True on Windows
is_macos()    # True on macOS
is_linux()    # True on Linux
```

Use these instead of direct `platform.system()` checks for consistency.

### System Utils

#### `check_chocolatey_installed()`
Checks if Chocolatey package manager is installed (Windows only).

**Returns:**
```python
{
    "installed": True,
    "version": "1.2.0"
}
# or
{
    "installed": False,
    "version": None
}
```

**Usage:**
```python
choco = check_chocolatey_installed()
if not choco["installed"]:
    console.print("[yellow]Chocolatey not installed[/]")
```

## Design Patterns

### Separation of Concerns
- **Terminal Utils**: Command execution and I/O
- **Platform Utils**: Platform detection and system info
- **System Utils**: External tool detection
- **Display Utils**: UI and formatting

### Error Handling
All utility functions follow this pattern:

1. Try to perform operation
2. Catch specific exceptions first
3. Return safe defaults on error
4. Never crash the application

**Example:**
```python
def get_git_info():
    try:
        # Try to get git info
        result = subprocess.run(...)
        return {"branch": result.stdout, ...}
    except subprocess.TimeoutExpired:
        return {"branch": "", "has_changes": False}
    except FileNotFoundError:
        return {"branch": "", "has_changes": False}
    except Exception:
        return {"branch": "", "has_changes": False}
```

### Configuration
- Timeouts are configurable via environment variables
- Loading indicators can be disabled (silent mode)
- Output verbosity is controllable

## Performance

- **Command Execution**: Depends on external command (Flutter, Git, etc.)
- **Platform Detection**: < 1ms (cached)
- **Git Info**: < 100ms (with 2s timeout)
- **Path Operations**: < 1ms

## Testing

### Unit Tests
```python
def test_platform_detection():
    info = get_platform_info()
    assert "system" in info
    assert info["system"] in ["Windows", "Darwin", "Linux"]

def test_git_info_not_in_repo(tmp_path):
    os.chdir(tmp_path)
    info = get_git_info()
    assert info["branch"] == ""
    assert info["has_changes"] is False

def test_run_with_loading_success():
    result = run_with_loading(["echo", "test"])
    assert result.returncode == 0
```

### Integration Tests
```python
def test_flutter_command_execution():
    output = run_flutter_command(["--version"])
    assert "Flutter" in output

def test_git_integration():
    # Initialize git repo, make changes, check status
    pass
```

## Common Patterns

### Checking Prerequisites
```python
# Check if tool is installed
flutter_info = check_flutter_installed()
if not flutter_info["installed"]:
    console.print("[red]Flutter not installed[/]")
    return

# Check platform
if is_windows():
    # Use Chocolatey
    choco = check_chocolatey_installed()
else:
    # Use alternative package manager
    pass
```

### Executing Commands with Feedback
```python
# Silent execution
result = run_with_loading(
    cmd,
    status_message="Working...",
    clear_on_success=True
)

# Verbose execution
result = run_with_loading(
    cmd,
    status_message="Running command...",
    should_display_command=True,
    show_output_on_failure=True
)
```

### Displaying System Info
```python
platform_info = get_platform_info()
git_info = get_git_info()
path = get_current_path()

console.print(f"System: {platform_info['system']}")
console.print(f"Branch: {git_info['branch']}")
console.print(f"Path: {path}")
```

## Change History

### 2026-01-17 (v0.1.3)
- **BREAKING**: Removed `display_utils.py` (deprecated)
- **BREAKING**: Removed duplicate functions from `beautiful_display.py`
- **Added**: `get_git_info()` to `platform_utils.py`
- **Added**: `get_current_path()` to `platform_utils.py`
- **Added**: Platform check helpers: `is_windows()`, `is_macos()`, `is_linux()`
- Consolidated duplicate utility functions
- Updated documentation

### 2025-10-16 (v0.1.2)
- Added animated loading indicators
- Enhanced terminal_utils with better output handling
- Added beautiful_prompt with auto-completion

### 2025-06-15 (v0.1.0)
- Initial utility functions
- Basic terminal operations
- Platform detection

## Future Plans

See `.context/architecture.yaml` for FINAL architecture migration (v0.2.0+):
- Utils will be reorganized into layers:
  - `infrastructure/terminal/` - Terminal operations
  - `infrastructure/platform/` - Platform-specific code
  - `infrastructure/storage/` - Configuration management
  - `presentation/ui/` - Display utilities
- Enhanced error handling and logging
- Comprehensive test coverage
- Performance optimizations
