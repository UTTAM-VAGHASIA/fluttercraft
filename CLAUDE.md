# FlutterCraft — Claude Code Config

## Project

FlutterCraft is a Python TUI for Flutter development. Currently migrating from Rich + prompt_toolkit to Textual.

## Context Files

**Read these first (in order):**
1. `.context/PROJECT_CONTEXT.md` — Full project state, what exists, what's planned
2. `.specs/features/v0.2.0-tui/progress.md` — What's done, what's next
3. `AGENTS.md` — Workflow rules

## Commands

```bash
# Run the app
python -m fluttercraft start

# Install in dev mode
pip install -e .

# Format
black fluttercraft/ --line-length 88

# Lint
flake8 fluttercraft/ --max-line-length 88 --extend-ignore E203,W503

# Syntax check single file
python -m py_compile fluttercraft/<file>.py

# Test imports
python -c "from fluttercraft.app import FlutterCraftApp"
```

## Architecture

- **Entry:** `fluttercraft/main.py` (typer) → `fluttercraft/app.py` (Textual App)
- **Plugins:** `fluttercraft/plugins/` — each feature is a plugin
- **Core:** `fluttercraft/core/` — events, config, state, keymap
- **Widgets:** `fluttercraft/widgets/` — reusable TUI components
- **Themes:** `fluttercraft/themes/` — 13 built-in themes
- **Commands:** `fluttercraft/commands/core/` — registry + executor (from v0.1.x)
- **Adapters:** `fluttercraft/adapters/` — CLI integrations (Claude, Gemini, OpenCode)

## Conventions

- `@dataclass(slots=True)` for all data classes
- `from __future__ import annotations` in all files
- Plugins implement `Plugin` ABC from `plugins/base.py`
- Adapters implement `CLIAdapter` ABC from `adapters/base.py`
- Events go through `EventBus` — plugins never import each other
- Silent degradation — plugin failures don't crash the app
- Commits: `<type>(<scope>): <description>`

## Branch

Work on `feature/v0.2.0-tui`. Do NOT push unless asked. Do NOT touch `main`.
