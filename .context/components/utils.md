---
component: Utilities
layer: Infrastructure
last_updated: 2026-01-24
maintainer: Core Team
---

# Utilities Component

## Purpose

Provides shared utility functions for terminal operations, platform detection, system utilities, and display helpers. These are low-level functions used across the application.

## Public API

### Terminal Utilities
```python
from fluttercraft.utils.terminal_utils import run_with_loading, run_with_progress

# Execute command with loading indicator
result = run_with_loading(
    ["flutter", "--version"],
    status_message="Checking Flutter version...",
    should_display_command=True,
    clear_on_success=True
)

# Execute command with progress bar
result = run_with_progress(
    ["curl", "..."],
    description="Downloading file...",
    transient=True
)
```

### Progress Indicators
```python
from fluttercraft.utils.progress import create_progress, create_download_progress

# Generic progress
progress = create_progress(console, transient=True)
with progress:
    task = progress.add_task("Working...", total=100)
    # ...

# Download progress
dl_progress = create_download_progress(console, transient=True)
with dl_progress:
    task = dl_progress.add_task("Downloading...", total=size)
    # ...
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
# ... (same as before)
```

### Animations
```python
from fluttercraft.utils.animations.engine import AnimationEngine
from fluttercraft.utils.animations import effects

# Run an animation
engine = AnimationEngine()
engine.slide_in(renderable, direction="left")
engine.wipe_in(text, vertical=True)
engine.shake(renderable)
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
├── progress.py             # Progress bar factories (NEW)
└── animations/             # Animation system
    ├── engine.py           # Animation driver
    └── effects.py          # Easing functions
```

## Dependencies

### Depends On:
- `rich` - Terminal formatting, Live display, Progress bars
- `subprocess` - Command execution
- `prompt_toolkit` - Interactive prompts
- `pygments` - Syntax highlighting

## Key Functions

### Terminal Utils

#### `run_with_progress(cmd, description, shell, transient)`
Executes a subprocess command while showing a sleek progress bar (indeterminate).

**Parameters:**
- `cmd` (list[str]|str): Command to run
- `description` (str): Text to show next to spinner
- `shell` (bool): Whether to use shell execution
- `transient` (bool): Hide bar after completion

**Returns:**
- `CompletedProcessLike`: Object with `returncode`, `stdout`, `stderr`

### Progress

#### `create_progress(console, transient)`
Creates a standard `rich.progress.Progress` instance with project-themed columns.

#### `create_download_progress(console, transient)`
Creates a `rich.progress.Progress` instance optimized for downloads (shows transfer speed, size).

## Change History

### 2026-01-24 (v0.1.3)
- **Added**: `progress.py` with themed factory functions
- **Added**: `run_with_progress` in `terminal_utils.py`
- **Updated**: `run_with_loading` improvements

### 2026-01-17 (v0.1.3)
- Refactored utilities and added platform helpers

### 2025-10-16 (v0.1.2)
- Added animated loading indicators