from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

# ── Event types ───────────────────────────────────────────────────────────────


@dataclass(slots=True)
class FileChangedEvent:
    """A file in the watched project directory changed."""

    path: str
    change_type: str = "modified"  # "created" | "modified" | "deleted"


@dataclass(slots=True)
class GitChangedEvent:
    """Git repository state changed (branch, staged files, etc.)."""

    branch: str = ""
    has_changes: bool = False


@dataclass(slots=True)
class SessionUpdateEvent:
    """An AI CLI session produced output or changed state."""

    session_id: str
    status: str  # "started" | "message" | "error" | "stopped"
    message: str = ""


@dataclass(slots=True)
class FocusChangedEvent:
    """The active plugin panel changed."""

    plugin_id: str


@dataclass(slots=True)
class RefreshNeededEvent:
    """A component needs to re-render its data."""

    scope: str = "all"  # "all" | "header" | plugin_id


@dataclass(slots=True)
class ErrorEvent:
    """A non-fatal error occurred inside a plugin or adapter."""

    source: str
    message: str
    exc: Exception | None = field(default=None)


# Union type for type checkers
Event = (
    FileChangedEvent
    | GitChangedEvent
    | SessionUpdateEvent
    | FocusChangedEvent
    | RefreshNeededEvent
    | ErrorEvent
)

Handler = Callable[[Any], None]


# ── Event bus ─────────────────────────────────────────────────────────────────


class EventBus:
    """Typed publish/subscribe event bus.

    Plugins subscribe to specific event types; the bus dispatches to all
    registered handlers when an event is published. Supports both sync and
    async handlers. One bad handler never crashes others (silent degradation).

    Usage::

        bus = EventBus()

        def on_git(event: GitChangedEvent) -> None:
            print(event.branch)

        bus.subscribe(GitChangedEvent, on_git)
        bus.publish(GitChangedEvent(branch="main", has_changes=True))
        bus.unsubscribe(GitChangedEvent, on_git)
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Handler]] = defaultdict(list)

    # ── Subscription ──────────────────────────────────────────────────────────

    def subscribe(self, event_type: type, handler: Handler) -> None:
        """Register *handler* to be called whenever *event_type* is published.

        Duplicate registrations are silently ignored.
        """
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Handler) -> None:
        """Remove *handler* from *event_type*. No-op if not registered."""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    # ── Publishing ────────────────────────────────────────────────────────────

    def publish(self, event: Event) -> None:
        """Fire-and-forget publish.

        Sync handlers are called immediately. Async handlers are scheduled
        as asyncio tasks on the running loop (if any).
        """
        for handler in list(self._handlers.get(type(event), [])):
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    try:
                        asyncio.get_running_loop().create_task(result)
                    except RuntimeError:
                        pass  # No running loop — skip async handler
            except Exception:
                pass  # Silent degradation

    async def publish_async(self, event: Event) -> None:
        """Publish and await all async handlers; call all sync handlers."""
        for handler in list(self._handlers.get(type(event), [])):
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                pass  # Silent degradation
