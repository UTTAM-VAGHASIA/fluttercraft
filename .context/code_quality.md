# Code Quality Reference

> This file defines what to check, what to ignore, and what errors matter.
> Agent reads this before running quality checks. Configured in `.flake8`.

---

## Quality Gate (Run Before Every Commit)

Run these in order. All must pass before providing git commit commands.

```bash
# 1. Format (auto-fixes style, run first)
black fluttercraft/ --line-length 88

# 2. Lint (after formatting so black-related noise is gone)
flake8 fluttercraft/

# 3. Lint tests/ (only if tests/ directory exists)
flake8 tests/

# 4. Syntax check (quick sanity on changed files)
python -m py_compile fluttercraft/<changed_file>.py
```

---

## Error Categories

### MUST FIX — These are real bugs or will break at runtime

| Code | Meaning | Example |
|------|---------|---------|
| F821 | Undefined name | `foo()` where `foo` is never imported/defined |
| F811 | Redefined unused name | Import overwritten before use |
| F841 | Local variable assigned but never used | `x = compute()` then never use `x` |
| F541 | f-string without placeholders | `f"hello"` should be `"hello"` |
| F401 | Imported but unused | `import os` never used (except `__init__.py`) |
| W605 | Invalid escape sequence | `"\d"` should be `r"\d"` or `"\\d"` |
| E711 | Comparison to None using `==` | `if x == None` → use `if x is None` |
| E712 | Comparison to True/False using `==` | `if x == True` → use `if x` |
| E721 | Type comparison using `==` | `type(x) == int` → use `isinstance(x, int)` |

### SUPPRESSED — Handled by Black or are noise

| Code | Reason Ignored |
|------|---------------|
| E203 | Black-compatible spacing |
| E501 | Black enforces line length |
| E302 | Black handles blank lines |
| W291/W292/W293 | Black handles whitespace |
| W503 | Black default line-break style |
| `__init__.py` F401 | Re-exports are intentional |

---

## Common Mistakes to Manually Check

These are not always caught by flake8 but cause runtime failures:

### Import Order
```python
# CORRECT order in every file
from __future__ import annotations   # always first
import os                             # stdlib
import sys

from textual.app import App           # third party
from rich.console import Console

from fluttercraft.core.events import EventBus   # local
```

### Missing `from __future__ import annotations`
Every new `.py` file must start with this. Flake8 won't catch the absence.

### Dataclass missing `slots=True`
```python
# WRONG
@dataclass
class Config:
    ...

# CORRECT
@dataclass(slots=True)
class Config:
    ...
```

### Bare except
```python
# WRONG — hides all errors
try:
    ...
except:
    pass

# CORRECT
try:
    ...
except ValueError as e:
    logger.error(f"Config error: {e}")
```

### Mutable default arguments
```python
# WRONG
def add_plugin(plugins=[]):
    ...

# CORRECT
def add_plugin(plugins=None):
    if plugins is None:
        plugins = []
```

---

## Textual-Specific Checks

These are specific to Textual TUI code and won't be caught by flake8:

1. **`compose()` must be a generator** — use `yield` not `return`
2. **`on_*` message handlers must be `async def`**
3. **Never block the event loop** — use `asyncio.create_subprocess_exec` not `subprocess.run` in async context
4. **`run_worker()` for subprocess calls** — keeps UI responsive
5. **CSS class names must match `.tcss` definitions** exactly (case-sensitive)

---

## Pre-Commit Checklist

Before giving the user a git commit command, verify:

- [ ] `black` ran with no changes (file is formatted)
- [ ] `flake8` output is empty (no errors from the MUST FIX list above)
- [ ] `python -m py_compile` succeeds on all changed files
- [ ] No `print()` statements left (use `self.log()` in Textual or logger)
- [ ] No hardcoded paths (use `Path.home()` or config values)
- [ ] No `TODO:` or `FIXME:` left in code added in this commit
- [ ] `from __future__ import annotations` present in all new files
- [ ] Test file written for the feature (if required by plan)

---

## Running the Full Suite

```bash
# All tests
python -m pytest tests/ -v

# Only fast unit tests (skip manual-tagged)
python -m pytest tests/ -v -m "not manual"

# With coverage
python -m pytest tests/ --cov=fluttercraft --cov-report=term-missing

# Single file
python -m pytest tests/core/test_events.py -v
```
