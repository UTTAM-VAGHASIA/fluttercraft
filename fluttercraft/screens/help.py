from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import RichLog, Static


_HELP_CONTENT = """\
[bold #7aa2f7]⚡ FlutterCraft — Keyboard Reference[/]

[bold #a9b1d6]── Navigation ──────────────────────────────────────────[/]
  [bold]1–7[/]          Switch to plugin panel (FVM, Flutter, Git, …)
  [bold]0[/]            Go back to Welcome screen
  [bold]Escape[/]       Go back to Welcome  (press twice if input has text)
  [bold]Ctrl+P[/]       Open command palette
  [bold]Ctrl+T[/]       Open theme picker
  [bold]Ctrl+,[/]       Open settings
  [bold]?[/]            Show this help screen
  [bold]Ctrl+Q[/]       Quit FlutterCraft

[bold #a9b1d6]── Layout ───────────────────────────────────────────────[/]
  [bold]Ctrl+Right[/]   Widen sidebar
  [bold]Ctrl+Left[/]    Narrow sidebar
  [bold]Ctrl+Up[/]      Grow output panel
  [bold]Ctrl+Down[/]    Shrink output panel
  Drag resize handles with mouse

[bold #a9b1d6]── Slash Commands ──────────────────────────────────────[/]
  [bold]/help[/]        Show help in output panel
  [bold]/clear[/]       Clear output panel
  [bold]/theme[/]       Open theme picker
  [bold]/settings[/]    Open settings
  [bold]/quit[/]        Quit FlutterCraft

[bold #a9b1d6]── Plugin 1: FVM Manager ────────────────────────────────[/]
  [bold]fvm install[/]      Install a Flutter version
  [bold]fvm use[/]          Switch global Flutter version
  [bold]fvm list[/]         List installed versions
  [bold]fvm releases[/]     Browse available releases
  [bold]fvm remove[/]       Remove a version
  [bold]fvm doctor[/]       Check FVM health
  [bold]fvm config[/]       Show FVM config

[bold #a9b1d6]── Plugin 2: Flutter Commands ───────────────────────────[/]
  [bold]flutter doctor[/]   Run flutter doctor
  [bold]flutter run[/]      Run the app
  [bold]flutter build[/]    Build the app
  [bold]flutter test[/]     Run tests
  [bold]flutter analyze[/]  Run analysis
  [bold]flutter pub get[/]  Get dependencies
  [bold]flutter clean[/]    Clean build cache
  [bold]flutter upgrade[/]  Upgrade Flutter SDK
  [bold]flutter devices[/]  List connected devices

[bold #a9b1d6]── Plugin 3: Git Control ────────────────────────────────[/]
  [bold]↑↓[/]      Navigate files       [bold]s/u[/]   Stage / unstage file
  [bold]a[/]       Stage all            [bold]c[/]     Commit (opens modal)
  [bold]p[/]       Push                 [bold]P[/]     Pull
  [bold]f[/]       Fetch                [bold]b[/]     Branch list
  [bold]n[/]       New branch           [bold]l[/]     Log viewer
  [bold]z/Z[/]     Stash push / pop     [bold]r[/]     Refresh

[bold #a9b1d6]── Plugin 4: Project Creator ────────────────────────────[/]
  Multi-step wizard — follow on-screen prompts
  [bold]n/→[/]   Next step       [bold]b/←[/]  Previous step
  [bold]Enter[/]  Select item     [bold]Space[/] Toggle selection
  [bold]P[/]     Preview template

[bold #a9b1d6]── Plugin 5: File Browser ───────────────────────────────[/]
  [bold]↑↓[/]    Navigate         [bold]Enter/→[/]  Expand / open
  [bold]←[/]     Collapse dir     [bold]Space[/]     Preview file
  [bold]Ctrl+O[/] Quick open       [bold]n/N[/]      New file / new dir
  [bold]d[/]     Delete           [bold]r[/]         Rename
  [bold]e[/]     Open in editor   [bold]s[/]         Search in files
  [bold]f[/]     Filter           [bold]R[/]         Refresh
  [bold]h[/]     Toggle hidden

[bold #a9b1d6]── Plugin 6: Workspace ─────────────────────────────────[/]
  [bold]add <path>[/]    Add a Flutter project
  [bold]switch <name>[/] Switch active project
  [bold]scan[/]          Auto-discover projects
  [bold]health[/]        Check project health
  [bold]↑↓[/]           Navigate project list   [bold]Enter[/]  Switch project

[bold #a9b1d6]── Plugin 7: CLI Adapters ───────────────────────────────[/]
  [bold]Tab bar[/]        Click to switch Claude / Gemini / OpenCode
  [bold]Enter[/]          Send message
  [bold]Ctrl+N[/]         New session
  [bold]Ctrl+H[/]         Toggle history panel
  [bold]Ctrl+L[/]         Clear output
  [bold]ask <msg>[/]      Send message via command input
  [bold]switch claude[/]  Switch adapter via command input

[bold #a9b1d6]── Settings ─────────────────────────────────────────────[/]
  [bold]/settings[/] or [bold]Ctrl+,[/]  Open settings panel
  Arrow keys / click to navigate options

[dim #565f89]Press Escape or Q to close this help.[/]
"""


class HelpScreen(ModalScreen):
    """In-app keyboard reference — press ? or /help to open."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("q", "dismiss", "Close", show=False),
    ]

    CSS = """
    HelpScreen {
        background: #1a1b2699;
        align: center middle;
    }
    #help-container {
        width: 80;
        height: 90vh;
        background: #1a1b26;
        border: round #7aa2f7;
        border-title-color: #7aa2f7;
        overflow: hidden auto;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help-container"):
            yield RichLog(id="help-log", highlight=False, markup=True, wrap=True)

    def on_mount(self) -> None:
        container = self.query_one("#help-container")
        container.border_title = "Help  (Esc or Q to close)"
        log = self.query_one("#help-log", RichLog)
        log.write(_HELP_CONTENT)
