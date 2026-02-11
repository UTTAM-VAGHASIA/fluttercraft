---
name: tui-scaffold
description: Scaffold new Textual screens, widgets, and components following FlutterCraft patterns
user-invocable: true
disable-model-invocation: false
---

# TUI Component Scaffolder

You create new Textual screens, widgets, and components for FlutterCraft. You follow the project's architecture patterns and produce production-ready code.

## Instructions

### Step 1: Determine Component Type

Ask or infer what the user needs:
- **Screen**: A full-screen view (e.g., Dashboard, FVM Manager, Settings)
- **Widget**: A reusable component (e.g., StatusBar, CommandPalette, LogViewer)
- **Modal**: A dialog/popup (e.g., Confirmation, Version Picker)
- **Service Widget**: A widget that wraps an external service (e.g., Flutter Doctor output)

### Step 2: Gather Context

1. Read `CLAUDE.md` for architecture patterns
2. Check existing Textual components in `fluttercraft/tui/` for naming and style conventions
3. Read `fluttercraft/utils/themes/theme.py` to understand the theme system
4. Check `fluttercraft/utils/themes/service.py` for ThemeDisplayService patterns

### Step 3: Generate Component

Follow these patterns based on component type:

#### Screen Template
```python
"""[Screen Name] screen for FlutterCraft TUI."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical

from fluttercraft.tui.theme import get_active_theme


class [ScreenName]Screen(Screen):
    """[Description of what this screen does]."""

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        # Add screen-specific bindings
    ]

    CSS = """
    [ScreenName]Screen {
        /* Screen-level styles using theme tokens */
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-content"):
            # Compose child widgets here
            yield Static("Content goes here")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize screen state after mounting."""
        pass

    # -- Actions --
    def action_pop_screen(self) -> None:
        self.app.pop_screen()
```

#### Widget Template
```python
"""[Widget Name] widget for FlutterCraft TUI."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message


class [WidgetName](Widget):
    """[Description]."""

    DEFAULT_CSS = """
    [WidgetName] {
        height: auto;
        /* Widget styles */
    }
    """

    # Reactive attributes for dynamic state
    value: reactive[str] = reactive("")

    class Changed(Message):
        """Emitted when value changes."""
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def compose(self) -> ComposeResult:
        # Compose child widgets
        pass

    def watch_value(self, new_value: str) -> None:
        """React to value changes."""
        self.post_message(self.Changed(new_value))
```

### Step 4: File Placement

Place generated files according to this structure:
```
fluttercraft/tui/
├── app.py              # Main Textual App class
├── theme.py            # Theme integration for Textual CSS
├── screens/
│   ├── __init__.py
│   ├── dashboard.py    # Main dashboard screen
│   ├── fvm_manager.py  # FVM management screen
│   └── [new_screen].py
├── widgets/
│   ├── __init__.py
│   ├── status_bar.py
│   ├── command_palette.py
│   └── [new_widget].py
└── modals/
    ├── __init__.py
    └── [new_modal].py
```

### Step 5: Integration

After creating the component:
1. Export it from the appropriate `__init__.py`
2. If it's a screen, add navigation to it from the app or parent screen
3. If it uses external commands, wire it through the existing command system
4. Add Textual CSS styles using theme tokens (not hardcoded colors)

## Key Rules

- **Always use Textual CSS** for styling, never inline Rich markup in Textual widgets
- **Always use reactive attributes** for dynamic state, never mutate widget internals directly
- **Always use Messages** for inter-widget communication, never direct method calls across widget boundaries
- **Use workers** (`@work`) for any I/O-bound operations (subprocess calls, file reads)
- **Theme tokens**: Map FlutterCraft theme colors to Textual CSS variables so themes work consistently
- **Type hints**: Use `from __future__ import annotations` and full type hints
