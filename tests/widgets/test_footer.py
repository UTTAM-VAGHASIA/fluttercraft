from __future__ import annotations

from unittest.mock import patch

import pytest

from fluttercraft.widgets.footer import (
    GLOBAL_HINTS,
    FlutterCraftFooter,
    KeyHint,
    _format_hints,
)


# ── Pure function tests (no Textual) ─────────────────────────────────────────


def test_format_hints_single():
    hints = [KeyHint("^Q", "Quit")]
    assert "^Q" in _format_hints(hints)
    assert "Quit" in _format_hints(hints)


def test_format_hints_multiple():
    hints = [KeyHint("^Q", "Quit"), KeyHint("^P", "Palette")]
    result = _format_hints(hints)
    assert "^Q" in result
    assert "^P" in result
    assert "Palette" in result


def test_format_hints_empty():
    assert _format_hints([]) == ""


def test_format_hints_separator():
    hints = [KeyHint("^Q", "Quit"), KeyHint("^P", "Palette")]
    result = _format_hints(hints)
    assert "    " in result  # four-space separator


def test_format_hints_uses_bold_markup():
    result = _format_hints([KeyHint("^Q", "Quit")])
    assert "[bold]" in result
    assert "[/bold]" in result


def test_global_hints_has_quit():
    keys = [h.key for h in GLOBAL_HINTS]
    assert "^Q" in keys


def test_global_hints_has_four_items():
    assert len(GLOBAL_HINTS) == 4


def test_key_hint_dataclass():
    hint = KeyHint(key="^T", description="Theme")
    assert hint.key == "^T"
    assert hint.description == "Theme"


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_test_app():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield FlutterCraftFooter()

    return _TestApp()


@pytest.mark.asyncio
async def test_footer_mounts_without_error():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        assert footer is not None


@pytest.mark.asyncio
async def test_footer_default_hints_are_global():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        assert footer._current_hints == list(GLOBAL_HINTS)


@pytest.mark.asyncio
async def test_footer_set_keybindings_updates_hints():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        custom = [KeyHint("^S", "Save"), KeyHint("^X", "Close")]
        footer.set_keybindings(custom)
        assert footer._current_hints == custom


@pytest.mark.asyncio
async def test_footer_reset_to_global_restores_defaults():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        footer.set_keybindings([KeyHint("^X", "Custom")])
        footer.reset_to_global()
        assert footer._current_hints == list(GLOBAL_HINTS)


@pytest.mark.asyncio
async def test_footer_register_and_set_context():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        fvm_hints = [KeyHint("^I", "Install"), KeyHint("^S", "Switch")]
        footer.register_context("fvm", fvm_hints)
        footer.set_context("fvm")
        assert footer._current_hints == fvm_hints


@pytest.mark.asyncio
async def test_footer_unknown_context_falls_back_to_global():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        footer.set_context("unknown_plugin")
        assert footer._current_hints == list(GLOBAL_HINTS)


@pytest.mark.asyncio
async def test_footer_set_keybindings_does_not_mutate_input():
    async with _make_test_app().run_test() as pilot:
        footer = pilot.app.query_one(FlutterCraftFooter)
        original = [KeyHint("^A", "Action")]
        footer.set_keybindings(original)
        original.append(KeyHint("^B", "Other"))
        assert len(footer._current_hints) == 1
