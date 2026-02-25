from __future__ import annotations

import pytest

from fluttercraft.widgets.sidebar import (
    DEFAULT_PLUGINS,
    PluginEntry,
    SidebarPanel,
    _format_entry,
)


# ── Pure function tests (no Textual) ─────────────────────────────────────────


def test_format_entry_unselected_contains_label():
    entry = PluginEntry(1, "◈", "FVM Manager", "fvm")
    result = _format_entry(entry, selected=False)
    assert "FVM Manager" in result


def test_format_entry_selected_contains_label():
    entry = PluginEntry(1, "◈", "FVM Manager", "fvm")
    result = _format_entry(entry, selected=True)
    assert "FVM Manager" in result


def test_format_entry_selected_has_indicator():
    entry = PluginEntry(2, "◈", "Flutter", "flutter")
    result = _format_entry(entry, selected=True)
    assert "◀" in result


def test_format_entry_unselected_no_indicator():
    entry = PluginEntry(2, "◈", "Flutter", "flutter")
    result = _format_entry(entry, selected=False)
    assert "◀" not in result


def test_format_entry_selected_uses_bright_color():
    entry = PluginEntry(3, "◈", "Git Control", "git")
    result = _format_entry(entry, selected=True)
    assert "#c0caf5" in result or "#7aa2f7" in result


def test_format_entry_unselected_uses_muted_color():
    entry = PluginEntry(3, "◈", "Git Control", "git")
    result = _format_entry(entry, selected=False)
    assert "#a9b1d6" in result


def test_format_entry_contains_number():
    entry = PluginEntry(5, "◈", "File Browser", "files")
    assert "5" in _format_entry(entry, selected=False)
    assert "5" in _format_entry(entry, selected=True)


def test_format_entry_contains_icon():
    entry = PluginEntry(1, "◈", "FVM Manager", "fvm")
    assert "◈" in _format_entry(entry, selected=False)


def test_plugin_entry_dataclass():
    e = PluginEntry(number=1, icon="◈", label="FVM Manager", plugin_id="fvm")
    assert e.number == 1
    assert e.plugin_id == "fvm"


def test_default_plugins_has_seven_entries():
    assert len(DEFAULT_PLUGINS) == 7


def test_default_plugins_numbers_are_one_to_seven():
    numbers = [e.number for e in DEFAULT_PLUGINS]
    assert numbers == list(range(1, 8))


def test_default_plugins_all_have_plugin_ids():
    for entry in DEFAULT_PLUGINS:
        assert entry.plugin_id != ""


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_test_app(plugins=None):
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield SidebarPanel(plugins=plugins)

    return _TestApp()


@pytest.mark.asyncio
async def test_sidebar_mounts():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        assert panel is not None


@pytest.mark.asyncio
async def test_sidebar_border_title_is_plugins():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        assert panel.border_title == "Plugins"


@pytest.mark.asyncio
async def test_sidebar_default_selected_is_zero():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        assert panel.selected == 0


@pytest.mark.asyncio
async def test_sidebar_select_updates_selected():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.select(2)
        assert panel.selected == 2


@pytest.mark.asyncio
async def test_sidebar_select_posts_plugin_selected():
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
        panel = pilot.app.query_one(SidebarPanel)
        panel.select(1)
        await pilot.pause()
        assert len(received) == 1
        assert received[0].number == 1
        assert received[0].plugin_id == "fvm"


@pytest.mark.asyncio
async def test_sidebar_select_out_of_range_is_noop():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.select(99)
        assert panel.selected == 0


@pytest.mark.asyncio
async def test_sidebar_select_next_wraps():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.selected = 7
        panel.select_next()
        assert panel.selected == 1


@pytest.mark.asyncio
async def test_sidebar_select_prev_wraps():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.selected = 1
        panel.select_prev()
        assert panel.selected == 7


@pytest.mark.asyncio
async def test_sidebar_active_plugin_id_none_when_unselected():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        assert panel.active_plugin_id is None


@pytest.mark.asyncio
async def test_sidebar_active_plugin_id_after_select():
    async with _make_test_app().run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.select(3)
        assert panel.active_plugin_id == "git"


@pytest.mark.asyncio
async def test_sidebar_custom_plugins():
    custom = [PluginEntry(1, "★", "Custom", "custom")]
    async with _make_test_app(plugins=custom).run_test() as pilot:
        panel = pilot.app.query_one(SidebarPanel)
        panel.select(1)
        assert panel.active_plugin_id == "custom"
