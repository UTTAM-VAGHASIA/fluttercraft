from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from fluttercraft.core.config import ConfigManager
from fluttercraft.core.events import EventBus
from fluttercraft.core.features import FeatureFlags
from fluttercraft.core.keymap import KeyBinding, KeymapRegistry
from fluttercraft.core.state import StateManager
from fluttercraft.plugins.base import PluginContext, PluginRegistry
from fluttercraft.plugins.flutter_commands import FlutterCommandsPlugin
from fluttercraft.plugins.fvm_manager import FvmManagerPlugin
from fluttercraft.plugins.git_control import GitControlPlugin
from fluttercraft.plugins.project_creator import ProjectCreatorPlugin
from fluttercraft.screens.dashboard import DashboardScreen
from fluttercraft.themes.theme_manager import ThemeDefinition, ThemeManager
from fluttercraft.widgets.notifications import Notifier


class FlutterCraftApp(App):
    """FlutterCraft TUI — Flutter development tool."""

    CSS_PATH = "themes/styles.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command Palette", show=False),
        Binding("ctrl+t", "cycle_theme", "Theme", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # ── Core infrastructure ────────────────────────────────────────────────
        self._config = ConfigManager()
        self._event_bus = EventBus()
        self._state = StateManager()
        self._theme_manager = ThemeManager()
        self._keymap = KeymapRegistry(self._config)
        self._feature_flags = FeatureFlags(self._config)
        self._plugin_registry = PluginRegistry()
        self._plugin_registry.register(FvmManagerPlugin())
        self._plugin_registry.register(FlutterCommandsPlugin())
        self._plugin_registry.register(GitControlPlugin())
        self._plugin_registry.register(ProjectCreatorPlugin())
        self.notifier = Notifier(self)

        # Register built-in global keybindings
        self._keymap.register_many([
            KeyBinding("ctrl+q", "quit", "Quit FlutterCraft"),
            KeyBinding("ctrl+p", "command_palette", "Open command palette"),
            KeyBinding("ctrl+t", "cycle_theme", "Cycle theme"),
        ])

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        ctx = PluginContext(
            work_dir="",
            project_root="",
            config=self._config,
            event_bus=self._event_bus,
            state=self._state,
            keymap=self._keymap,
        )
        self._plugin_registry.init_all(ctx)
        self._plugin_registry.start_all()
        self.push_screen(DashboardScreen())

    # ── Command palette ────────────────────────────────────────────────────────

    def action_command_palette(self) -> None:
        """Ctrl+P — open the global command palette."""
        if not self._feature_flags.is_enabled("command_palette"):
            return

        from fluttercraft.screens.command_palette import CommandPaletteScreen

        commands = self._plugin_registry.all_commands()
        commands += self._builtin_palette_commands()
        self.push_screen(
            CommandPaletteScreen(commands),
            self._on_palette_result,
        )

    def _builtin_palette_commands(self) -> list[dict]:
        """Built-in app-level commands always visible in the palette."""
        return [
            {
                "title": "Theme: Select theme",
                "description": "Ctrl+T — open theme picker",
                "plugin_id": "app",
                "action": self.action_cycle_theme,
            },
            {
                "title": "App: Quit FlutterCraft",
                "description": "Ctrl+Q",
                "plugin_id": "app",
                "action": self.action_quit,
            },
        ]

    def _on_palette_result(self, action) -> None:
        """Called when the command palette dismisses with a selected action."""
        if callable(action):
            try:
                action()
            except Exception:
                pass

    # ── Theme ─────────────────────────────────────────────────────────────────

    def action_cycle_theme(self) -> None:
        """Ctrl+T — open the theme picker overlay."""
        from fluttercraft.screens.theme_picker import ThemePickerScreen

        self.push_screen(
            ThemePickerScreen(
                themes=self._theme_manager._themes,
                active_index=self._theme_manager.active_index,
            ),
            self._on_theme_picked,
        )

    def _on_theme_picked(self, theme) -> None:
        """Called when ThemePickerScreen dismisses."""
        if theme is not None:
            self._theme_manager.set_by_name(theme.name)
            self._apply_theme(theme)

    def _apply_theme(self, theme: ThemeDefinition) -> None:
        """Apply *theme* to all mounted widgets via inline styles."""
        self.screen.styles.background = theme.bg

        try:
            from fluttercraft.widgets.command_input import CommandInput
            from fluttercraft.widgets.footer import FlutterCraftFooter
            from fluttercraft.widgets.header import FlutterCraftHeader
            from fluttercraft.widgets.output_panel import OutputPanel
            from fluttercraft.widgets.resize_handle import ResizeHandle
            from fluttercraft.widgets.sidebar import SidebarPanel
            from textual.widgets import Static

            screen = self.query_one(DashboardScreen)

            header = screen.query_one(FlutterCraftHeader)
            header.styles.background = theme.bg_surface

            sidebar = screen.query_one(SidebarPanel)
            sidebar.styles.background = theme.bg_surface
            sidebar.styles.border = ("round", theme.border)

            handle = screen.query_one(ResizeHandle)
            handle.styles.background = theme.resize_handle

            content = screen.query_one("#content-panel", Static)
            content.styles.background = theme.bg_surface
            content.styles.border = ("round", theme.border)

            output = screen.query_one(OutputPanel)
            output.styles.background = theme.bg_overlay
            output.styles.border = ("round", theme.border)

            cmd = screen.query_one(CommandInput)
            cmd.styles.background = theme.bg

            footer = screen.query_one(FlutterCraftFooter)
            footer.styles.background = theme.footer_bg
            footer.styles.color = theme.footer_fg

            output.write_info(f"Theme: {theme.name}")

        except Exception:
            if self.is_running:
                self.log.warning("Theme application failed — widgets may not be mounted")

    # ── Notifications ─────────────────────────────────────────────────────────

    def notify_toast(
        self,
        message: str,
        level: str = "info",
        timeout: float = 4.0,
    ) -> None:
        """Show a toast notification on the current screen.

        Levels: ``"info"`` · ``"success"`` · ``"warning"`` · ``"error"``
        """
        if self._feature_flags.is_enabled("notifications"):
            self.notifier.notify(message, level=level, timeout=timeout)

    # ── Properties (read-only access for screens / plugins) ───────────────────

    @property
    def plugin_registry(self) -> PluginRegistry:
        return self._plugin_registry

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def config(self) -> ConfigManager:
        return self._config

    @property
    def state(self) -> StateManager:
        return self._state

    @property
    def keymap(self) -> KeymapRegistry:
        return self._keymap

    @property
    def feature_flags(self) -> FeatureFlags:
        return self._feature_flags

    @property
    def theme_manager(self) -> ThemeManager:
        return self._theme_manager
