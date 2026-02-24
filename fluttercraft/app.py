from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from fluttercraft.screens.dashboard import DashboardScreen
from fluttercraft.themes.theme_manager import ThemeDefinition, ThemeManager


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
        self._theme_manager = ThemeManager()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

    # ── Theme ─────────────────────────────────────────────────────────────────

    def action_cycle_theme(self) -> None:
        """Ctrl+T — advance to the next theme."""
        theme = self._theme_manager.next()
        self._apply_theme(theme)

    def _apply_theme(self, theme: ThemeDefinition) -> None:
        """Apply *theme* to all mounted widgets via inline styles."""
        # Screen background
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

            # Header
            header = screen.query_one(FlutterCraftHeader)
            header.styles.background = theme.bg_surface

            # Sidebar
            sidebar = screen.query_one(SidebarPanel)
            sidebar.styles.background = theme.bg_surface
            sidebar.styles.border = ("round", theme.border)

            # Resize handle
            handle = screen.query_one(ResizeHandle)
            handle.styles.background = theme.resize_handle

            # Content panel
            content = screen.query_one("#content-panel", Static)
            content.styles.background = theme.bg_surface
            content.styles.border = ("round", theme.border)

            # Output panel
            output = screen.query_one(OutputPanel)
            output.styles.background = theme.bg_overlay
            output.styles.border = ("round", theme.border)

            # Command input
            cmd = screen.query_one(CommandInput)
            cmd.styles.background = theme.bg

            # Footer
            footer = screen.query_one(FlutterCraftFooter)
            footer.styles.background = theme.footer_bg
            footer.styles.color = theme.footer_fg

            # Notify in output
            output.write_info(f"Theme: {theme.name}")

        except Exception:
            pass  # App may not be fully mounted yet

    @property
    def theme_manager(self) -> ThemeManager:
        """Expose the theme manager for external use (e.g. settings screen)."""
        return self._theme_manager
