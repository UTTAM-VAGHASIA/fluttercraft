from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from fluttercraft.widgets.command_input import CommandInput
from fluttercraft.widgets.footer import FlutterCraftFooter
from fluttercraft.widgets.header import FlutterCraftHeader
from fluttercraft.widgets.output_panel import OutputPanel
from fluttercraft.widgets.resize_handle import (
    ResizeHandle,
    SIDEBAR_DEFAULT,
    SIDEBAR_MIN,
    SIDEBAR_MAX,
    _clamp_sidebar,
)
from fluttercraft.widgets.sidebar import SidebarPanel

_WELCOME = """\
[bold #7aa2f7]⚡ FlutterCraft[/]  [dim #565f89]v0.2.0[/]

[#565f89]Your Flutter development command centre[/]

[dim #3b4261]──────────────────────────────────────[/]

  [dim #565f89]Press [/][bold #a9b1d6]1–7[/][dim #565f89] to open a plugin[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+P[/][dim #565f89] for the command palette[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+T[/][dim #565f89] to switch themes[/]
  [dim #565f89]Press [/][bold #a9b1d6]?[/][dim #565f89] for help[/]
"""


class DashboardScreen(Screen):
    """Main FlutterCraft dashboard — sidebar + resize handle + content + output."""

    BINDINGS = [
        Binding("1", "select_plugin(1)", "FVM Manager",     show=False, priority=False),
        Binding("2", "select_plugin(2)", "Flutter",          show=False, priority=False),
        Binding("3", "select_plugin(3)", "Git Control",      show=False, priority=False),
        Binding("4", "select_plugin(4)", "Project Creator",  show=False, priority=False),
        Binding("5", "select_plugin(5)", "File Browser",     show=False, priority=False),
        Binding("6", "select_plugin(6)", "Workspace",        show=False, priority=False),
        Binding("7", "select_plugin(7)", "CLI Adapters",     show=False, priority=False),
        Binding("ctrl+right", "grow_sidebar",   "Grow sidebar",   show=False),
        Binding("ctrl+left",  "shrink_sidebar", "Shrink sidebar", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._sidebar_width: int = SIDEBAR_DEFAULT

    def compose(self) -> ComposeResult:
        yield FlutterCraftHeader()
        with Horizontal(id="main-area"):
            yield SidebarPanel(id="sidebar")
            yield ResizeHandle(id="resize-handle")
            with Vertical(id="content-area"):
                yield Static(_WELCOME, id="content-panel")
                yield OutputPanel(id="output-panel")
        yield CommandInput(id="command-input")
        yield FlutterCraftFooter()

    def on_mount(self) -> None:
        self.query_one("#content-panel", Static).border_title = "Welcome"

    # ── Plugin selection ──────────────────────────────────────────────────────

    def action_select_plugin(self, number: int) -> None:
        self.query_one(SidebarPanel).select(number)

    def on_sidebar_panel_plugin_selected(
        self, event: SidebarPanel.PluginSelected
    ) -> None:
        """Handle sidebar plugin click — update content panel and footer."""
        content = self.query_one("#content-panel", Static)
        content.update(
            f"[bold #7aa2f7]{event.plugin_id.title()}[/] plugin selected\n\n"
            f"[dim #565f89]Plugin UI will be loaded here in Phase 2[/]"
        )
        content.border_title = event.plugin_id.title()

        # Update footer context
        footer = self.query_one(FlutterCraftFooter)
        footer.set_context(event.plugin_id)

        # Write to output panel
        output = self.query_one(OutputPanel)
        output.write_info(f"Switched to {event.plugin_id}")

    # ── Command input ──────────────────────────────────────────────────────────

    def on_command_input_submitted(self, event: CommandInput.Submitted) -> None:
        """Handle command submission — display in output panel."""
        output = self.query_one(OutputPanel)
        output.write_cmd(event.value)
        output.write(f"Command registry not yet wired (Phase 2)", "dim")

    # ── Sidebar resize ────────────────────────────────────────────────────────

    def on_resize_handle_resized(self, event: ResizeHandle.Resized) -> None:
        self._apply_sidebar_width(self._sidebar_width + event.delta)

    def action_grow_sidebar(self) -> None:
        """Ctrl+Right — widen the sidebar by 2 columns."""
        self._apply_sidebar_width(self._sidebar_width + 2)

    def action_shrink_sidebar(self) -> None:
        """Ctrl+Left — narrow the sidebar by 2 columns."""
        self._apply_sidebar_width(self._sidebar_width - 2)

    def _apply_sidebar_width(self, new_width: int) -> None:
        clamped = _clamp_sidebar(new_width)
        if clamped == self._sidebar_width:
            return
        self._sidebar_width = clamped
        self.query_one(SidebarPanel).styles.width = clamped
