---
name: gather-context
description: Gather and summarize all relevant context for a task across the FlutterCraft codebase
user-invocable: true
disable-model-invocation: true
---

# Context Gatherer

You gather and organize all relevant codebase context needed before starting work on a task. This prevents wasted effort from incomplete understanding.

## Instructions

### Step 1: Understand the Task

Parse what the user wants to accomplish. Identify:
- Which layer(s) are involved (TUI / commands / services / utils / config)
- Which external tools are involved (Flutter CLI, FVM, ADB, AI APIs)
- Whether this is new code, a modification, a migration, or a bug fix

### Step 2: Systematic Context Gathering

Run through this checklist and read the relevant files:

#### Always Read
- [ ] `CLAUDE.md` — architecture overview and conventions
- [ ] `v0.1.3-roadmap.md` — current roadmap and priorities

#### If Touching Commands
- [ ] `fluttercraft/commands/core/base.py` — Command ABC
- [ ] `fluttercraft/commands/core/models.py` — CommandContext, CommandResult, CommandMetadata
- [ ] `fluttercraft/commands/core/executor.py` — dispatch logic
- [ ] `fluttercraft/commands/core/registry.py` — registration system
- [ ] `fluttercraft/commands/bootstrap.py` — all registered commands
- [ ] The specific command file being modified

#### If Touching TUI
- [ ] `fluttercraft/tui/app.py` — main App class (if exists)
- [ ] `fluttercraft/tui/theme.py` — theme integration (if exists)
- [ ] The specific screen/widget being modified
- [ ] Parent and sibling widgets that interact with the target

#### If Touching Theming
- [ ] `fluttercraft/utils/themes/theme.py` — Theme dataclass
- [ ] `fluttercraft/utils/themes/service.py` — ThemeDisplayService
- [ ] `fluttercraft/utils/themes/theme_manager.py` — persistence
- [ ] `fluttercraft/utils/themes/gradient.py` — gradient rendering
- [ ] `fluttercraft/utils/themes/professional_themes.py` — theme definitions

#### If Touching External Tool Integration
- [ ] `fluttercraft/commands/flutter_commands.py` — Flutter CLI wrappers
- [ ] `fluttercraft/commands/fvm_commands.py` — FVM CLI wrappers (if exists)
- [ ] `fluttercraft/utils/platform_utils.py` — platform detection
- [ ] `fluttercraft/utils/system_utils.py` — system utilities

#### If Touching UI/Display
- [ ] `fluttercraft/utils/beautiful_prompt.py` — prompt and auto-completion
- [ ] `fluttercraft/utils/themed_display.py` — legacy display utilities
- [ ] `fluttercraft/utils/beautiful_display.py` — display helpers
- [ ] `fluttercraft/utils/display_utils.py` — general display utilities

### Step 3: Produce Context Summary

Output a structured summary:

```
## Context for: [Task Description]

### Relevant Files (read)
[List of files read with 1-line summary of what's relevant in each]

### Architecture Notes
[Key patterns, constraints, and conventions that apply to this task]

### Dependencies
[Other code that depends on or is depended upon by the code being changed]

### Gotchas
[Anything tricky, non-obvious, or easy to break found during context gathering]

### Ready to Proceed
[Confirmation that context is sufficient, or list of questions that remain]
```

### Step 4: Save Important Findings

If you discover something non-obvious that would be useful for future tasks:
- Update CLAUDE.md if it's an architectural pattern
- Update memory files if it's a debugging insight or project convention
