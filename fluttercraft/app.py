from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding

from fluttercraft.screens.dashboard import DashboardScreen


class FlutterCraftApp(App):
    """FlutterCraft TUI — Flutter development tool."""

    CSS_PATH = "themes/styles.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command Palette", show=False),
    ]

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())
