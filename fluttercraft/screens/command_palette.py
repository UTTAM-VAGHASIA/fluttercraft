from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Input, Static


class CommandPaletteScreen(ModalScreen):
    """Global fuzzy command palette — opened with Ctrl+P.

    Aggregates commands from all registered plugins and the global app.
    Type to filter, Up/Down to navigate, Enter to run, Escape to close.

    The dismissed value is the selected command's ``action`` callable, or
    ``None`` if the user pressed Escape without selecting.

    Usage (from :class:`~fluttercraft.app.FlutterCraftApp`)::

        cmds = self.plugin_registry.all_commands()
        cmds += self._builtin_commands()
        self.push_screen(CommandPaletteScreen(cmds), self._on_palette_result)
    """

    BINDINGS = [
        Binding("escape",    "dismiss",         "Close",    show=False, priority=True),
        Binding("up",        "move_up",          "Up",       show=False, priority=True),
        Binding("down",      "move_down",        "Down",     show=False, priority=True),
        Binding("enter",     "select_command",   "Select",   show=False, priority=True),
    ]

    DEFAULT_CSS = """
    CommandPaletteScreen {
        align: center top;
        padding-top: 4;
    }
    CommandPaletteScreen > Vertical {
        width: 72;
        max-width: 90%;
        background: #1f2335;
        border: round #7aa2f7;
        height: auto;
        max-height: 30;
    }
    #palette-input {
        border: none;
        background: #1f2335;
        color: #c0caf5;
        padding: 0 1;
    }
    #palette-divider {
        height: 1;
        background: #3b4261;
        color: #3b4261;
    }
    #palette-results {
        background: #1f2335;
        color: #a9b1d6;
        padding: 0 1;
        height: auto;
        max-height: 22;
    }
    """

    _cursor: reactive[int] = reactive(0)

    def __init__(self, commands: list[dict], **kwargs) -> None:
        super().__init__(**kwargs)
        self._all_commands = list(commands)
        self._filtered: list[dict] = list(commands)

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(
                placeholder="> type to search commands…",
                id="palette-input",
            )
            yield Static("─" * 72, id="palette-divider")
            yield Static(self._render_list(), id="palette-results")

    def on_mount(self) -> None:
        self.query_one("#palette-input", Input).focus()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_list(self) -> str:
        if not self._filtered:
            return "[dim #565f89]  No commands found[/]"
        lines: list[str] = []
        for i, cmd in enumerate(self._filtered[:20]):
            title = cmd.get("title", "Untitled")
            desc = cmd.get("description", "")
            plugin = cmd.get("plugin_id", "")
            suffix = desc or plugin
            if i == self._cursor:
                lines.append(
                    f" [bold #7aa2f7]▶ {title}[/]"
                    + (f"  [dim #a9b1d6]{suffix}[/]" if suffix else "")
                )
            else:
                lines.append(
                    f"   [#a9b1d6]{title}[/]"
                    + (f"  [dim #565f89]{suffix}[/]" if suffix else "")
                )
        return "\n".join(lines)

    def _refresh_results(self) -> None:
        try:
            self.query_one("#palette-results", Static).update(self._render_list())
        except Exception:
            pass

    # ── Filtering ─────────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        if not query:
            self._filtered = list(self._all_commands)
        else:
            try:
                from rapidfuzz import fuzz, process

                titles = [c.get("title", "") for c in self._all_commands]
                results = process.extract(
                    query, titles, scorer=fuzz.partial_ratio, limit=20
                )
                matched = {r[0] for r in results if r[1] > 30}
                self._filtered = [
                    c for c in self._all_commands if c.get("title") in matched
                ]
            except ImportError:
                q = query.lower()
                self._filtered = [
                    c
                    for c in self._all_commands
                    if q in c.get("title", "").lower()
                    or q in c.get("description", "").lower()
                ]

        self._cursor = 0
        self._refresh_results()

    # ── Navigation ────────────────────────────────────────────────────────────

    def action_move_up(self) -> None:
        if self._filtered:
            self._cursor = (self._cursor - 1) % min(len(self._filtered), 20)
            self._refresh_results()

    def action_move_down(self) -> None:
        if self._filtered:
            self._cursor = (self._cursor + 1) % min(len(self._filtered), 20)
            self._refresh_results()

    def action_select_command(self) -> None:
        if self._filtered and 0 <= self._cursor < len(self._filtered):
            cmd = self._filtered[self._cursor]
            action = cmd.get("action")
            self.dismiss(action)
        else:
            self.dismiss(None)
