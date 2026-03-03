from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Static

from fluttercraft.themes.theme_manager import ThemeDefinition


class ThemePickerScreen(ModalScreen):
    """Theme selection overlay — Ctrl+T.

    Shows all 13 built-in themes grouped by dark/light.
    Navigate with Up/Down, apply with Enter, cancel with Escape.
    The dismissed value is the chosen :class:`ThemeDefinition`, or ``None``
    if the user pressed Escape.
    """

    BINDINGS = [
        Binding("escape", "cancel_picker",  "Cancel", show=False, priority=True),
        Binding("up",     "move_up",        "Up",     show=False, priority=True),
        Binding("down",   "move_down",      "Down",   show=False, priority=True),
        Binding("enter",  "select_theme",   "Apply",  show=False, priority=True),
    ]

    DEFAULT_CSS = """
    ThemePickerScreen {
        align: center middle;
    }
    ThemePickerScreen > Vertical {
        width: 52;
        height: auto;
        max-height: 36;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 0 1;
    }
    #picker-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        padding: 0 0 1 0;
        width: 1fr;
    }
    #picker-list {
        background: #1f2335;
        color: #a9b1d6;
        height: auto;
        width: 1fr;
    }
    #picker-hint {
        color: #565f89;
        text-align: center;
        padding: 1 0 0 0;
        width: 1fr;
    }
    """

    _cursor: reactive[int] = reactive(0)

    def __init__(
        self,
        themes: list[ThemeDefinition],
        active_index: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._themes = themes
        self._cursor = active_index
        self._original_index = active_index  # used to restore on Escape

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("⚡ Select Theme", id="picker-title")
            yield Static(self._render_list(), id="picker-list")
            yield Static(
                "[dim]↑ ↓  navigate    Enter  apply    Esc  cancel[/]",
                id="picker-hint",
            )

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_list(self) -> str:
        lines: list[str] = []
        dark_header_shown = False
        light_header_shown = False

        for i, theme in enumerate(self._themes):
            # Section headers
            if theme.is_dark and not dark_header_shown:
                lines.append("[dim #565f89] ── Dark ──────────────────────────────[/]")
                dark_header_shown = True
            elif not theme.is_dark and not light_header_shown:
                lines.append("[dim #565f89] ── Light ─────────────────────────────[/]")
                light_header_shown = True

            mode = "🌙" if theme.is_dark else "☀"
            if i == self._cursor:
                lines.append(
                    f" [bold #7aa2f7]▶ {mode}  {theme.name:<22}[/bold #7aa2f7]"
                    f"[dim #a9b1d6]{theme.description[:18]}[/]"
                )
            else:
                lines.append(
                    f"   [dim #565f89]{mode}[/]  [#a9b1d6]{theme.name:<22}[/]"
                    f"[dim #565f89]{theme.description[:18]}[/]"
                )

        return "\n".join(lines)

    def _refresh_list(self) -> None:
        try:
            self.query_one("#picker-list", Static).update(self._render_list())
        except Exception:
            pass

    # ── Navigation ────────────────────────────────────────────────────────────

    def action_move_up(self) -> None:
        self._cursor = (self._cursor - 1) % len(self._themes)
        self._refresh_list()
        self._preview_current()

    def action_move_down(self) -> None:
        self._cursor = (self._cursor + 1) % len(self._themes)
        self._refresh_list()
        self._preview_current()

    def action_cancel_picker(self) -> None:
        """Escape — restore the original theme then close without applying."""
        self._apply_preview(self._themes[self._original_index])
        self.dismiss(None)

    def action_select_theme(self) -> None:
        self.dismiss(self._themes[self._cursor])

    # ── Live preview ──────────────────────────────────────────────────────────

    def _preview_current(self) -> None:
        self._apply_preview(self._themes[self._cursor])

    def _apply_preview(self, theme: ThemeDefinition) -> None:
        try:
            self.app._apply_theme(theme)
        except Exception:
            pass
