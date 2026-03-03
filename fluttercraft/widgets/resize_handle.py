from __future__ import annotations

from textual import events
from textual.message import Message
from textual.widget import Widget


# ── Constants ─────────────────────────────────────────────────────────────────

SIDEBAR_MIN: int = 18
SIDEBAR_MAX: int = 50
SIDEBAR_DEFAULT: int = 26

OUTPUT_MIN: int = 3
OUTPUT_MAX: int = 40
OUTPUT_DEFAULT: int = 8


# ── Pure helper (testable without Textual) ────────────────────────────────────


def _clamp_sidebar(width: int) -> int:
    """Return *width* clamped to [SIDEBAR_MIN, SIDEBAR_MAX]."""
    return max(SIDEBAR_MIN, min(SIDEBAR_MAX, width))


def _clamp_output(height: int) -> int:
    """Return *height* clamped to [OUTPUT_MIN, OUTPUT_MAX]."""
    return max(OUTPUT_MIN, min(OUTPUT_MAX, height))


# ── Widget ────────────────────────────────────────────────────────────────────


class ResizeHandle(Widget):
    """One-column-wide draggable divider between the sidebar and content area.

    **Mouse:** click-drag left/right to resize the sidebar.
    **Keyboard:** ``Ctrl+Left`` / ``Ctrl+Right`` on the parent
    :class:`~fluttercraft.screens.dashboard.DashboardScreen` (wired there).

    Posts :class:`Resized` with the x-delta each time the mouse moves while
    held down. The parent screen listens and adjusts the sidebar width.
    """

    DEFAULT_CSS = """
    ResizeHandle {
        width: 1;
        background: #3b4261;
    }
    ResizeHandle:hover {
        background: #7aa2f7;
    }
    ResizeHandle.dragging {
        background: #7aa2f7;
    }
    """

    # ── Messages ──────────────────────────────────────────────────────────────

    class Resized(Message):
        """Posted during a drag with the column delta since the last event."""

        def __init__(self, delta: int) -> None:
            self.delta = delta
            super().__init__()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._dragging: bool = False
        self._last_x: int = 0

    # ── Mouse handlers ────────────────────────────────────────────────────────

    def on_mouse_down(self, event: events.MouseDown) -> None:
        event.stop()
        self._dragging = True
        self._last_x = event.screen_x
        self.capture_mouse()
        self.add_class("dragging")

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._dragging:
            return
        event.stop()
        delta = event.screen_x - self._last_x
        if delta != 0:
            self._last_x = event.screen_x
            self.post_message(self.Resized(delta))

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if not self._dragging:
            return
        event.stop()
        self._dragging = False
        self.release_mouse()
        self.remove_class("dragging")

    def on_leave(self, event: events.Leave) -> None:
        """Safety net: stop drag if the cursor leaves the widget unexpectedly."""
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            self.remove_class("dragging")


# ── Output panel resize handle ────────────────────────────────────────────────


class OutputResizeHandle(Widget):
    """One-row-high draggable divider between the content area and output panel.

    **Mouse:** click-drag up/down to resize the output panel.
    **Keyboard:** ``Ctrl+Up`` / ``Ctrl+Down`` on the parent
    :class:`~fluttercraft.screens.dashboard.DashboardScreen` (wired there).

    Posts :class:`Resized` with the y-delta each time the mouse moves while
    held down. Dragging **up** (negative delta) grows the output panel;
    dragging **down** (positive delta) shrinks it.
    """

    DEFAULT_CSS = """
    OutputResizeHandle {
        height: 1;
        background: #3b4261;
    }
    OutputResizeHandle:hover {
        background: #9ece6a;
    }
    OutputResizeHandle.dragging {
        background: #9ece6a;
    }
    """

    class Resized(Message):
        """Posted during a drag with the row delta since the last event."""

        def __init__(self, delta: int) -> None:
            self.delta = delta
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._dragging: bool = False
        self._last_y: int = 0

    def on_mouse_down(self, event: events.MouseDown) -> None:
        event.stop()
        self._dragging = True
        self._last_y = event.screen_y
        self.capture_mouse()
        self.add_class("dragging")

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._dragging:
            return
        event.stop()
        delta = event.screen_y - self._last_y
        if delta != 0:
            self._last_y = event.screen_y
            self.post_message(self.Resized(delta))

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if not self._dragging:
            return
        event.stop()
        self._dragging = False
        self.release_mouse()
        self.remove_class("dragging")

    def on_leave(self, event: events.Leave) -> None:
        """Safety net: stop drag if the cursor leaves the widget unexpectedly."""
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            self.remove_class("dragging")
