from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

_LOGO = """\
[bold #7aa2f7]
  ______  __         __    __                  ______                     ____  __
 /      \\|  \\       |  \\  |  \\                /      \\                   /    \\|  \\
|  ▓▓▓▓▓▓\\ ▓▓____  | ▓▓  | ▓▓  ______       |  ▓▓▓▓▓▓\\  ______   ____  | ▓▓▓▓\\ ▓▓__
| ▓▓_  \\▓▓ ▓▓    \\ | ▓▓  | ▓▓ /      \\      | ▓▓   \\▓▓ /      \\ |    \\ | ▓▓ \\▓▓ ▓▓  \\
| ▓▓ \\    | ▓▓▓▓▓▓\\| ▓▓  | ▓▓|  ▓▓▓▓▓▓\\     | ▓▓      |  ▓▓▓▓▓▓\\ \\▓▓▓▓\\| ▓▓  | ▓▓▓▓▓▓\\
| ▓▓▓▓    | ▓▓  | ▓▓ ▓▓  | ▓▓ \\▓▓    ▓▓     | ▓▓   __ | ▓▓   \\▓▓/      ▓▓ ▓▓  | ▓▓  | ▓▓
| ▓▓      | ▓▓  | ▓▓ ▓▓__/ ▓▓  ▓▓▓▓▓▓▓▓_    | ▓▓__/  \\| ▓▓     |  ▓▓▓▓▓▓ ▓▓  | ▓▓  | ▓▓
| ▓▓      | ▓▓  | ▓▓\\▓▓    ▓▓ \\▓▓     \\  \\    \\▓▓    ▓▓| ▓▓      \\▓▓    \\ ▓▓  | ▓▓  | ▓▓
 \\▓▓       \\▓▓   \\▓▓ \\▓▓▓▓▓▓   \\▓▓▓▓▓▓▓       \\▓▓▓▓▓▓  \\▓▓       \\▓▓▓▓▓▓\\▓▓   \\▓▓   \\▓▓
[/bold #7aa2f7]"""

_TAGLINE = "[dim #565f89]Your Flutter development command centre[/]"
_VERSION = "[bold #3d59a1]v0.2.0[/]"
_HINT    = "[dim #3b4261]Loading…[/]"


class SplashScreen(Screen):
    """Brief intro splash shown at startup before pushing DashboardScreen."""

    AUTO_FOCUS = ""

    CSS = """
    SplashScreen {
        background: #1a1b26;
        align: center middle;
    }
    #splash-box {
        width: auto;
        height: auto;
        content-align: center middle;
        text-align: center;
        padding: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(
            f"{_LOGO}\n\n{_TAGLINE}  {_VERSION}\n\n{_HINT}",
            id="splash-box",
            markup=True,
        )

    def on_mount(self) -> None:
        # Auto-dismiss after 1.4 s
        self.set_timer(1.4, self._dismiss)

    def _dismiss(self) -> None:
        from fluttercraft.screens.dashboard import DashboardScreen
        self.app.switch_screen(DashboardScreen())
