from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from fluttercraft.widgets.footer import FlutterCraftFooter
from fluttercraft.widgets.header import FlutterCraftHeader

_SIDEBAR = """\

  [bold #7aa2f7]1[/]  [#bb9af7]◈[/]  FVM Manager
  [bold #7aa2f7]2[/]  [#bb9af7]◈[/]  Flutter
  [bold #7aa2f7]3[/]  [#bb9af7]◈[/]  Git Control
  [bold #7aa2f7]4[/]  [#bb9af7]◈[/]  Project Creator
  [bold #7aa2f7]5[/]  [#bb9af7]◈[/]  File Browser
  [bold #7aa2f7]6[/]  [#bb9af7]◈[/]  Workspace
  [bold #7aa2f7]7[/]  [#bb9af7]◈[/]  CLI Adapters
"""

_WELCOME = """\
[bold #7aa2f7]⚡ FlutterCraft[/]  [dim #565f89]v0.2.0[/]

[#565f89]Your Flutter development command centre[/]

[dim #3b4261]──────────────────────────────────────[/]

  [dim #565f89]Press [/][bold #a9b1d6]1–7[/][dim #565f89] to open a plugin[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+P[/][dim #565f89] for the command palette[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+T[/][dim #565f89] to switch themes[/]
  [dim #565f89]Press [/][bold #a9b1d6]?[/][dim #565f89] for help[/]
"""

_OUTPUT = "  [bold #9ece6a]▶[/]  [dim #565f89]FlutterCraft ready[/]"


class DashboardScreen(Screen):
    """Main FlutterCraft dashboard — sidebar + content + output."""

    def compose(self) -> ComposeResult:
        yield FlutterCraftHeader()
        with Horizontal(id="main-area"):
            yield Static(_SIDEBAR, id="sidebar")
            with Vertical(id="content-area"):
                yield Static(_WELCOME, id="content-panel")
                yield Static(_OUTPUT, id="output-panel")
        yield FlutterCraftFooter()

    def on_mount(self) -> None:
        self.query_one("#sidebar", Static).border_title = "Plugins"
        self.query_one("#content-panel", Static).border_title = "Welcome"
        self.query_one("#output-panel", Static).border_title = "Output"
