from __future__ import annotations

import pytest

from fluttercraft.widgets.command_input import CommandHistory, FuzzyMatcher, CommandInput


# ── CommandHistory tests (pure, no Textual) ───────────────────────────────────


def test_history_add_and_len():
    h = CommandHistory()
    h.add("flutter run")
    assert len(h) == 1


def test_history_ignores_empty():
    h = CommandHistory()
    h.add("")
    assert len(h) == 0


def test_history_ignores_consecutive_duplicate():
    h = CommandHistory()
    h.add("flutter run")
    h.add("flutter run")
    assert len(h) == 1


def test_history_allows_non_consecutive_duplicate():
    h = CommandHistory()
    h.add("flutter run")
    h.add("flutter build")
    h.add("flutter run")
    assert len(h) == 3


def test_history_navigate_up_returns_latest():
    h = CommandHistory()
    h.add("first")
    h.add("second")
    assert h.navigate_up() == "second"


def test_history_navigate_up_twice():
    h = CommandHistory()
    h.add("first")
    h.add("second")
    h.navigate_up()
    assert h.navigate_up() == "first"


def test_history_navigate_up_clamps_at_oldest():
    h = CommandHistory()
    h.add("only")
    h.navigate_up()
    assert h.navigate_up() == "only"


def test_history_navigate_down_after_up():
    h = CommandHistory()
    h.add("first")
    h.add("second")
    h.navigate_up()
    h.navigate_up()
    assert h.navigate_down() == "second"


def test_history_navigate_down_past_newest_returns_none():
    h = CommandHistory()
    h.add("cmd")
    h.navigate_up()
    assert h.navigate_down() is None


def test_history_navigate_down_without_navigation_returns_none():
    h = CommandHistory()
    h.add("cmd")
    assert h.navigate_down() is None


def test_history_navigate_up_empty_returns_none():
    h = CommandHistory()
    assert h.navigate_up() is None


def test_history_reset_navigation():
    h = CommandHistory()
    h.add("cmd")
    h.navigate_up()
    h.reset_navigation()
    assert h.navigate_down() is None  # cursor is back at -1


def test_history_all_returns_copy():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    lst = h.all()
    lst.append("c")
    assert len(h) == 2


def test_history_max_size_evicts_oldest():
    h = CommandHistory(max_size=3)
    h.add("a")
    h.add("b")
    h.add("c")
    h.add("d")
    assert "a" not in h.all()
    assert len(h) == 3


# ── FuzzyMatcher tests (pure, no Textual) ────────────────────────────────────


def test_fuzzy_empty_query_returns_empty():
    fm = FuzzyMatcher(["flutter run", "flutter build"])
    assert fm.match("") == []


def test_fuzzy_no_commands_returns_empty():
    fm = FuzzyMatcher([])
    assert fm.match("flutter") == []


def test_fuzzy_substring_match():
    fm = FuzzyMatcher(["flutter run", "flutter build", "git status"])
    results = fm.match("flutter")
    assert any("flutter" in r for r in results)


def test_fuzzy_set_commands_replaces_list():
    fm = FuzzyMatcher(["old"])
    fm.set_commands(["new1", "new2"])
    results = fm.match("new")
    assert any("new" in r for r in results)


def test_fuzzy_limit_respected():
    commands = [f"cmd{i}" for i in range(20)]
    fm = FuzzyMatcher(commands)
    results = fm.match("cmd", limit=3)
    assert len(results) <= 3


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_test_app():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield CommandInput()

    return _TestApp()


@pytest.mark.asyncio
async def test_command_input_mounts():
    async with _make_test_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        assert widget is not None


@pytest.mark.asyncio
async def test_command_input_set_commands():
    async with _make_test_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        widget.set_commands(["flutter run", "flutter build"])
        assert widget._matcher._commands == ["flutter run", "flutter build"]


@pytest.mark.asyncio
async def test_command_input_submitted_message():
    received: list[str] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield CommandInput()

        def on_command_input_submitted(self, event: CommandInput.Submitted) -> None:
            received.append(event.value)

    async with _TestApp().run_test() as pilot:
        from textual.widgets import Input
        inp = pilot.app.query_one("#cmd-input-field", Input)
        await pilot.click(inp)
        await pilot.press(*list("flutter run"))
        await pilot.press("enter")
        assert received == ["flutter run"]


@pytest.mark.asyncio
async def test_command_input_history_stored_after_submit():
    async with _make_test_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        from textual.widgets import Input
        inp = pilot.app.query_one("#cmd-input-field", Input)
        await pilot.click(inp)
        await pilot.press(*list("mycommand"))
        await pilot.press("enter")
        assert "mycommand" in widget._history.all()


@pytest.mark.asyncio
async def test_command_input_escape_clears_field():
    async with _make_test_app().run_test() as pilot:
        from textual.widgets import Input
        inp = pilot.app.query_one("#cmd-input-field", Input)
        await pilot.click(inp)
        await pilot.press(*list("hello"))
        await pilot.press("escape")
        assert inp.value == ""
