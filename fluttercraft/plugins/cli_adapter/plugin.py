from __future__ import annotations

import time
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, RichLog, Static

from fluttercraft.adapters.base import CLIAdapter, AdapterSession
from fluttercraft.adapters.claude import ClaudeAdapter
from fluttercraft.adapters.gemini import GeminiAdapter
from fluttercraft.adapters.opencode import OpenCodeAdapter
from fluttercraft.adapters.detect import detect_adapters
from fluttercraft.plugins.base import Plugin
from fluttercraft.plugins.cli_adapter.session_store import (
    load_sessions,
    save_sessions,
    get_history_for_adapter,
)


# ── Adapter tab bar ───────────────────────────────────────────────────────────


class _AdapterTab(Static):
    """Clickable tab for one adapter."""

    DEFAULT_CSS = """
    _AdapterTab {
        width: auto;
        padding: 0 2;
        color: #565f89;
        border: none;
    }
    _AdapterTab.active {
        color: #7aa2f7;
        text-style: bold;
    }
    _AdapterTab.unavailable {
        color: #3b4261;
    }
    """

    class Pressed(Message):
        def __init__(self, adapter_id: str) -> None:
            super().__init__()
            self.adapter_id = adapter_id

    def __init__(self, adapter: CLIAdapter, available: bool, active: bool = False) -> None:
        label = f"{adapter.icon} {adapter.name}"
        if not available:
            label += " [dim](not found)[/dim]"
        super().__init__(label, markup=True)
        self._adapter_id = adapter.id
        self._available = available
        if active:
            self.add_class("active")
        if not available:
            self.add_class("unavailable")

    def on_click(self) -> None:
        self.post_message(self._AdapterTab.Pressed(self._adapter_id))


# ── Conversation viewer ───────────────────────────────────────────────────────


