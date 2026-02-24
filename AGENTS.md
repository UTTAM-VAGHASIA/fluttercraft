# FlutterCraft — Agent Workflow Guide

> Rules and workflow for any AI agent (Claude, Gemini, Cursor, etc.) working on this project.

---

## Quick Start

1. Read `.context/PROJECT_CONTEXT.md` first — it has the full project state
2. Read `.specs/features/v0.2.0-tui/plan.md` for the implementation plan
3. Check `.specs/features/v0.2.0-tui/progress.md` for what's done and what's next
4. Follow the workflow below

---

## Git Operations Policy

> **CRITICAL — Read before doing anything.**

### Rule 1: Agent NEVER runs git commands

The agent (Claude, Gemini, etc.) **MUST NOT** execute any `git` command under any circumstance.

- Wrong branch + wrong command = lost work, destroyed history, unrecoverable state
- All git operations are provided as **copy-paste command blocks** for the user to run manually
- The user confirms each git operation before running it

### Rule 2: Format for providing git commands

Whenever a git operation is needed, the agent outputs it in this format:

```
## Git Command Required

Run this command:

    git <command>

Expected result: <what the user should see after running it>
```

### Rule 3: Agent waits for confirmation

After providing a git command, the agent **stops and waits** for the user to confirm the command ran successfully before proceeding.

### Rule 4: State branch only when it matters

The agent states the required branch **only at these specific points**:

| When | Why |
|------|-----|
| Initial branch setup | One-time switch from `main` → `feature/v0.2.0-tui` |
| Phase-end push | Verify correct branch before pushing to remote |
| Recovery scenario | Explicit branch repair commands |

**NOT required at:** every commit — there is zero branch switching during normal development. Once you are on `feature/v0.2.0-tui`, you stay there for the entire v0.2.0 build.

Before any push command, always provide this branch check first:
```bash
git branch
# Expected: * feature/v0.2.0-tui
```

---

## Git Branch Strategy

### Branch Layout

```
origin/main                          ← stable, never touch directly
origin/feature/v0.1.3-signature-ui   ← previous feature branch (reference only)
feature/v0.2.0-tui                   ← ALL v0.2.0 work happens here
```

### Initial Setup (do this ONCE before any implementation)

**You should be on:** `main`

```bash
# Step 1: Create and switch to the working branch
git checkout -b feature/v0.2.0-tui

# Step 2: Verify you are on the correct branch
git branch
# Expected: * feature/v0.2.0-tui
```

> Untracked files (.context/, .specs/, AGENTS.md, CLAUDE.md, sidecar-architecture-reference.md)
> carry over automatically — nothing is lost.

### Per-Phase Push (end of each phase)

The plan marks push points as `-> PUSH`. When you reach one:

**You should be on:** `feature/v0.2.0-tui`

```bash
# First push (Phase 1 end — sets upstream)
git push -u origin feature/v0.2.0-tui

# All subsequent phase pushes
git push
```

### Checking Current Branch (before any git work)

```bash
git branch
git status
```

### Recovering if on the Wrong Branch

**Do not run any recovery commands on your own. Describe the situation to the agent and ask for the exact commands for your specific case.**

General steps (agent will tailor to your exact state):
```
1. Run: git log --oneline -5
2. Run: git status
3. Share output with agent → agent provides exact recovery commands
```

> Recovery is case-specific — the wrong command here can permanently lose commits.

---

## Mandatory Workflow

Every implementation task MUST follow these steps in order:

### Step 1: Understand Context

```
READ .context/PROJECT_CONTEXT.md
READ .specs/features/v0.2.0-tui/progress.md
```

- Know what phase we're in
- Know what step is next
- Know what's already built

### Step 2: Read Before Writing

- NEVER modify code you haven't read
- Read the existing file before editing
- Understand the patterns already in use
- Check imports and dependencies

### Step 3: Implement

- Follow the architecture in `.context/PROJECT_CONTEXT.md`
- Match existing code style (see Code Style section below)
- One feature per commit
- Keep changes focused — don't refactor unrelated code

### Step 4: Write Test Cases

**Testing is always interactive. The agent writes tests and provides commands — the user runs them.**

After implementing each feature, the agent MUST:
1. Write test cases in `tests/` matching the feature (see Test Structure below)
2. Provide the user with test commands to run (automated + manual)
3. Wait for the user to run tests and report results
4. Debug any failures, provide fixes
5. User re-tests after each fix

**CRITICAL — Git command gate:**
The agent MUST NOT provide any `git add` / `git commit` command until the user explicitly says **"tests complete"** or **"all tests pass"**. No exceptions.

**Test case format — provide the user with:**
```
## Test: <feature name>

### Automated Tests
Run: `python -m pytest tests/<test_file>.py -v`

### Manual Verification
1. Run: `<command>`
   Expected: <what should happen>
2. Run: `<command>`
   Expected: <what should happen>

### Edge Cases
1. <edge case scenario> → Expected: <behavior>
```

