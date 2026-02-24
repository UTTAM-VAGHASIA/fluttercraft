# FlutterCraft — Project Context

> **This is the single source of truth for the project state.**
> Give this file to any AI agent to get full context without reading the codebase.
>
> Last Updated: 2026-02-23

---

## What Is FlutterCraft

A Python TUI (Terminal User Interface) tool for Flutter developers. It wraps Flutter CLI, FVM (Flutter Version Manager), project creation, git management, and AI CLI integration into a single unified terminal application.

- **Language:** Python 3.10+
- **TUI Framework:** Textual (migration from Rich + prompt_toolkit)
- **Package:** PyPI `fluttercraft`
- **License:** AGPL v3
- **Repo:** https://github.com/UTTAM-VAGHASIA/fluttercraft

---

## Current State

**Version:** 0.1.3 (published) / 0.2.0 (in development)
**Active Branch:** `feature/v0.2.0-tui`
**Current Phase:** Not started (Phase 1 next)
**Overall Progress:** 0%

### Branches

| Branch | State | Description |
|--------|-------|-------------|
| `main` | Stable v0.1.3 | Rich + prompt_toolkit CLI, Windows-only REPL |
| `feature/v0.1.3-signature-ui` | Paused | Phase 1 UI enhancements (fuzzy completion, history, timing) + Claude skills + TUI MVP plan |
| `feature/opencode-tui` | Abandoned | Tried Textual TUI, reverted. Has animations, settings, progress bars |
| `feature/v0.2.0-tui` | NEW | Complete TUI rewrite using Textual |

### What Exists (v0.1.3 on main)

Working:
- Typer CLI entry point (`fluttercraft start`)
- Interactive REPL with Rich + prompt_toolkit (Windows-only)
- Command registry system (`commands/core/` — Registry, Executor, Command base, models)
- FVM commands: install, uninstall, releases, list
- Flutter commands: upgrade (with flags)
- Slash commands: /quit, /clear, /help, /about, /theme
- 13 professional themes (7 dark, 6 light) with gradient ASCII art
- ThemeManager with persistence to `~/.fluttercraft/theme.json`
- ThemeDisplayService for all themed rendering
- Interactive theme selector (prompt_toolkit Application)

Dead code (to be removed in v0.2.0):
- `commands/command_handler.py` — legacy monolithic dispatcher
- `commands/theme/interactive_theme_selector.py` — duplicate
- `commands/theme/live_theme_selector.py` — Windows-only msvcrt
- `commands/theme/rich_theme_selector.py` — Windows-only msvcrt
- `utils/display_utils.py` — deprecated display functions

### What Exists (from feature branches, to be cherry-picked)

From `feature/v0.1.3-signature-ui`:
- `utils/fuzzy_matcher.py` — FuzzyMatcher class using rapidfuzz
- `utils/history_manager.py` — Persistent command history
- Platform utils: `get_git_info()`, `get_current_path()`, `is_windows/macos/linux()`

From `feature/opencode-tui`:
- `utils/animations/engine.py` + `effects.py` — AnimationEngine (slide, wipe, shake)
- `utils/progress.py` — Themed Rich progress bars
- `commands/settings/` — Settings panel + ConfigManager
- Command timing in CommandResult/Executor

---

## Target Architecture (v0.2.0)

