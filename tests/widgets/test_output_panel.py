from __future__ import annotations

import pytest

from fluttercraft.widgets.output_panel import (
    OutputPanel,
    _level_markup,
    _LEVEL_COLORS,
    _LEVEL_PREFIXES,
)


# ── Pure function tests (no Textual) ─────────────────────────────────────────


def test_level_markup_info_contains_text():
    result = _level_markup("hello", "info")
    assert "hello" in result


def test_level_markup_success_color():
    result = _level_markup("done", "success")
    assert _LEVEL_COLORS["success"] in result


def test_level_markup_error_color():
    result = _level_markup("failed", "error")
    assert _LEVEL_COLORS["error"] in result


def test_level_markup_warning_color():
    result = _level_markup("careful", "warning")
    assert _LEVEL_COLORS["warning"] in result


def test_level_markup_cmd_color():
    result = _level_markup("flutter run", "cmd")
    assert _LEVEL_COLORS["cmd"] in result


def test_level_markup_dim_color():
    result = _level_markup("...", "dim")
    assert _LEVEL_COLORS["dim"] in result


def test_level_markup_unknown_level_falls_back_to_info():
    result = _level_markup("text", "unknown_level")
    assert _LEVEL_COLORS["info"] in result


def test_level_markup_success_prefix():
    result = _level_markup("ok", "success")
    assert _LEVEL_PREFIXES["success"] in result


def test_level_markup_error_prefix():
    result = _level_markup("bad", "error")
    assert _LEVEL_PREFIXES["error"] in result


def test_level_markup_returns_string():
    assert isinstance(_level_markup("x", "info"), str)


def test_level_markup_default_level_is_info():
    result_explicit = _level_markup("text", "info")
    result_default = _level_markup("text")
    assert result_explicit == result_default


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_test_app():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

    return _TestApp()


@pytest.mark.asyncio
async def test_output_panel_mounts():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        assert panel is not None


@pytest.mark.asyncio
async def test_output_panel_has_richlog():
    from textual.widgets import RichLog

    async with _make_test_app().run_test() as pilot:
        log = pilot.app.query_one("#output-log", RichLog)
        assert log is not None


@pytest.mark.asyncio
async def test_output_panel_border_title_is_output():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        assert panel.border_title == "Output"


@pytest.mark.asyncio
async def test_output_panel_write_posts_written_message():
    received: list[OutputPanel.Written] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

        def on_output_panel_written(self, event: OutputPanel.Written) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write("hello", "info")
        await pilot.pause()
        assert len(received) >= 1
        assert received[-1].text == "hello"
        assert received[-1].level == "info"


@pytest.mark.asyncio
async def test_output_panel_write_success():
    received: list[OutputPanel.Written] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

        def on_output_panel_written(self, event: OutputPanel.Written) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write_success("Build OK")
        await pilot.pause()
        assert any(e.level == "success" for e in received)


@pytest.mark.asyncio
async def test_output_panel_write_error():
    received: list[OutputPanel.Written] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

        def on_output_panel_written(self, event: OutputPanel.Written) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write_error("Build failed")
        await pilot.pause()
        assert any(e.level == "error" for e in received)


@pytest.mark.asyncio
async def test_output_panel_write_warning():
    received: list[OutputPanel.Written] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

        def on_output_panel_written(self, event: OutputPanel.Written) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write_warning("deprecated API")
        await pilot.pause()
        assert any(e.level == "warning" for e in received)


@pytest.mark.asyncio
async def test_output_panel_write_cmd():
    received: list[OutputPanel.Written] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield OutputPanel()

        def on_output_panel_written(self, event: OutputPanel.Written) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write_cmd("flutter run")
        await pilot.pause()
        assert any(e.level == "cmd" and e.text == "flutter run" for e in received)


@pytest.mark.asyncio
async def test_output_panel_clear_does_not_raise():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(OutputPanel)
        panel.write_info("something")
        panel.clear()  # should not raise
