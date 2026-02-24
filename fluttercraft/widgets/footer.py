from __future__ import annotations

from dataclasses import dataclass, field

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


# ── Data type ─────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class KeyHint:
    """A single keybinding hint displayed in the footer."""

    key: str          # e.g. "^Q", "^P", "?"
    description: str  # e.g. "Quit", "Palette", "Help"


# ── Global (default) keybindings ──────────────────────────────────────────────

GLOBAL_HINTS: list[KeyHint] = [
    KeyHint("^Q", "Quit"),
    KeyHint("^P", "Palette"),
    KeyHint("^T", "Theme"),
    KeyHint("?", "Help"),
]


# ── Pure helper (testable without Textual) ────────────────────────────────────


def _format_hints(hints: list[KeyHint]) -> str:
    """Build the footer display string from *hints*.

    Each hint is rendered as ``key description`` and separated by four spaces.
    An empty list returns an empty string.
    """
    return "    ".join(
        f"[bold]{h.key}[/bold] {h.description}" for h in hints
    )


# ── Footer widget ─────────────────────────────────────────────────────────────


class FlutterCraftFooter(Widget):
    """Context-aware keybinding hints bar.

    Shows global keybindings by default. Plugins register their own hint sets
    via :meth:`register_context`; the footer switches to those hints when the
    plugin is focused via :meth:`set_context`.

    This wiring (focus → set_context) happens in Phase 2 via the EventBus.
    """

    DEFAULT_CSS = """
    FlutterCraftFooter {
        height: 1;
        background: #7aa2f7;
        color: #1a1b26;
        content-align: left middle;
        padding: 0 2;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_hints: list[KeyHint] = list(GLOBAL_HINTS)
        self._contexts: dict[str, list[KeyHint]] = {}

    def compose(self) -> ComposeResult:
        yield Label(_format_hints(self._current_hints), id="footer-hints")

    # ── Public API ────────────────────────────────────────────────────────────

    def set_keybindings(self, hints: list[KeyHint]) -> None:
        """Replace the displayed keybindings with *hints*."""
        self._current_hints = list(hints)
        self._refresh_label()

    def reset_to_global(self) -> None:
        """Restore the default global keybindings."""
        self.set_keybindings(GLOBAL_HINTS)

    def register_context(self, plugin_id: str, hints: list[KeyHint]) -> None:
        """Register a named keybinding set for *plugin_id*.

        Called by plugins during init (Phase 2). Does not immediately change
        the display — use :meth:`set_context` to activate.
        """
        self._contexts[plugin_id] = list(hints)

    def set_context(self, plugin_id: str) -> None:
        """Switch to the keybindings registered for *plugin_id*.

        Falls back to global hints if *plugin_id* has no registered context.
        """
        self.set_keybindings(self._contexts.get(plugin_id, GLOBAL_HINTS))

    # ── Internal ──────────────────────────────────────────────────────────────

    def _refresh_label(self) -> None:
        try:
            self.query_one("#footer-hints", Label).update(
                _format_hints(self._current_hints)
            )
        except Exception:
            pass  # Not yet mounted
