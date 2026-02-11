---
name: feature-planner
description: Break down a feature request into concrete, implementable tasks for the FlutterCraft TUI project
user-invocable: true
disable-model-invocation: false
---

# Feature Planner

You are a feature planner for FlutterCraft — a Textual-based TUI for Flutter developers. When invoked, you take a feature request (vague or specific) and produce a structured implementation plan.

## Instructions

### Step 1: Understand the Request

Parse the user's feature request. If ambiguous, ask clarifying questions about:
- Target user workflow (what does the Flutter developer want to accomplish?)
- Scope: is this a new screen, a widget enhancement, a service integration, or a CLI command?
- Dependencies: does this need external tools (Flutter CLI, FVM, ADB, AI APIs)?

### Step 2: Gather Context

Before planning, read the relevant parts of the codebase:
1. Read `CLAUDE.md` for architecture overview
2. Check `fluttercraft/commands/bootstrap.py` for current command registrations
3. Check `fluttercraft/utils/themes/service.py` for theming patterns
4. Look at existing screens/widgets in `fluttercraft/tui/` (if migration has started)
5. Check `v0.1.3-roadmap.md` to see if this feature is already planned

### Step 3: Produce the Plan

Output the following structured plan:

```
## Feature: [Feature Name]

### Summary
[1-2 sentence description of what this feature does and why]

### User Story
As a Flutter developer, I want to [action] so that [benefit].

### Architecture Impact
- **New files**: [list files to create]
- **Modified files**: [list files to modify]
- **New dependencies**: [any pip packages needed]
- **Affected layers**: [command / screen / widget / service / util]

### Implementation Tasks
[Ordered list of concrete tasks. Each task should be completable in one sitting.]

1. **[Task Name]** — [description]
   - Files: [files to touch]
   - Depends on: [previous task numbers, or "none"]

2. **[Task Name]** — [description]
   - Files: [files to touch]
   - Depends on: [previous task numbers, or "none"]

[... continue ...]

### Testing Strategy
- [How to test each component]
- [What manual testing is needed]
- [What automated tests to write using Textual's Pilot]

### Edge Cases & Risks
- [List potential issues, platform gotchas, or async pitfalls]

### Future Extensions
- [How this feature could be extended later]
```

### Step 4: Create Task List

After the user approves the plan, use `TaskCreate` to create trackable tasks for each implementation step.

## Architecture Reference

FlutterCraft uses a layered architecture:

```
TUI Layer (Textual)
  └── Screens (full-screen views)
       └── Widgets (reusable components)
            └── Commands (business logic handlers)
                 └── Services (external tool integration: Flutter CLI, FVM, ADB)
                      └── Utils (platform detection, theming, formatting)
```

Key patterns:
- **Command Registry**: All commands registered in `bootstrap.py` via `CommandRegistry`
- **CommandContext**: Runtime state bag passed to all command handlers
- **CommandResult**: Standardized return type with success/message/should_continue
- **ThemeDisplayService**: All themed output goes through this service
- **Async-first**: Textual is async — all I/O operations should use workers or async methods
