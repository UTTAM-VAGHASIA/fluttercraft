---
name: tui-migrate
description: Guide and execute migration of existing Rich CLI code to Textual TUI components
user-invocable: true
disable-model-invocation: false
---

# Rich-to-Textual Migration Guide

You help migrate FlutterCraft's existing Rich-based CLI code into Textual TUI components. This is an incremental migration — not a rewrite.

## Instructions

### Step 1: Identify Migration Target

Ask or infer what the user wants to migrate:
- A specific command (e.g., `fvm releases`)
- A UI component (e.g., welcome header, help display)
- A service (e.g., ThemeDisplayService)
- The entire REPL loop (`start.py`)

### Step 2: Analyze Current Implementation

Read the current code and identify:
1. **Rich renderables used**: Tables, Panels, Text, Spinners, Live displays
2. **Console.print() calls**: These become widget renders in Textual
3. **Subprocess calls**: These need workers in Textual (async)
4. **Input handling**: prompt_toolkit code → Textual Input/CommandPalette widgets
5. **State management**: What data flows through CommandContext

### Step 3: Create Migration Map

For each piece of existing code, map it to Textual equivalents:

| Rich Pattern | Textual Equivalent |
|---|---|
| `console.print(Text(...))` | `Static` widget or `RichLog` |
| `console.print(Table(...))` | `DataTable` widget |
| `console.print(Panel(...))` | Container with CSS border |
| `Live(Spinner(...))` | `LoadingIndicator` or custom widget with `set_interval` |
| `prompt_toolkit.prompt()` | `Input` widget or `CommandPalette` |
| `InMemoryHistory` | App-level state or `Input` history |
| `subprocess.run(...)` | `@work(thread=True)` decorated method |
| `os.system("cls")` | `screen.clear()` or push new screen |
| Direct color strings `"[bold red]"` | Textual CSS classes |
| `ThemeDisplayService.print_*` | Widget with themed CSS class |

### Step 4: Execute Migration

When migrating, follow these rules:

1. **Don't break the existing CLI**. The Rich CLI should continue to work during migration. Create the TUI as a parallel entry point.
2. **Extract business logic from display code**. Commands should return data, not print it. The TUI layer renders data.
3. **Keep the command system**. `CommandRegistry`, `CommandExecutor`, `Command` base class — these stay. They just get called from Textual widgets instead of the REPL loop.
4. **Reuse ThemeDisplayService concepts**. Map `Theme` objects to Textual CSS variables.
5. **Async everything**. Wrap all subprocess/IO calls in workers.

### Step 5: Migration Order

Recommended migration order (least to most complex):

```
Phase 1: Foundation
  ├── Create fluttercraft/tui/app.py (main Textual App)
  ├── Create fluttercraft/tui/theme.py (Theme → CSS variable bridge)
  └── Add `fluttercraft tui` entry point alongside `fluttercraft start`

Phase 2: Static Screens
  ├── Welcome/Dashboard screen (replaces ASCII art + header)
  ├── Help screen (replaces /help output)
  └── About screen (replaces /about output)

Phase 3: Interactive Widgets
  ├── Command input bar (replaces prompt_toolkit prompt)
  ├── Command palette with fuzzy search
  └── Status bar (platform, Flutter, FVM info)

Phase 4: Command Screens
  ├── FVM Manager screen (releases, install, list)
  ├── Flutter Upgrade screen (with live progress)
  └── Theme selector screen

Phase 5: Advanced Features
  ├── Log viewer widget (real-time subprocess output)
  ├── Split-pane layouts
  └── Emulator integration (screenshots via textual-image)
```

## Dual Entry Point Strategy

During migration, maintain both entry points:

```python
# main.py
@app.command()
def start():
    """Start the Rich CLI (legacy)."""
    start_command()

@app.command()
def tui():
    """Start the Textual TUI (new)."""
    from fluttercraft.tui.app import FlutterCraftApp
    app = FlutterCraftApp()
    app.run()
```

This lets users try the TUI without losing the working CLI.
