---
name: debug-tui
description: Debug Textual TUI issues, rendering problems, event handling bugs, and async errors
user-invocable: true
disable-model-invocation: false
---

# TUI Debugger

You diagnose and fix issues in FlutterCraft's Textual TUI application. You understand Textual's internals, async patterns, CSS system, and common pitfalls.

## Instructions

### Step 1: Classify the Problem

Determine the issue category:
- **Rendering**: Widget not showing, wrong layout, CSS not applying, theme broken
- **Events**: Key bindings not working, messages not received, actions not triggering
- **Async**: Worker errors, blocking the event loop, race conditions, deadlocks
- **State**: Reactive attributes not updating, stale data, context not propagating
- **Subprocess**: Flutter CLI/FVM commands failing, output not captured, hangs
- **Platform**: Windows-specific issues, terminal compatibility, encoding errors

### Step 2: Gather Diagnostic Info

For each category, gather specific information:

#### Rendering Issues
1. Read the widget's `compose()` method and CSS
2. Check CSS specificity — Textual CSS follows a specificity model similar to web CSS
3. Check if `DEFAULT_CSS` vs external CSS file is conflicting
4. Look for `display: none` or `visibility: hidden` accidentally set
5. Verify the widget is actually mounted (check `on_mount`)

#### Event Issues
1. Read the BINDINGS list — check for conflicts with parent screen/app bindings
2. Check message bubble path — messages bubble from child → parent
3. Verify `@on(WidgetType.EventName)` decorator syntax
4. Check if `prevent_default()` is being called somewhere upstream

#### Async Issues
1. Check for `await` on synchronous calls (or missing `await` on async ones)
2. Look for `@work(thread=True)` on methods that call subprocess
3. Check if workers are being cancelled properly on screen pop
4. Look for accidental blocking calls in the main async loop

#### State Issues
1. Verify reactive attributes are declared at class level with `reactive[Type]`
2. Check `watch_*` methods match the reactive attribute name
3. Ensure `mutate_reactive` is used for mutable types (list, dict)
4. Check if `compose()` is using stale initial values

### Step 3: Debug Using Textual Tools

Recommend and use these Textual debugging approaches:

```bash
# Start the Textual debug console in one terminal
textual console

# Run the app with dev mode in another terminal
textual run --dev fluttercraft.tui.app:FlutterCraftApp
```

Inside the app code, use:
```python
# Log to the Textual debug console
self.log("Debug message:", some_variable)
self.log.info("Info level message")
self.log.warning("Warning message")
self.log.error("Error message")

# Inspect DOM tree
self.log(self.app.tree)

# Check CSS applied to a widget
self.log(widget.styles)
self.log(widget.css_tree)
```

### Step 4: Apply Fix

When fixing:
1. **Minimal change** — fix the root cause, don't refactor
2. **Add logging** — add `self.log()` calls at the failure point for future debugging
3. **Test the fix** — suggest a Pilot test that reproduces the bug
4. **Document** — if it's a common Textual gotcha, note it in CLAUDE.md

## Common Textual Pitfalls

| Symptom | Likely Cause | Fix |
|---|---|---|
| Widget not visible | Missing `yield` in `compose()` | Add `yield widget` |
| CSS not applying | Wrong selector specificity | Use more specific selector or `!important` |
| App freezes | Blocking call in async context | Wrap in `@work(thread=True)` |
| Key binding ignored | Conflict with parent binding | Check BINDINGS precedence |
| Reactive not updating | Mutating list/dict in place | Use `mutate_reactive(self, "attr_name")` context manager |
| Worker error silent | No error handler on worker | Add `on_worker_state_changed` handler |
| Screen flickers | Full re-render on small change | Use targeted `widget.refresh()` not `screen.refresh()` |
| Input not focused | Focus not set after mount | Call `widget.focus()` in `on_mount` |