**The flow is:**
```
Agent implements feature
  → Agent writes test file
  → Agent presents test commands to user
  → User runs tests, reports results
  → If FAIL: Agent debugs + fixes → User re-tests
  → If FAIL again: Repeat debug cycle
  → User says "tests complete" / "all pass"
  → ONLY NOW: Agent provides git commit commands
```

### Step 5: Code Quality

**Full reference:** `.context/code_quality.md` — lists every error code, what to fix vs ignore, and Textual-specific checks.

```bash
# 1. Format (always run first — fixes style before linting)
black fluttercraft/ --line-length 88

# 2. Format tests/ (only if tests/ directory exists)
black tests/ --line-length 88

# 3. Lint (config in .flake8 — suppresses noise, keeps real errors)
flake8 fluttercraft/

# 4. Lint tests/ (only if tests/ exists)
flake8 tests/

# 5. Syntax check changed files
python -m py_compile fluttercraft/<modified_file>.py
```

**What flake8 will catch (must fix before commit):** F821 undefined names, F841 unused variables, F401 unused imports, F541 empty f-strings, W605 invalid escape sequences — see `.context/code_quality.md` for full list.

**What flake8 will NOT report (suppressed as noise):** E203, E501, E302, W291/W292/W293, W503 — all handled by Black.

### Step 6: Commit

**Only provide these commands after the user says "tests complete".**
**The agent MUST NOT run these commands — provide them for the user to run.**

```
## Git Command Required

Run these commands:

    git status
    (verify only the intended files are shown — no accidental extras)

    git add <specific files only — never git add .>
    git commit -m "<type>(<scope>): <description>"

Expected result: commit hash printed, no errors.
```

**Never use `git add .` or `git add -A`** — always add specific files by name to avoid committing unintended files.

Commit types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`
Scopes: `tui`, `core`, `plugins`, `fvm`, `flutter`, `git`, `creator`, `browser`, `workspace`, `adapters`

### Step 7: Update Progress

After completing a step, update `.specs/features/v0.2.0-tui/progress.md`:
- Check off the completed step `[x]`
- Mark test status (PASS/FAIL) in the Test Log
- Add commit to the Commit Log table
- Update phase status if all steps done

### Step 8: Update Context

After completing a phase or making architectural changes, update `.context/PROJECT_CONTEXT.md`:
- Update "Current State" section
- Update "What Exists" section
- Add any new modules to the Module Map

---

## Code Style

### Python

- Python >= 3.10
- Use `from __future__ import annotations` in all new files
- Dataclasses with `@dataclass(slots=True)` for all data objects
- Type hints on all function signatures
- No bare `except:` — always catch specific exceptions
- f-strings over `.format()` or `%`

### Naming

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_prefixed`

### Imports

```python
# Standard library
from __future__ import annotations
import os
import sys

# Third party
from textual.app import App
from rich.console import Console

# Local
from fluttercraft.core.events import EventBus
from fluttercraft.plugins.base import Plugin
```

### Patterns

1. **Plugin interface**: All features are plugins implementing `Plugin` base class
2. **Event bus**: Plugins communicate via events, never direct references
3. **Command pattern**: Commands are `Command` subclasses in the registry
4. **Context injection**: `PluginContext` is passed to all plugins at init
5. **Silent degradation**: Plugins that fail don't crash the app
6. **State persistence**: User preferences saved to `~/.fluttercraft/state.json`
7. **Config management**: App settings in `~/.fluttercraft/config.json`

---

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures (app instance, mock plugins, etc.)
├── core/
│   ├── test_events.py             # Event bus tests
│   ├── test_config.py             # Config manager tests
│   ├── test_state.py              # State persistence tests
│   └── test_keymap.py             # Keybinding registry tests
├── plugins/
│   ├── test_base.py               # Plugin interface + registry tests
│   ├── test_fvm_manager.py        # FVM plugin tests
│   ├── test_flutter_commands.py   # Flutter commands tests
│   ├── test_git_control.py        # Git plugin tests
│   ├── test_file_browser.py       # File browser tests
│   ├── test_workspace.py          # Workspace manager tests
│   └── test_project_creator.py    # Project creator tests
├── widgets/
│   ├── test_header.py             # Header widget tests
│   ├── test_sidebar.py            # Sidebar widget tests
│   ├── test_command_input.py      # Command input tests
│   ├── test_output_panel.py       # Output panel tests
│   └── test_modal.py              # Modal system tests
├── adapters/
│   ├── test_detect.py             # Adapter detection tests
│   ├── test_claude.py             # Claude adapter tests
│   ├── test_gemini.py             # Gemini adapter tests
│   └── test_opencode.py           # OpenCode adapter tests
└── themes/
    ├── test_theme.py              # Theme dataclass tests
    └── test_manager.py            # ThemeManager tests
