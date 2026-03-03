from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


# ── Toast widget ──────────────────────────────────────────────────────────────

_LEVEL_STYLE: dict[str, tuple[str, str]] = {
    "info":    ("#7aa2f7", "ℹ"),
    "success": ("#9ece6a", "✓"),
    "warning": ("#e0af68", "⚠"),
    "error":   ("#f7768e", "✗"),
}


class Toast(Widget):
    """A single auto-dismissing notification toast.

    Mount this to the screen (or any parent) — it auto-removes itself after
    *timeout* seconds.

    Levels: ``"info"`` (default) · ``"success"`` · ``"warning"`` · ``"error"``

    Usage (from inside a screen or widget)::

        self.mount(Toast("Flutter upgraded successfully!", level="success"))
        self.mount(Toast("Connection failed", level="error", timeout=6.0))
    """

    DEFAULT_CSS = """
    Toast {
        dock: bottom;
        height: auto;
        width: auto;
        max-width: 60;
        padding: 0 2;
        margin-bottom: 1;
        margin-right: 2;
        background: #1f2335;
        border: round #3b4261;
        layer: notification;
    }
    Toast Static {
        background: transparent;
    }
    """

    def __init__(
        self,
        message: str,
        level: str = "info",
        timeout: float = 4.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        color, icon = _LEVEL_STYLE.get(level, ("#c0caf5", "•"))
        self._markup = f"[{color}]{icon}[/]  [{color}]{message}[/]"
        self._timeout = timeout

    def compose(self) -> ComposeResult:
        yield Static(self._markup)

    def on_mount(self) -> None:
        self.set_timer(self._timeout, self.remove)


# ── App-level helper ──────────────────────────────────────────────────────────


class Notifier:
    """Convenience wrapper that mounts :class:`Toast` widgets onto a screen.

    Attach one to :class:`~fluttercraft.app.FlutterCraftApp` so any widget can
    call ``self.app.notifier.notify(...)``::

        # in FlutterCraftApp.__init__:
        self.notifier = Notifier(self)

        # from any widget:
        self.app.notifier.notify("Done!", level="success")
        self.app.notifier.notify("Oops", level="error", timeout=6.0)
    """

    def __init__(self, app) -> None:
        self._app = app

    def notify(
        self,
        message: str,
        level: str = "info",
        timeout: float = 4.0,
    ) -> None:
        """Mount a :class:`Toast` onto the current screen."""
        try:
            screen = self._app.screen
            screen.mount(Toast(message, level=level, timeout=timeout))
        except Exception:
            pass  # Never crash when showing a notification
