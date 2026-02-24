from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label, ListView, ListItem


# ── Command history ───────────────────────────────────────────────────────────


class CommandHistory:
    """In-memory command history with Up/Down navigation.

    Stores at most *max_size* unique consecutive entries (consecutive
    duplicates are silently dropped). Navigation index is independent of
    appends so submitting a command always resets to the "no selection" state.
    """

    def __init__(self, max_size: int = 100) -> None:
        self._history: list[str] = []
        self._index: int = -1          # -1 = not navigating
        self._max_size = max_size

    # ── Mutation ──────────────────────────────────────────────────────────────

    def add(self, command: str) -> None:
        """Append *command* to history (empty strings and consecutive duplicates ignored)."""
        if not command:
            return
        if self._history and self._history[-1] == command:
            return
        self._history.append(command)
        if len(self._history) > self._max_size:
            self._history.pop(0)

    def reset_navigation(self) -> None:
        """Reset the navigation cursor to the "no selection" state."""
        self._index = -1

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_up(self) -> str | None:
        """Return the previous command, or ``None`` when history is empty."""
        if not self._history:
            return None
        if self._index == -1:
            self._index = len(self._history) - 1
        elif self._index > 0:
            self._index -= 1
        return self._history[self._index]

    def navigate_down(self) -> str | None:
        """Return the next command, or ``None`` when past the newest entry."""
        if self._index == -1:
            return None
        self._index += 1
        if self._index >= len(self._history):
            self._index = -1
            return None
        return self._history[self._index]

    # ── Inspection ────────────────────────────────────────────────────────────

    def all(self) -> list[str]:
        """Return a copy of the full history list (oldest first)."""
        return list(self._history)

    def __len__(self) -> int:
        return len(self._history)


# ── Fuzzy matcher ─────────────────────────────────────────────────────────────


class FuzzyMatcher:
    """Fuzzy command matcher backed by rapidfuzz with substring fallback.

    Uses ``rapidfuzz.process.extract`` with ``partial_ratio`` scoring when
    rapidfuzz is available; falls back to case-insensitive substring matching
    so the widget works even if the package is missing.
    """

    def __init__(self, commands: list[str] | None = None) -> None:
        self._commands: list[str] = list(commands or [])

    def set_commands(self, commands: list[str]) -> None:
        """Replace the searchable command list."""
        self._commands = list(commands)

    def match(self, query: str, limit: int = 5) -> list[str]:
        """Return up to *limit* commands that best match *query*.

        Returns an empty list for an empty query or no commands.
        """
        if not query or not self._commands:
            return []
        try:
            from rapidfuzz import fuzz, process  # type: ignore

            results = process.extract(
                query,
                self._commands,
                scorer=fuzz.partial_ratio,
                limit=limit,
            )
            return [r[0] for r in results if r[1] > 40]
        except ImportError:
            lower = query.lower()
            return [c for c in self._commands if lower in c.lower()][:limit]


# ── Command input widget ──────────────────────────────────────────────────────


class CommandInput(Widget):
    """Text input with history navigation and fuzzy autocomplete.

    Keyboard shortcuts:
    - **Enter** — submit the command (posts :class:`Submitted` message)
    - **Up / Down** — navigate command history
    - **Tab** — accept the first autocomplete suggestion
    - **Escape** — clear the input and reset history cursor

    Register commands via :meth:`set_commands`. Wire :class:`Submitted` in the
    parent screen/app to forward commands to the plugin system (Phase 2).
    """

    DEFAULT_CSS = """
    CommandInput {
        height: auto;
        background: #1a1b26;
        border-top: solid #3b4261;
    }
    #cmd-input-field {
        background: #1a1b26;
        border: none;
        color: #a9b1d6;
        padding: 0 2;
    }
    #cmd-input-field:focus {
        border: none;
    }
    #cmd-autocomplete {
        height: auto;
        max-height: 6;
        background: #1f2335;
        border: round #3b4261;
        display: none;
    }
    #cmd-autocomplete > ListItem {
        background: #1f2335;
        color: #a9b1d6;
        padding: 0 2;
    }
    #cmd-autocomplete > ListItem:hover {
        background: #24283b;
    }
    #cmd-autocomplete > ListItem.--highlight {
        background: #3b4261;
        color: #c0caf5;
    }
    """

    BINDINGS = [
        Binding("up", "history_up", "Previous command", show=False),
        Binding("down", "history_down", "Next command", show=False),
        Binding("tab", "autocomplete", "Autocomplete", show=False),
        Binding("escape", "clear_input", "Clear", show=False),
    ]

    class Submitted(Message):
        """Posted when the user submits a command."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(
        self,
        placeholder: str = "▶  Enter command…",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._placeholder = placeholder
        self._history = CommandHistory()
        self._matcher = FuzzyMatcher()
        self._suggestions: list[str] = []

    def compose(self) -> ComposeResult:
        yield ListView(id="cmd-autocomplete")
        yield Input(placeholder=self._placeholder, id="cmd-input-field")

    def on_mount(self) -> None:
        self.query_one("#cmd-input-field", Input).focus()

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        if query:
            self._suggestions = self._matcher.match(query)
            self._update_autocomplete()
        else:
            self._hide_autocomplete()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            self._history.add(value)
            self._history.reset_navigation()
            self.post_message(self.Submitted(value))
        self._set_input("")
        self._hide_autocomplete()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Accept an autocomplete suggestion when the user clicks it."""
        event.stop()
        idx = event.index
        if idx is not None and 0 <= idx < len(self._suggestions):
            self._set_input(self._suggestions[idx])
            self._hide_autocomplete()
            self.focus_input()

    # ── Key actions ───────────────────────────────────────────────────────────

    def action_history_up(self) -> None:
        cmd = self._history.navigate_up()
        if cmd is not None:
            self._set_input(cmd)

    def action_history_down(self) -> None:
        cmd = self._history.navigate_down()
        self._set_input(cmd if cmd is not None else "")

    def action_autocomplete(self) -> None:
        if self._suggestions:
            self._set_input(self._suggestions[0])
            self._hide_autocomplete()

    def action_clear_input(self) -> None:
        self._set_input("")
        self._hide_autocomplete()
        self._history.reset_navigation()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_commands(self, commands: list[str]) -> None:
        """Update the pool of autocomplete candidates."""
        self._matcher.set_commands(commands)

    def focus_input(self) -> None:
        """Move keyboard focus to the text field."""
        try:
            self.query_one("#cmd-input-field", Input).focus()
        except Exception:
            pass

    # ── Internal ──────────────────────────────────────────────────────────────

    def _set_input(self, value: str) -> None:
        try:
            self.query_one("#cmd-input-field", Input).value = value
        except Exception:
            pass

    def _update_autocomplete(self) -> None:
        try:
            lv = self.query_one("#cmd-autocomplete", ListView)
            lv.clear()
            for suggestion in self._suggestions:
                lv.append(ListItem(Label(suggestion)))
            lv.display = bool(self._suggestions)
        except Exception:
            pass

    def _hide_autocomplete(self) -> None:
        self._suggestions = []
        try:
            lv = self.query_one("#cmd-autocomplete", ListView)
            lv.clear()
            lv.display = False
        except Exception:
            pass
