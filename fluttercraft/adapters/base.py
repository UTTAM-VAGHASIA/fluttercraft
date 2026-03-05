from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class AdapterMessage:
    """A single message in a conversation."""

    role: str          # "user" | "assistant" | "system"
    content: str
    timestamp: float = 0.0


@dataclass
class AdapterSession:
    """Represents one CLI conversation session."""

    adapter_id: str
    session_id: str
    messages: list[AdapterMessage] = field(default_factory=list)
    active: bool = False
    context: dict = field(default_factory=dict)   # project/git context injected


# ── Abstract adapter ──────────────────────────────────────────────────────────


class CLIAdapter(ABC):
    """Base class for all CLI AI adapters (Claude, Gemini, OpenCode…).

    Lifecycle:
        adapter.detect()          → True if binary available
        adapter.start_session()   → returns AdapterSession
        adapter.send(session, msg, on_chunk)  → streams reply via callback
        adapter.stop_session(session)
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Machine identifier, e.g. ``'claude'``."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name, e.g. ``'Claude Code'``."""

    @property
    @abstractmethod
    def icon(self) -> str:
        """Display icon glyph."""

    @abstractmethod
    def detect(self) -> bool:
        """Return True if the backing binary is available on PATH."""

    @abstractmethod
    def start_session(self, context: dict | None = None) -> AdapterSession:
        """Create and return a new session."""

    @abstractmethod
    def send(
        self,
        session: AdapterSession,
        message: str,
        on_chunk: Callable[[str], None],
        on_done: Callable[[], None] | None = None,
    ) -> None:
        """Send *message* in *session*, calling *on_chunk* for each output chunk.

        Must be called from a background thread (not the Textual event loop).
        """

    @abstractmethod
    def stop_session(self, session: AdapterSession) -> None:
        """Terminate the session and free resources."""

    def build_context_prompt(self, context: dict) -> str:
        """Format project context as a short preamble for the AI."""
        parts: list[str] = []
        if context.get("project_name"):
            parts.append(f"Project: {context['project_name']}")
        if context.get("project_path"):
            parts.append(f"Path: {context['project_path']}")
        if context.get("flutter_version"):
            parts.append(f"Flutter: {context['flutter_version']}")
        if context.get("git_branch"):
            parts.append(f"Branch: {context['git_branch']}")
        return "\n".join(parts)
