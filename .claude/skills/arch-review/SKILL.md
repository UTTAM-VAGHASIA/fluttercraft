---
name: arch-review
description: Review code changes against FlutterCraft's architectural patterns and TUI best practices
user-invocable: true
disable-model-invocation: false
---

# Architecture Reviewer

You review code changes for architectural consistency in the FlutterCraft TUI project. You enforce patterns, catch anti-patterns, and suggest improvements.

## Instructions

### Step 1: Identify What Changed

Read the files the user has modified or is proposing to modify. Use `git diff` if available, or read the specific files mentioned.

### Step 2: Review Against Checklist

Score each applicable category:

#### Command System Compliance
- [ ] New commands inherit from `Command` base class
- [ ] `CommandMetadata` is fully specified (name, help_text, category, aliases)
- [ ] `execute()` returns `CommandResult` — never raises to the caller
- [ ] Command is registered in `bootstrap.build_command_system()`
- [ ] Business logic is separated from display/rendering

#### Textual TUI Patterns
- [ ] Screens use `compose()` to declare widget tree (not imperative creation)
- [ ] State uses `reactive[]` attributes (not instance variables for dynamic data)
- [ ] Inter-widget communication uses `Message` classes (not direct method calls)
- [ ] I/O operations use `@work(thread=True)` workers (not blocking calls)
- [ ] CSS is in `DEFAULT_CSS` or external `.tcss` file (not inline Rich markup)
- [ ] Key bindings declared in `BINDINGS` class variable

#### Theme Consistency
- [ ] Colors reference theme tokens (not hardcoded hex/named colors)
- [ ] Output uses ThemeDisplayService methods (for Rich) or CSS variables (for Textual)
- [ ] New semantic colors are added to Theme dataclass if needed
- [ ] Gradient/accent colors come from theme, not constants

#### Async Safety
- [ ] No blocking calls in async methods (`subprocess.run` → worker)
- [ ] Workers are properly cancelled when screen is popped
- [ ] `await` is used correctly (not missing, not on sync calls)
- [ ] Error handling in workers doesn't silently swallow exceptions

#### Code Quality
- [ ] `from __future__ import annotations` at top of file
- [ ] Type hints on function signatures
- [ ] No circular imports (check import graph)
- [ ] Follows existing naming conventions (snake_case files, PascalCase classes)
- [ ] flake8 clean (max line length 88)

### Step 3: Produce Review

Output a structured review:

```
## Architecture Review

### Score: X/Y checks passed

### Passes
- [List things done correctly]

### Issues (must fix)
- [file:line] — [description of architectural violation]
  - **Fix**: [specific suggestion]

### Suggestions (nice to have)
- [Non-blocking improvements]

### Pattern Compliance
| Pattern | Status |
|---|---|
| Command System | pass/fail |
| Textual TUI | pass/fail |
| Theme Consistency | pass/fail |
| Async Safety | pass/fail |
| Code Quality | pass/fail |
```

## Anti-Patterns to Flag

| Anti-Pattern | Why It's Bad | Correct Pattern |
|---|---|---|
| `console.print()` in Textual widget | Bypasses Textual rendering | Use widget composition or `RichLog` |
| `subprocess.run()` without worker | Blocks the event loop | Use `@work(thread=True)` |
| Hardcoded `"[bold red]"` in TUI | Breaks theming | Use CSS classes |
| `self.query_one("#id").value = x` from outside widget | Breaks encapsulation | Post a message, let widget handle it |
| `time.sleep()` in async code | Blocks everything | Use `asyncio.sleep()` or `set_timer()` |
| Mutable default in `CommandMetadata` | Shared state bug | Use `tuple` not `list` for defaults |
| Import at module level causing circular dep | ImportError at startup | Use local imports or restructure |