class _HistoryPanel(Widget):
    """Shows past sessions for an adapter (read-only scroll)."""

    DEFAULT_CSS = """
    _HistoryPanel {
        height: 1fr;
        border: round #3b4261;
        border-title-color: #565f89;
        overflow: hidden auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield RichLog(id="history-log", highlight=True, markup=True, wrap=True)

    def load(self, sessions: list[AdapterSession]) -> None:
        log = self.query_one("#history-log", RichLog)
        log.clear()
        if not sessions:
            log.write("[dim #565f89]No history yet.[/dim]")
            return
        for s in sessions:
            log.write(f"[bold #7aa2f7]── Session {s.session_id[:8]} ──[/bold]")
            for m in s.messages:
                if m.role == "system":
                    continue
                ts = time.strftime("%H:%M", time.localtime(m.timestamp))
                if m.role == "user":
                    log.write(f"[bold #a9b1d6][{ts}] You:[/bold] {m.content}")
                else:
                    log.write(f"[#565f89][{ts}] AI:[/] {m.content}")
            log.write("")


# ── Main CLI panel widget ─────────────────────────────────────────────────────


class CLIWidget(Widget):
    """The full CLI Adapters panel — tab bar + output + input."""

    DEFAULT_CSS = """
    CLIWidget {
        height: 1fr;
        layout: vertical;
    }
    #cli-tabs {
        height: 3;
        layout: horizontal;
        background: #1a1b26;
        border: round #3b4261;
        padding: 0 1;
    }
    #cli-tabs-empty {
        height: 3;
        background: #1a1b26;
        border: round #3b4261;
        color: #565f89;
        content-align: left middle;
        padding: 0 2;
    }
    #cli-body {
        height: 1fr;
        layout: horizontal;
    }
    #cli-left {
        width: 2fr;
        height: 1fr;
        layout: vertical;
    }
    #cli-output {
        height: 1fr;
        border: round #3b4261;
        border-title-color: #7aa2f7;
        overflow: hidden auto;
    }
    #cli-input-row {
        height: 3;
        layout: horizontal;
        border: round #3b4261;
    }
    #cli-prompt {
        width: 6;
        height: 3;
        content-align: left middle;
        color: #7aa2f7;
        padding: 0 1;
    }
    #cli-input {
        height: 3;
        width: 1fr;
        border: none;
        background: #1a1b26;
    }
    #cli-right {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        margin-left: 1;
    }
    #cli-context-panel {
        height: auto;
        border: round #3b4261;
        border-title-color: #565f89;
        padding: 0 1;
        color: #565f89;
    }
    """

    BINDINGS = [
        Binding("ctrl+h", "show_history", "History", show=False),
        Binding("ctrl+n", "new_session", "New session", show=False),
        Binding("ctrl+l", "clear_output", "Clear", show=False),
    ]

    _active_adapter_id: reactive[str] = reactive("")

    def __init__(self, adapters: list[CLIAdapter], **kwargs) -> None:
        super().__init__(**kwargs)
        self._all_adapters = adapters
        self._available = detect_adapters(adapters)
        self._available_ids = {a.id for a in self._available}
        self._sessions: dict[str, AdapterSession] = {}   # adapter_id → active session
        self._history: list[AdapterSession] = load_sessions()
        self._project_context: dict = {}
        self._show_history = False
        # Pick first available adapter by default
        if self._available:
            self._active_adapter_id = self._available[0].id
        elif self._all_adapters:
            self._active_adapter_id = self._all_adapters[0].id

    def compose(self) -> ComposeResult:
        if self._all_adapters:
            with Horizontal(id="cli-tabs"):
                for adapter in self._all_adapters:
                    available = adapter.id in self._available_ids
                    active = adapter.id == self._active_adapter_id
                    yield _AdapterTab(adapter, available, active)
        else:
            yield Static("No AI CLI adapters configured.", id="cli-tabs-empty")

        with Horizontal(id="cli-body"):
            with Vertical(id="cli-left"):
                yield RichLog(id="cli-output", highlight=True, markup=True, wrap=True)
                with Horizontal(id="cli-input-row"):
                    yield Static("> ", id="cli-prompt")
                    yield Input(
                        placeholder="Type a message… (Enter to send)",
                        id="cli-input",
                    )
            with Vertical(id="cli-right"):
                yield Static(id="cli-context-panel", markup=True)
                yield _HistoryPanel(id="cli-history")

    def on_mount(self) -> None:
        output = self.query_one("#cli-output", RichLog)
        output.border_title = "Output"
        self._refresh_context_panel()
        self._show_welcome()
        history = self.query_one(_HistoryPanel)
        history.border_title = "History"
        history.display = False

    # ── Welcome message ───────────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        output = self.query_one("#cli-output", RichLog)
        output.clear()
        if not self._available:
            output.write(
                "[bold #f7768e]No AI CLI found.[/]\n"
                "[dim #565f89]Install one of:[/]\n"
                "  [#a9b1d6]claude[/]   — Claude Code (npm install -g @anthropic-ai/claude-code)\n"
                "  [#a9b1d6]gemini[/]   — Gemini CLI  (npm install -g @google/gemini-cli)\n"
                "  [#a9b1d6]opencode[/] — OpenCode    (https://opencode.ai)\n"
            )
            return

        adapter = self._get_active_adapter()
        if adapter is None:
            return
        output.write(
            f"[bold #7aa2f7]{adapter.icon} {adapter.name}[/] [dim #565f89]ready[/]\n"
            "[dim #565f89]Type a message and press Enter to send.[/]\n"
            "[dim #565f89]Ctrl+N — new session  Ctrl+H — toggle history  Ctrl+L — clear[/]\n"
        )

    # ── Adapter switching ─────────────────────────────────────────────────────

    def on__adapter_tab_pressed(self, event: _AdapterTab.Pressed) -> None:
        self._switch_adapter(event.adapter_id)

    def _switch_adapter(self, adapter_id: str) -> None:
        if adapter_id == self._active_adapter_id:
            return
        self._active_adapter_id = adapter_id
        # Update tab active state
        for tab in self.query(_AdapterTab):
            if tab._adapter_id == adapter_id:
                tab.add_class("active")
            else:
                tab.remove_class("active")
        self._show_welcome()
        self._refresh_context_panel()

    def _get_active_adapter(self) -> CLIAdapter | None:
        for a in self._all_adapters:
            if a.id == self._active_adapter_id:
                return a
        return None

    # ── Context panel ─────────────────────────────────────────────────────────

    def _refresh_context_panel(self) -> None:
        panel = self.query_one("#cli-context-panel", Static)
        ctx = self._project_context
        if not ctx:
            panel.update("[dim #565f89]No project context[/]")
            panel.border_title = "Context"
            return
        lines = ["[bold #565f89]Context[/]"]
        if ctx.get("project_name"):
            lines.append(f"  [dim]Project:[/] [#a9b1d6]{ctx['project_name']}[/]")
        if ctx.get("flutter_version"):
            lines.append(f"  [dim]Flutter:[/] [#a9b1d6]{ctx['flutter_version']}[/]")
        if ctx.get("git_branch"):
            lines.append(f"  [dim]Branch:[/]  [#a9b1d6]{ctx['git_branch']}[/]")
        panel.update("\n".join(lines))
        panel.border_title = "Context"

    def set_project_context(self, context: dict) -> None:
        self._project_context = context
        self._refresh_context_panel()

    # ── Send message ──────────────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.clear()
        self._send_message(text)

    def _send_message(self, text: str) -> None:
        adapter = self._get_active_adapter()
        if adapter is None:
            return
        if adapter.id not in self._available_ids:
            self.query_one("#cli-output", RichLog).write(
                f"[bold #f7768e]{adapter.name} is not installed.[/]"
            )
            return

        output = self.query_one("#cli-output", RichLog)
        output.write(f"[bold #a9b1d6]You:[/] {text}")
        output.write("[dim #565f89]Thinking…[/]")

        # Ensure session exists
        if adapter.id not in self._sessions:
            self._sessions[adapter.id] = adapter.start_session(self._project_context)

        session = self._sessions[adapter.id]
        self._stream_response(adapter, session, text)

    @work(thread=True)
    def _stream_response(
        self, adapter: CLIAdapter, session: AdapterSession, message: str
    ) -> None:
        output_lines: list[str] = []

        def on_chunk(chunk: str) -> None:
            output_lines.append(chunk)
            self.app.call_from_thread(self._append_chunk, chunk)

        def on_done() -> None:
            self.app.call_from_thread(self._finalize_output)
            # Persist sessions in background
            all_sessions = list(self._sessions.values()) + self._history
            save_sessions(all_sessions)

        adapter.send(session, message, on_chunk=on_chunk, on_done=on_done)

    def _append_chunk(self, chunk: str) -> None:
        output = self.query_one("#cli-output", RichLog)
        # Remove the "Thinking…" placeholder on first chunk
        if not hasattr(self, "_thinking_cleared"):
            self._thinking_cleared = True
            output.write("[bold #7aa2f7]AI:[/]")
        output.write(f"  {chunk}")

    def _finalize_output(self) -> None:
        # Reset so next send shows Thinking… again
        if hasattr(self, "_thinking_cleared"):
            del self._thinking_cleared
        output = self.query_one("#cli-output", RichLog)
        output.write("")  # blank line separator

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_new_session(self) -> None:
        adapter = self._get_active_adapter()
        if adapter is None or adapter.id not in self._available_ids:
            return
        # Archive old session
        if adapter.id in self._sessions:
            old = self._sessions.pop(adapter.id)
            self._history.append(old)
            save_sessions(list(self._sessions.values()) + self._history)
        self._show_welcome()
        self.query_one("#cli-output", RichLog).write(
            "[dim #565f89]— New session started —[/]"
        )

    def action_show_history(self) -> None:
        history_panel = self.query_one(_HistoryPanel)
        self._show_history = not self._show_history
        history_panel.display = self._show_history
        if self._show_history:
            adapter = self._get_active_adapter()
            if adapter:
                hist = get_history_for_adapter(self._history, adapter.id)
                history_panel.load(hist)

    def action_clear_output(self) -> None:
        self.query_one("#cli-output", RichLog).clear()
        self._show_welcome()


# ── Plugin ────────────────────────────────────────────────────────────────────


class CLIAdapterPlugin(Plugin):
    """Plugin 7 — CLI Adapter (Claude Code, Gemini CLI, OpenCode)."""

    def __init__(self) -> None:
        self._widget: CLIWidget | None = None
        self._adapters: list[CLIAdapter] = [
            ClaudeAdapter(),
            GeminiAdapter(),
            OpenCodeAdapter(),
        ]

    @property
    def id(self) -> str:
        return "cli"

    @property
    def name(self) -> str:
        return "CLI Adapters"

    @property
    def icon(self) -> str:
        return "◆"

    def compose(self) -> ComposeResult:
        self._widget = CLIWidget(self._adapters)
        yield self._widget

    def start(self) -> None:
        if self._widget is not None:
            try:
                self._widget.query_one("#cli-input", Input).focus()
            except Exception:
                pass

    def commands(self) -> list[dict[str, Any]]:
        return [
            {
                "title": "CLI: New session",
                "description": "Start a fresh AI conversation",
                "plugin_id": self.id,
                "action": lambda: self._widget and self._widget.action_new_session(),
            },
            {
                "title": "CLI: Toggle history",
                "description": "Show/hide past sessions",
                "plugin_id": self.id,
                "action": lambda: self._widget and self._widget.action_show_history(),
            },
            {
                "title": "CLI: Clear output",
                "description": "Clear the output panel",
                "plugin_id": self.id,
                "action": lambda: self._widget and self._widget.action_clear_output(),
            },
        ]

    def handle_command(self, text: str) -> bool:
        lower = text.lower().strip()
        if lower == "new" or lower == "new session":
            if self._widget:
                self._widget.action_new_session()
            return True
        if lower == "history":
            if self._widget:
                self._widget.action_show_history()
            return True
        if lower == "clear":
            if self._widget:
                self._widget.action_clear_output()
            return True
        # Switch adapter: "switch claude" / "switch gemini" / "switch opencode"
        if lower.startswith("switch "):
            adapter_id = lower.split(None, 1)[1].strip()
            if self._widget:
                self._widget._switch_adapter(adapter_id)
            return True
        # Send a message directly: "ask <...>"
        if lower.startswith("ask "):
            msg = text[4:].strip()
            if msg and self._widget:
                self._widget._send_message(msg)
            return True
        return False