```

### Test Categories

1. **Unit Tests** — Test individual functions/classes in isolation
   - Pure logic (config parsing, event dispatch, theme resolution)
   - Mock external dependencies (subprocess, filesystem, network)

2. **Widget Tests** — Test Textual widgets using `textual.testing`
   - Widget rendering, key handling, mouse events
   - Use `async with app.run_test()` pattern

3. **Integration Tests** — Test component interactions
   - Plugin → EventBus → Plugin communication
   - Command input → Executor → Output panel flow

4. **Manual Tests** — User-verified (agent provides steps)
   - Visual rendering correctness
   - Real subprocess execution (flutter, fvm, git)
   - Cross-platform behavior

### Test Naming Convention

```python
# test_<module>.py
def test_<function>_<scenario>():
    """<What it tests>."""

# Examples:
def test_event_bus_subscribe_receives_published_events():
def test_config_manager_dot_notation_nested_access():
def test_plugin_registry_silent_degradation_on_init_failure():
```

### When to Write Tests

| After implementing... | Write tests in... |
|---|---|
| Step 1.1 (App skeleton) | `tests/test_app.py` + manual: app launches |
| Step 1.2 (Event bus) | `tests/core/test_events.py` |
| Step 1.3 (Config) | `tests/core/test_config.py` |
| Step 1.4 (State) | `tests/core/test_state.py` |
| Step 1.6-1.10 (Widgets) | `tests/widgets/test_*.py` + manual: visual check |
| Step 1.13 (Themes) | `tests/themes/test_*.py` + manual: theme switching |
| Step 2.1-2.3 (Plugins) | `tests/plugins/test_base.py` |
| Step 2.4 (Modals) | `tests/widgets/test_modal.py` + manual: modal display |
| Step 2.5 (Palette) | manual: Ctrl+P opens, fuzzy search works |
| Step 2.6 (Keybindings) | `tests/core/test_keymap.py` |
| Step 3.x (FVM) | `tests/plugins/test_fvm_manager.py` + manual: real FVM commands |
| Step 4.x (Flutter) | `tests/plugins/test_flutter_commands.py` + manual: real Flutter commands |
| Step 5.x (Git) | `tests/plugins/test_git_control.py` + manual: real git operations |
| Step 6.x (Creator) | `tests/plugins/test_project_creator.py` + manual: project creation |
| Step 7.x (Browser) | `tests/plugins/test_file_browser.py` + manual: file navigation |
| Step 8.x (Workspace) | `tests/plugins/test_workspace.py` + manual: project switching |
| Step 9.x (Adapters) | `tests/adapters/test_*.py` + manual: CLI interaction |

---

## DO NOT

- Do NOT skip reading existing code before modifying
- Do NOT create files outside the architecture defined in the plan
- Do NOT add dependencies without documenting in setup.py AND context
- Do NOT run any git command — only provide them for the user to run
- Do NOT push to remote unless explicitly asked
- Do NOT modify `main` branch directly — work on `feature/v0.2.0-tui`
- Do NOT assume the user is on the correct branch — always state required branch before giving git commands
- Do NOT chain git commands into one-liners that obscure what they do — give them one at a time
- Do NOT skip updating progress.md after completing steps
- Do NOT add docstrings/comments to code you didn't write or change
- Do NOT over-engineer — minimum complexity for the current step
- Do NOT add error handling for impossible scenarios
- Do NOT create abstractions for one-time operations

---

## File Map (Key Files)

```
.context/PROJECT_CONTEXT.md              <- START HERE: full project state
.context/architecture.md                 <- Architecture reference
.context/code_quality.md                 <- Linting rules, error categories, pre-commit checklist
.specs/features/v0.2.0-tui/
  plan.md                                <- Implementation plan (10 phases)
  progress.md                            <- What's done, what's next
AGENTS.md                                <- This file (workflow rules)
CLAUDE.md                                <- Claude Code specific config
sidecar-architecture-reference.md        <- Sidecar TUI reference (patterns to adopt)
setup.py                                 <- Dependencies and package config
.flake8                                  <- Linting config (source of truth for flake8)
fluttercraft/
  app.py                                 <- Main Textual App
  main.py                                <- Entry point (typer)
  core/                                  <- Infrastructure (events, config, state, keymap)
  plugins/                               <- All feature plugins
  widgets/                               <- Reusable TUI components
  screens/                               <- Textual screens
  themes/                                <- Theme system
  adapters/                              <- CLI adapters
  commands/                              <- Command registry (from v0.1.x)
```

### Sidecar Reference Usage

`sidecar-architecture-reference.md` documents the Go/Bubble Tea TUI that FlutterCraft is inspired by. When implementing any of these systems, check the sidecar reference first for patterns:

| FlutterCraft Component | Sidecar Equivalent to Reference |
|---|---|
| `core/events.py` | Section 3.4 — Event System |
| `plugins/base.py` (Plugin ABC) | Section 3.2 — Plugin Interface |
| `plugins/base.py` (Registry) | Section 3.2 — Plugin Registry (panic recovery, silent degradation) |
| `core/state.py` | Section 5 — State Management |
| `core/config.py` | Section 4 — Configuration System |
| `widgets/modal.py` | Section 7 — Modal System |
| `core/keymap.py` | Section 8 — Key Binding System |
| `adapters/base.py` | Section 3.3 — Adapter Interface |
| Epoch invalidation (project switching) | Section 3.5 — Epoch-based Staleness |
