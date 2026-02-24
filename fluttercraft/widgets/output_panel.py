from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import RichLog


# ── Level helpers (testable without Textual) ──────────────────────────────────

_LEVEL_COLORS: dict[str, str] = {
    "info":    "#a9b1d6",
    "success": "#9ece6a",
    "error":   "#f7768e",
    "warning": "#e0af68",
    "cmd":     "#7aa2f7",
    "dim":     "#565f89",
}

_LEVEL_PREFIXES: dict[str, str] = {
    "info":    "·",
    "success": "▶",
    "error":   "✖",
    "warning": "⚠",
    "cmd":     "$",
    "dim":     "·",
}


def _level_markup(text: str, level: str = "info") -> str:
    """Return a Rich markup string for *text* at *level*.

    Produces:  ``prefix  text``  coloured with the Tokyo Night palette.
    Pure function — testable without Textual.
    """
    color = _LEVEL_COLORS.get(level, _LEVEL_COLORS["info"])
    prefix = _LEVEL_PREFIXES.get(level, "·")
    return f"[{color}]{prefix}[/{color}]  [{color}]{text}[/{color}]"


# ── Output panel widget ───────────────────────────────────────────────────────


class OutputPanel(Widget):
    """Scrollable output log for command results and status messages.

    Write to the panel from anywhere in the app::

        panel = self.app.query_one(OutputPanel)
        panel.write_success("Build finished")
        panel.write_error("flutter: command not found")
        panel.write_cmd("flutter run --release")
        panel.clear()

    The widget also posts :class:`Written` whenever a line is appended so
    other widgets can react to new output (Phase 2 EventBus wiring).
    """

    DEFAULT_CSS = """
    OutputPanel {
        height: 5;
        background: #16161e;
        border: round #3b4261;
        border-title-color: #9ece6a;
        border-title-align: left;
    }
    OutputPanel > RichLog {
        background: #16161e;
        color: #a9b1d6;
        padding: 0 1;
    }
    """

    # ── Messages ──────────────────────────────────────────────────────────────

    class Written(Message):
        """Posted after a line is appended to the log."""

        def __init__(self, text: str, level: str) -> None:
            self.text = text
            self.level = level
            super().__init__()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield RichLog(id="output-log", wrap=True, highlight=False, markup=True)

    def on_mount(self) -> None:
        self.border_title = "Output"
        self._write_raw(_level_markup("FlutterCraft ready", "dim"))

    # ── Public API ────────────────────────────────────────────────────────────

    def write(self, text: str, level: str = "info") -> None:
        """Append *text* to the log at *level* (info / success / error / warning / cmd / dim)."""
        markup = _level_markup(text, level)
        self._write_raw(markup)
        self.post_message(self.Written(text, level))

    def write_info(self, text: str) -> None:
        self.write(text, "info")

    def write_success(self, text: str) -> None:
        self.write(text, "success")

    def write_error(self, text: str) -> None:
        self.write(text, "error")

    def write_warning(self, text: str) -> None:
        self.write(text, "warning")

    def write_cmd(self, text: str) -> None:
        """Display a command that was executed (blue $ prefix)."""
        self.write(text, "cmd")

    def clear(self) -> None:
        """Clear all output lines."""
        try:
            self.query_one("#output-log", RichLog).clear()
        except Exception:
            pass

    # ── Internal ──────────────────────────────────────────────────────────────

    def _write_raw(self, markup: str) -> None:
        try:
            self.query_one("#output-log", RichLog).write(markup)
        except Exception:
            pass
