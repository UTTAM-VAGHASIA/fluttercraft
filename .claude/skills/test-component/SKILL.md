---
name: test-component
description: Generate tests for FlutterCraft Textual components using Pilot and pytest-asyncio
user-invocable: true
disable-model-invocation: false
---

# Component Test Generator

You generate tests for FlutterCraft's Textual TUI components using Textual's built-in Pilot testing framework and pytest-asyncio.

## Instructions

### Step 1: Read the Component

Read the screen, widget, or modal that needs testing. Identify:
- What it renders (compose tree)
- What reactive attributes it has
- What messages it emits/handles
- What user interactions it supports (key bindings, clicks, input)
- What workers/async operations it performs

### Step 2: Generate Test File

Place tests in `tests/tui/` mirroring the source structure:
```
tests/
├── conftest.py              # Shared fixtures
├── tui/
│   ├── __init__.py
│   ├── test_app.py
│   ├── screens/
│   │   ├── __init__.py
│   │   └── test_dashboard.py
│   └── widgets/
│       ├── __init__.py
│       └── test_status_bar.py
└── commands/
    ├── __init__.py
    └── test_fvm_command.py
```

### Step 3: Write Tests

Follow this pattern for every test:

```python
"""Tests for [ComponentName]."""

from __future__ import annotations

import pytest
from textual.app import App, ComposeResult

from fluttercraft.tui.widgets.your_widget import YourWidget


# Create a minimal app that mounts the widget under test
class YourWidgetApp(App):
    def compose(self) -> ComposeResult:
        yield YourWidget()


class TestYourWidget:
    """Tests for YourWidget."""

    @pytest.mark.asyncio
    async def test_initial_render(self) -> None:
        """Widget renders with correct initial state."""
        async with YourWidgetApp().run_test() as pilot:
            widget = pilot.app.query_one(YourWidget)
            assert widget is not None
            # Assert initial state

    @pytest.mark.asyncio
    async def test_reactive_update(self) -> None:
        """Reactive attribute changes trigger re-render."""
        async with YourWidgetApp().run_test() as pilot:
            widget = pilot.app.query_one(YourWidget)
            widget.value = "new_value"
            await pilot.pause()  # Let Textual process the change
            # Assert updated render

    @pytest.mark.asyncio
    async def test_key_binding(self) -> None:
        """Key binding triggers expected action."""
        async with YourWidgetApp().run_test() as pilot:
            await pilot.press("enter")
            # Assert expected behavior

    @pytest.mark.asyncio
    async def test_message_emission(self) -> None:
        """Widget emits correct message on interaction."""
        messages = []

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield YourWidget()

            def on_your_widget_changed(self, event: YourWidget.Changed) -> None:
                messages.append(event.value)

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(YourWidget)
            widget.value = "test"
            await pilot.pause()
            assert len(messages) == 1
            assert messages[0] == "test"
```

### Test Categories to Cover

For each component, generate tests for:

1. **Rendering**: Component mounts and shows expected content
2. **Reactivity**: Reactive attributes update the display
3. **Messages**: Events are emitted and handled correctly
4. **Key Bindings**: Keyboard shortcuts trigger correct actions
5. **Edge Cases**: Empty state, error state, boundary values
6. **Workers**: Async operations complete and update UI (mock external calls)

### Testing Dependencies

The test setup requires:
```
pip install pytest pytest-asyncio
```

In `pyproject.toml` or `pytest.ini`:
```ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
```

### Mocking External Commands

For commands that call Flutter CLI or FVM:
```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_flutter_upgrade_success() -> None:
    with patch("fluttercraft.commands.flutter_commands.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Flutter 3.35.0"
        # Run the test
```