Inspired by [Sidecar](https://github.com/marcus/sidecar) — plugin-based TUI with adapter pattern.

```
fluttercraft/
├── app.py                          # Main Textual App (FlutterCraftApp)
├── screens/
│   ├── dashboard.py                # Main dashboard (sidebar + content + output)
│   ├── project_wizard.py           # Project creation wizard
│   └── settings.py                 # Settings screen
├── widgets/
│   ├── header.py                   # Status bar
│   ├── footer.py                   # Keybinding hints
│   ├── command_input.py            # Input with autocomplete
│   ├── output_panel.py             # Scrollable output
│   ├── sidebar.py                  # Plugin tabs
│   ├── modal.py                    # Declarative modal builder
│   └── spinner.py                  # Loading indicators
├── plugins/
│   ├── base.py                     # Plugin interface + registry + lifecycle
│   ├── fvm_manager/                # FVM management
│   ├── flutter_commands/           # Flutter CLI runner
│   ├── project_creator/            # Project creation + templates
│   ├── git_control/                # Git management
│   ├── file_browser/               # File browser
│   ├── workspace/                  # Multi-project workspace
│   ├── cli_adapter/                # AI CLI integration
│   └── icon_generator/             # App icon setup
├── adapters/
│   ├── base.py                     # CLIAdapter interface
│   ├── detect.py                   # Auto-detect CLIs on PATH
│   ├── claude.py                   # Claude Code
│   ├── gemini.py                   # Gemini CLI
│   └── opencode.py                 # OpenCode
├── core/
│   ├── events.py                   # Event bus (typed pub/sub)
│   ├── config.py                   # ~/.fluttercraft/config.json
│   ├── state.py                    # ~/.fluttercraft/state.json
│   ├── keymap.py                   # Keybinding registry
│   └── platform.py                 # Platform detection
├── themes/
│   ├── theme.py                    # Theme dataclass
│   ├── manager.py                  # ThemeManager
│   ├── professional.py             # 13 built-in themes
│   └── styles.tcss                 # Textual CSS
├── commands/
│   └── core/                       # Registry, Executor, Command, models (reused)
└── main.py                         # typer entry → launches Textual app
```

### Key Patterns

1. **Plugin System**: Every feature panel is a Plugin (interface: `id`, `name`, `icon`, `init`, `start`, `stop`, `compose`, `update`, `commands`). Registry manages lifecycle with silent degradation.

2. **Adapter Pattern**: External CLIs (Claude, Gemini, OpenCode) are CLIAdapters (interface: `detect`, `start_session`, `send`, `stream_output`, `stop`). Auto-detected from PATH.

3. **Event Bus**: Typed pub/sub (`file_changed`, `git_changed`, `session_update`, `focus_changed`). Plugins communicate via events, never direct references.

4. **Plugin Context**: Shared bag injected at init: `work_dir`, `project_root`, `config`, `event_bus`, `adapters`, `keymap`, `state`.

5. **State Persistence**: Per-project state in `~/.fluttercraft/state.json` (active plugin, pane widths, file selections). Thread-safe via locks.

6. **Command Registry**: Reused from v0.1.x. `CommandRegistry` → `CommandExecutor` → `Command.execute()` → `CommandResult`.

7. **Declarative Modals**: Builder pattern with priority stack: `Modal("Title").section(...).buttons(...)`.

---

## Dependencies

```
textual>=0.85.0       # TUI framework
typer[all]            # CLI entry point
rich                  # Rendering (Textual uses internally)
rapidfuzz>=3.0.0      # Fuzzy matching
pyfiglet              # ASCII art
colorama              # Windows colors
watchdog>=3.0.0       # File watching (git plugin, workspace)
```

---

## Implementation Plan

10 phases, see `.specs/features/v0.2.0-tui/plan.md` for full details.

| Phase | Name | Key Deliverable |
|-------|------|-----------------|
| 1 | TUI Shell & Core | Working Textual app replacing prompt_toolkit REPL |
| 2 | Plugin Architecture | Modular plugin system, command palette, keybindings |
| 3 | FVM Manager | Full FVM management panel |
| 4 | Flutter Commands | All Flutter CLI commands in TUI |
| 5 | Git Control | Git status, diff, commit, push, branch management |
| 6 | Project Creator | Wizard with templates, state management, icons |
| 7 | File Browser | Tree view, preview, file operations |
| 8 | Workspace Manager | Multi-project switching, per-project state |
| 9 | CLI Adapters | Claude/Gemini/OpenCode integration, sessions |
| 10 | Polish & Release | Tests, docs, v0.2.0 release |

---

## Git Strategy

```
main (stable v0.1.3)
 └── feature/v0.2.0-tui
      ├── Push after each phase completion
      ├── Merge to main at v0.2.0 release
      └── Tag: v0.2.0
```

Commit convention: `<type>(<scope>): <description>`
Push after: each phase completion (for backup)
Merge to main: only at v0.2.0 release

---

## Testing Workflow

**Interactive testing — agent cannot access terminal.**

After every feature:
1. Agent writes automated tests in `tests/` + manual test steps
2. Agent presents both to the user
3. User runs `python -m pytest tests/<file>.py -v` and manual steps
4. User reports results back
5. If failures: agent debugs, user re-tests
6. If all pass: commit

Test structure mirrors source: `tests/core/`, `tests/plugins/`, `tests/widgets/`, `tests/adapters/`, `tests/themes/`

See `AGENTS.md` → "Test Structure" section for full mapping of steps to test files.

---

## Quick Reference

| What | Where |
|------|-------|
| Full plan | `.specs/features/v0.2.0-tui/plan.md` |
| Progress tracker | `.specs/features/v0.2.0-tui/progress.md` |
| Agent workflow | `AGENTS.md` |
| Architecture ref | `.context/architecture.md` |
| Sidecar reference | `sidecar-architecture-reference.md` |
| Package config | `setup.py` |
| Entry point | `fluttercraft/main.py` |
| Current commands | `fluttercraft/commands/` |
| Current themes | `fluttercraft/utils/themes/` |
