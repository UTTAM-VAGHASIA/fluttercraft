# FlutterCraft - Gemini CLI Task

> **Status:** 🔴 ACTIVE
> **Goal:** Make UI Look Like OpenCode (Minimal, No Extra Boxes)

---

## Problem

Current UI has too many bordered boxes. OpenCode style = minimal, clean, no clutter.

---

## Changes Required

### 1. Remove Multiple Bordered Boxes

**File:** `fluttercraft/utils/beautiful_prompt.py`

Find `root_container = HSplit([...])` (around line 603) and change:

**FROM (Current):**
```python
root_container = HSplit([
    build_rounded_frame(input_box, ...),      # Box 1
    ConditionalContainer(
        build_rounded_frame(completion_menu, ...),  # Box 2
    ),
    build_rounded_frame(toolbar, ...),        # Box 3
])
```

**TO (OpenCode Style):**
```python
root_container = HSplit([
    # Simple input - NO border
    LayoutWindow(content=input_control, height=Dimension(min=1, max=10)),
    
    # Completion menu - NO border, just content
    ConditionalContainer(
        LayoutWindow(content=completion_control, height=Dimension(min=1, max=6)),
        filter=should_show_menu,
    ),
    
    # Single thin separator line
    Window(char='─', height=1, style='class:separator'),
    
    # Toolbar - NO border, just text
    LayoutWindow(content=toolbar_control, height=1),
])
```

### 2. Simplify Prompt Symbol

**File:** `beautiful_prompt.py` line ~331

```python
prompt_symbol = "> "  # Simple, clean
```

### 3. Update Styles for Minimal Look

**File:** `beautiful_prompt.py` → `build_prompt_style()`

```python
return Style.from_dict({
    "": "",  # No default background forcing
    "prompt": f"{theme.accent_cyan} bold",
    "separator": f"{theme.gray}",
    "completion-menu.completion.current": f"reverse",
    "toolbar": f"{theme.semantic.text_secondary}",
})
```

### 4. Remove Welcome Header Boxes

**File:** `fluttercraft/utils/themes/service.py`

In `get_welcome_header_content()` - remove any Panel/Box wrapping, just plain text.

---

## Expected Result

```
FLUTTER CRAFT [gradient logo]

Getting Started:
💡 Use /help, /clear, /quit
📦 Manage Flutter versions with FVM
⌨️  Type / to see commands

Platform: Linux | Python: 3.12.3 | Flutter: 3.30.7 ✓

> flutter --version
  ▸ flutter --version    Coming Soon
    flutter              Run Flutter operations
──────────────────────────────────────────────
~/Desktop/fluttercraft (*) | ⬆⬇ history
```

No heavy boxes. Clean. Minimal. OpenCode style.

---

## Test

```bash
python -m fluttercraft start
```
