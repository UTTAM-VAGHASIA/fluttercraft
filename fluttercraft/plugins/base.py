from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult

if TYPE_CHECKING:
    from fluttercraft.core.config import ConfigManager
    from fluttercraft.core.events import EventBus
    from fluttercraft.core.state import StateManager


# ── Plugin context ────────────────────────────────────────────────────────────


@dataclass
class PluginContext:
    """Shared bag injected into each plugin at :meth:`Plugin.init` time.

    Plugins must not import each other. All cross-plugin communication goes
    through ``event_bus``.
    """

    work_dir: str
    project_root: str
    config: ConfigManager
    event_bus: EventBus
    state: StateManager
    adapters: dict[str, Any] = field(default_factory=dict)
    keymap: Any = None  # KeymapRegistry — guarded to avoid circular import


# ── Plugin ABC ────────────────────────────────────────────────────────────────


class Plugin(ABC):
    """Base class for all FlutterCraft plugins.

    Lifecycle (managed by :class:`PluginRegistry`)::

        registry.register(plugin)    # store
        registry.init_all(ctx)       # Plugin.init(ctx) — store context
        registry.start_all()         # Plugin.start()   — activate
        ...
        registry.stop_all()          # Plugin.stop()    — deactivate
        registry.reinit_all(ctx)     # project switch   — stop+init+start

    Required overrides: :attr:`id`, :attr:`name`, :attr:`icon`.
    All other methods have safe no-op defaults.
    """

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def id(self) -> str:
        """Machine-readable unique identifier, e.g. ``'fvm'``."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name, e.g. ``'FVM Manager'``."""

    @property
    @abstractmethod
    def icon(self) -> str:
        """Sidebar icon glyph, e.g. ``'◈'``."""

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def init(self, ctx: PluginContext) -> None:
        """Called once on registration. Stores the shared context."""
        self._ctx: PluginContext = ctx

    def start(self) -> None:
        """Called when the plugin panel becomes the active view."""

    def stop(self) -> None:
        """Called when the plugin panel is deactivated."""

    def reinit(self, ctx: PluginContext) -> None:
        """Called when the active project changes. Performs stop → init → start."""
        self.stop()
        self.init(ctx)
        self.start()

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Return the Textual widget tree for this plugin's panel.

        Override to provide a real UI. The dashboard mounts the result into the
        content area when this plugin is activated.
        """
        return iter([])

    # ── Event handler ─────────────────────────────────────────────────────────

    def update(self, event: Any) -> None:
        """Handle an EventBus event forwarded by the registry."""

    # ── Commands ──────────────────────────────────────────────────────────────

    def commands(self) -> list[dict[str, Any]]:
        """Return commands contributed to the command palette.

        Each command dict must have:
            ``title`` (str), ``description`` (str), ``action`` (callable)

        Example::

            return [
                {
                    "title": "FVM: List versions",
                    "description": "Show all cached Flutter SDK versions",
                    "action": self.list_versions,
                }
            ]
        """
        return []

    # ── Focus ─────────────────────────────────────────────────────────────────

    @property
    def is_focused(self) -> bool:
        """True if this plugin's panel currently holds focus."""
        return False

    @property
    def focus_context(self) -> str:
        """Keybinding context string used by :class:`~fluttercraft.core.keymap.KeymapRegistry`."""
        return self.id


# ── Plugin registry ───────────────────────────────────────────────────────────


class PluginRegistry:
    """Manages the full lifecycle of all registered plugins.

    Plugins are called in registration order. A crash inside any plugin's
    lifecycle method is silently swallowed so that one broken plugin can never
    take down others (**silent degradation**).

    Usage::

        registry = PluginRegistry()
        registry.register(FvmPlugin())
        registry.init_all(ctx)
        registry.start_all()
        ...
        registry.reinit_all(new_ctx)   # project switched
        registry.stop_all()
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._order: list[str] = []

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, plugin: Plugin) -> None:
        """Register a plugin. Silently ignores duplicate IDs."""
        if plugin.id not in self._plugins:
            self._plugins[plugin.id] = plugin
            self._order.append(plugin.id)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def init_all(self, ctx: PluginContext) -> None:
        """Call :meth:`Plugin.init` on every registered plugin."""
        for pid in self._order:
            try:
                self._plugins[pid].init(ctx)
            except Exception:
                pass  # silent degradation

    def start_all(self) -> None:
        """Call :meth:`Plugin.start` on every registered plugin."""
        for pid in self._order:
            try:
                self._plugins[pid].start()
            except Exception:
                pass

    def stop_all(self) -> None:
        """Call :meth:`Plugin.stop` on every registered plugin."""
        for pid in self._order:
            try:
                self._plugins[pid].stop()
            except Exception:
                pass

    def reinit_all(self, ctx: PluginContext) -> None:
        """Re-init all plugins with a new context (project switch)."""
        for pid in self._order:
            try:
                self._plugins[pid].reinit(ctx)
            except Exception:
                pass

    # ── Queries ───────────────────────────────────────────────────────────────

    def get(self, plugin_id: str) -> Plugin | None:
        """Return the plugin with *plugin_id*, or ``None`` if not registered."""
        return self._plugins.get(plugin_id)

    def all_commands(self) -> list[dict[str, Any]]:
        """Collect command palette entries from all plugins.

        Each dict is guaranteed to have a ``plugin_id`` key injected if absent.
        """
        result: list[dict[str, Any]] = []
        for pid in self._order:
            try:
                cmds = self._plugins[pid].commands()
                for cmd in cmds:
                    cmd.setdefault("plugin_id", pid)
                result.extend(cmds)
            except Exception:
                pass
        return result

    @property
    def plugins(self) -> list[Plugin]:
        """All registered plugins in insertion order."""
        return [self._plugins[pid] for pid in self._order]

    def __len__(self) -> int:
        return len(self._plugins)

    def __contains__(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins
