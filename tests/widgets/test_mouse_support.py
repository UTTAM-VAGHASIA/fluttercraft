from __future__ import annotations

import pytest

from fluttercraft.widgets.sidebar import _plugin_number_from_id, SidebarPanel
from fluttercraft.widgets.command_input import CommandInput


# ── Pure function tests: _plugin_number_from_id ───────────────────────────────


def test_plugin_number_from_valid_id_1():
    assert _plugin_number_from_id("plugin-entry-1") == 1


def test_plugin_number_from_valid_id_7():
    assert _plugin_number_from_id("plugin-entry-7") == 7


def test_plugin_number_from_valid_id_middle():
    assert _plugin_number_from_id("plugin-entry-4") == 4


def test_plugin_number_from_non_entry_id_returns_none():
    assert _plugin_number_from_id("sidebar") is None


def test_plugin_number_from_empty_string_returns_none():
    assert _plugin_number_from_id("") is None


def test_plugin_number_from_partial_prefix_returns_none():
    assert _plugin_number_from_id("plugin-entry-") is None


def test_plugin_number_from_non_numeric_suffix_returns_none():
    assert _plugin_number_from_id("plugin-entry-abc") is None


def test_plugin_number_from_spacer_id_returns_none():
    assert _plugin_number_from_id("sidebar-spacer-top") is None


def test_plugin_number_from_unrelated_id_returns_none():
    assert _plugin_number_from_id("content-panel") is None


# ── Sidebar click-to-select tests ─────────────────────────────────────────────


def _make_sidebar_app(plugins=None):
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield SidebarPanel(plugins=plugins)

    return _TestApp()


@pytest.mark.asyncio
async def test_sidebar_click_entry_selects_plugin():
    async with _make_sidebar_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        assert panel.selected == 0
        await pilot.click("#plugin-entry-3")
        assert panel.selected == 3


@pytest.mark.asyncio
async def test_sidebar_click_posts_plugin_selected_message():
    received: list[SidebarPanel.PluginSelected] = []

    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield SidebarPanel()

        def on_sidebar_panel_plugin_selected(
            self, event: SidebarPanel.PluginSelected
        ) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        await pilot.click("#plugin-entry-2")
        await pilot.pause()
        assert len(received) == 1
        assert received[0].number == 2
        assert received[0].plugin_id == "flutter"


@pytest.mark.asyncio
async def test_sidebar_click_different_entries():
    async with _make_sidebar_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        await pilot.click("#plugin-entry-1")
        assert panel.selected == 1
        await pilot.click("#plugin-entry-5")
        assert panel.selected == 5


@pytest.mark.asyncio
async def test_sidebar_click_updates_label_class():
    async with _make_sidebar_app().run_test() as pilot:
        from textual.widgets import Label
        await pilot.click("#plugin-entry-4")
        label = pilot.app.query_one("#plugin-entry-4", Label)
        assert label.has_class("selected")


@pytest.mark.asyncio
async def test_sidebar_click_deselects_previous_label():
    async with _make_sidebar_app().run_test() as pilot:
        from textual.widgets import Label
        await pilot.click("#plugin-entry-2")
        await pilot.click("#plugin-entry-6")
        label2 = pilot.app.query_one("#plugin-entry-2", Label)
        label6 = pilot.app.query_one("#plugin-entry-6", Label)
        assert not label2.has_class("selected")
        assert label6.has_class("selected")


# ── CommandInput click-to-accept autocomplete tests ───────────────────────────


def _make_cmd_app():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield CommandInput()

    return _TestApp()


@pytest.mark.asyncio
async def test_autocomplete_list_view_selected_sets_input():
    """Directly trigger ListView.Selected to simulate a click."""
    from textual.app import App, ComposeResult
    from textual.widgets import Input, ListView, ListItem, Label

    async with _make_cmd_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        widget.set_commands(["flutter run", "flutter build", "flutter test"])
        widget._suggestions = ["flutter run", "flutter build"]
        widget._update_autocomplete()
        await pilot.pause()

        lv = pilot.app.query_one("#cmd-autocomplete", ListView)
        items = [c for c in lv.children if isinstance(c, ListItem)]
        assert len(items) > 0

        # Fire Selected with index=0 — handler uses the index to look up _suggestions
        lv.post_message(ListView.Selected(lv, items[0]))
        await pilot.pause()

        inp = pilot.app.query_one("#cmd-input-field", Input)
        assert inp.value == "flutter run"


@pytest.mark.asyncio
async def test_autocomplete_click_hides_list():
    """After a ListView.Selected, the autocomplete list should be hidden."""
    from textual.widgets import Input, ListView, ListItem, Label

    async with _make_cmd_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        widget._suggestions = ["flutter run"]
        widget._update_autocomplete()
        await pilot.pause()

        lv = pilot.app.query_one("#cmd-autocomplete", ListView)
        items = [c for c in lv.children if isinstance(c, ListItem)]
        lv.post_message(ListView.Selected(lv, items[0]))
        await pilot.pause()

        assert not lv.display


@pytest.mark.asyncio
async def test_autocomplete_click_focuses_input():
    """After accepting a suggestion, focus should return to the input field."""
    from textual.widgets import Input, ListView, ListItem

    async with _make_cmd_app().run_test() as pilot:
        widget = pilot.app.query_one(CommandInput)
        widget._suggestions = ["flutter run"]
        widget._update_autocomplete()
        await pilot.pause()

        lv = pilot.app.query_one("#cmd-autocomplete", ListView)
        items = [c for c in lv.children if isinstance(c, ListItem)]
        lv.post_message(ListView.Selected(lv, items[0]))
        await pilot.pause()

        inp = pilot.app.query_one("#cmd-input-field", Input)
        assert inp.has_focus
