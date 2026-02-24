from __future__ import annotations

from dataclasses import dataclass

from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


# ── Data type ─────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class PluginEntry:
    """One item in the sidebar plugin list."""

    number: int   # 1-based shortcut key
    icon: str     # decorative glyph, e.g. "◈"
    label: str    # display name
    plugin_id: str  # machine identifier, e.g. "fvm"


# ── Default plugin list ───────────────────────────────────────────────────────

DEFAULT_PLUGINS: list[PluginEntry] = [
    PluginEntry(1, "◈", "FVM Manager",     "fvm"),
    PluginEntry(2, "◈", "Flutter",          "flutter"),
    PluginEntry(3, "◈", "Git Control",      "git"),
    PluginEntry(4, "◈", "Project Creator",  "project"),
    PluginEntry(5, "◈", "File Browser",     "files"),
    PluginEntry(6, "◈", "Workspace",        "workspace"),
    PluginEntry(7, "◈", "CLI Adapters",     "cli"),
]


# ── Pure helper (testable without Textual) ────────────────────────────────────


def _plugin_number_from_id(widget_id: str) -> int | None:
    """Extract the plugin number from a label ID like ``'plugin-entry-3'``.

    Returns ``None`` for any string that is not a valid plugin-entry ID.
    Pure function — testable without Textual.
    """
    if not widget_id.startswith("plugin-entry-"):
        return None
    try:
        return int(widget_id.split("-")[-1])
    except (ValueError, IndexError):
        return None


def _format_entry(entry: PluginEntry, selected: bool) -> str:
    """Return Rich markup for a single sidebar row.

    Unselected: muted colours.
    Selected: bright blue number + white label + left arrow indicator.
    """
    if selected:
        return (
            f" [bold #7aa2f7]{entry.number}[/]  "
            f"[#7aa2f7]{entry.icon}[/]  "
            f"[bold #c0caf5]{entry.label}[/] "
            f"[#7aa2f7]◀[/]"
        )
    return (
        f" [bold #7aa2f7]{entry.number}[/]  "
        f"[#bb9af7]{entry.icon}[/]  "
        f"[#a9b1d6]{entry.label}[/]"
    )


# ── Sidebar widget ────────────────────────────────────────────────────────────


class SidebarPanel(Widget):
    """Plugin navigation sidebar.

    Displays the plugin list with a highlighted active entry. Selecting an
    entry posts :class:`PluginSelected`; the parent screen listens and
    switches the content area to that plugin's view.

    Keyboard (when sidebar or app has focus):
    - **1–7** — jump directly to a plugin
    - **Up / Down** — move selection one step

    Call :meth:`select` programmatically from the parent screen's bindings.
    """

    DEFAULT_CSS = """
    SidebarPanel {
        width: 26;
        background: #1f2335;
        border: round #3b4261;
        border-title-color: #7aa2f7;
        border-title-align: left;
        margin-right: 1;
    }
    SidebarPanel Label {
        padding: 0 1;
        width: 1fr;
    }
    SidebarPanel Label:hover {
        background: #24283b;
    }
    SidebarPanel Label.selected {
        background: #1a1b26;
    }
    SidebarPanel Label.selected:hover {
        background: #1e2030;
    }
    """

    selected: reactive[int] = reactive(0)  # 0 = nothing selected; 1-7 otherwise

    # ── Messages ──────────────────────────────────────────────────────────────

    class PluginSelected(Message):
        """Posted when the user activates a plugin entry."""

        def __init__(self, number: int, plugin_id: str) -> None:
            self.number = number
            self.plugin_id = plugin_id
            super().__init__()

    # ── Init & lifecycle ──────────────────────────────────────────────────────

    def __init__(
        self,
        plugins: list[PluginEntry] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._plugins: list[PluginEntry] = list(plugins or DEFAULT_PLUGINS)

    def compose(self) -> ComposeResult:
        yield Label("", id="sidebar-spacer-top")
        for entry in self._plugins:
            yield Label(
                _format_entry(entry, selected=False),
                id=f"plugin-entry-{entry.number}",
            )
        yield Label("", id="sidebar-spacer-bottom")

    def on_mount(self) -> None:
        self.border_title = "Plugins"

    def on_click(self, event: events.Click) -> None:
        """Select a plugin when the user clicks its label row."""
        widget = event.widget
        if widget is None:
            return
        number = _plugin_number_from_id(widget.id or "")
        if number is not None:
            self.select(number)

    # ── Reactive watcher ──────────────────────────────────────────────────────

    def watch_selected(self, value: int) -> None:
        """Re-render all entries whenever selection changes."""
        for entry in self._plugins:
            is_selected = entry.number == value
            label = self.query_one(f"#plugin-entry-{entry.number}", Label)
            label.update(_format_entry(entry, selected=is_selected))
            label.set_class(is_selected, "selected")

    # ── Public API ────────────────────────────────────────────────────────────

    def select(self, number: int) -> None:
        """Activate plugin *number* (1-based).  No-op if out of range."""
        if 1 <= number <= len(self._plugins):
            self.selected = number
            entry = self._plugins[number - 1]
            self.post_message(self.PluginSelected(number, entry.plugin_id))

    def select_next(self) -> None:
        """Move selection one step down, wrapping at the bottom."""
        if not self._plugins:
            return
        nxt = (self.selected % len(self._plugins)) + 1
        self.select(nxt)

    def select_prev(self) -> None:
        """Move selection one step up, wrapping at the top."""
        if not self._plugins:
            return
        n = len(self._plugins)
        prv = ((self.selected - 2) % n) + 1
        self.select(prv)

    @property
    def active_plugin_id(self) -> str | None:
        """Return the ``plugin_id`` of the currently selected entry, or None."""
        if self.selected == 0:
            return None
        return self._plugins[self.selected - 1].plugin_id
