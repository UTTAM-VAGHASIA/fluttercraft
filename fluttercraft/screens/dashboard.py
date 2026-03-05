from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.widget import Widget
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from fluttercraft.widgets.command_input import CommandInput
from fluttercraft.widgets.footer import FlutterCraftFooter
from fluttercraft.widgets.header import FlutterCraftHeader
from fluttercraft.widgets.output_panel import OutputPanel
from fluttercraft.widgets.resize_handle import (
    OutputResizeHandle,
    ResizeHandle,
    OUTPUT_DEFAULT,
    SIDEBAR_DEFAULT,
    _clamp_output,
    _clamp_sidebar,
)
from fluttercraft.widgets.sidebar import SidebarPanel

_WELCOME = """\
[bold #7aa2f7]⚡ FlutterCraft[/]  [dim #565f89]v0.2.0[/]

[#565f89]Your Flutter development command centre[/]

[dim #3b4261]──────────────────────────────────────[/]

  [dim #565f89]Press [/][bold #a9b1d6]1–7[/][dim #565f89] to open a plugin[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+P[/][dim #565f89] for the command palette[/]
  [dim #565f89]Press [/][bold #a9b1d6]Ctrl+T[/][dim #565f89] to switch themes[/]
  [dim #565f89]Press [/][bold #a9b1d6]?[/][dim #565f89] for help[/]
"""


class DashboardScreen(Screen):
    """Main FlutterCraft dashboard — sidebar + resize handle + content + output."""

    BINDINGS = [
        Binding("1", "select_plugin(1)", "FVM Manager",    show=False, priority=True),
        Binding("2", "select_plugin(2)", "Flutter",         show=False, priority=True),
        Binding("3", "select_plugin(3)", "Git Control",     show=False, priority=True),
        Binding("4", "select_plugin(4)", "Project Creator", show=False, priority=True),
        Binding("5", "select_plugin(5)", "File Browser",    show=False, priority=True),
        Binding("6", "select_plugin(6)", "Workspace",       show=False, priority=True),
        Binding("7", "select_plugin(7)", "CLI Adapters",    show=False, priority=True),
        Binding("escape",     "go_home",          "Home",            show=False, priority=True),
        Binding("ctrl+right", "grow_sidebar",    "Grow sidebar",    show=False),
        Binding("ctrl+left",  "shrink_sidebar",  "Shrink sidebar",  show=False),
        Binding("ctrl+up",    "grow_output",     "Grow output",     show=False),
        Binding("ctrl+down",  "shrink_output",   "Shrink output",   show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._sidebar_width: int = SIDEBAR_DEFAULT
        self._output_height: int = OUTPUT_DEFAULT
        self._active_plugin_id: str | None = None
        self._mounted_plugins: dict[str, Widget] = {}  # plugin_id → root widget

    def compose(self) -> ComposeResult:
        yield FlutterCraftHeader()
        with Horizontal(id="main-area"):
            yield SidebarPanel(id="sidebar")
            yield ResizeHandle(id="resize-handle")
            with Vertical(id="content-area"):
                yield Static(_WELCOME, id="content-panel")
                yield OutputResizeHandle(id="output-resize-handle")
                yield OutputPanel(id="output-panel")
        yield CommandInput(id="command-input")
        yield FlutterCraftFooter()

    def on_mount(self) -> None:
        self.query_one("#content-panel", Static).border_title = "Welcome"
        self.query_one(OutputPanel).styles.height = self._output_height

    # ── Plugin selection ──────────────────────────────────────────────────────

    def action_select_plugin(self, number: int) -> None:
        self.query_one(SidebarPanel).select(number)

    def action_go_home(self) -> None:
        """Escape / 0 — deselect the active plugin and return to the Welcome screen."""
        # Hide the active plugin widget
        if self._active_plugin_id and self._active_plugin_id in self._mounted_plugins:
            self._mounted_plugins[self._active_plugin_id].display = False
        self._active_plugin_id = None

        # Restore the welcome panel
        content = self.query_one("#content-panel", Static)
        content.update(_WELCOME)
        content.border_title = "Welcome"
        content.display = True

        # Deselect sidebar (0 = nothing selected)
        self.query_one(SidebarPanel).selected = 0

        # Reset footer context
        self.query_one(FlutterCraftFooter).set_context("")

        # Return focus to command input
        self.query_one(CommandInput).focus_input()

    def on_sidebar_panel_plugin_selected(
        self, event: SidebarPanel.PluginSelected
    ) -> None:
        """Handle sidebar plugin selection — load plugin UI or show placeholder."""
        # Hide the previously active plugin widget (if any)
        if self._active_plugin_id and self._active_plugin_id in self._mounted_plugins:
            self._mounted_plugins[self._active_plugin_id].display = False

        self._active_plugin_id = event.plugin_id

        # Try to load (or reveal) the plugin widget from the registry
        plugin_widget = self._try_load_plugin(event.plugin_id)

        content = self.query_one("#content-panel", Static)
        if plugin_widget is None:
            # No registered plugin — show placeholder
            content.display = True
            content.update(
                f"[bold #7aa2f7]{event.plugin_id.title()}[/] plugin\n\n"
                f"[dim #565f89]Coming soon — plugin will be loaded here[/]"
            )
            content.border_title = event.plugin_id.title()
        else:
            content.display = False

        # Update footer context
        footer = self.query_one(FlutterCraftFooter)
        footer.set_context(event.plugin_id)

        # Write to output panel
        output = self.query_one(OutputPanel)
        output.write_info(f"Switched to {event.plugin_id}")

    def _try_load_plugin(self, plugin_id: str) -> Widget | None:
        """Show a plugin widget in the content area.

        On first activation the plugin is composed and mounted.
        On subsequent activations the already-mounted widget is re-shown
        (avoids duplicate mounting and preserves widget state).

        Returns the root widget on success, or None if the plugin is not
        registered or produces no compose output.
        """
        try:
            registry = self.app.plugin_registry
            plugin = registry.get(plugin_id)
            if plugin is None:
                return None

            # Already mounted — just reveal it
            if plugin_id in self._mounted_plugins:
                widget = self._mounted_plugins[plugin_id]
                widget.display = True
                plugin.start()
                return widget

            # First time — compose and mount
            widgets = list(plugin.compose())
            if not widgets:
                return None
            content_area = self.query_one("#content-area", Vertical)
            for w in widgets:
                content_area.mount(w, before=self.query_one(OutputPanel))
            self._mounted_plugins[plugin_id] = widgets[0]
            plugin.start()
            return widgets[0]
        except Exception:
            return None

    # ── Command input ─────────────────────────────────────────────────────────

    def on_command_input_submitted(self, event: CommandInput.Submitted) -> None:
        """Handle command submission — route to slash handler or active plugin."""
        output = self.query_one(OutputPanel)
        output.write_cmd(event.value)
        self._route_command(event.value.strip())

    def _route_command(self, text: str) -> None:
        output = self.query_one(OutputPanel)

        # ── Plugin shortcut: 0 = home, 1–7 = switch plugin ───────────────────
        if len(text) == 1 and text.isdigit():
            n = int(text)
            if n == 0:
                self.action_go_home()
                return
            if 1 <= n <= 7:
                self.action_select_plugin(n)
                return

        # ── Built-in slash commands ────────────────────────────────────────────
        if text.startswith("/"):
            self._handle_slash(text, output)
            return

        # ── Delegate to the active plugin ─────────────────────────────────────
        if self._active_plugin_id:
            plugin = self.app.plugin_registry.get(self._active_plugin_id)
            if plugin is not None:
                try:
                    if plugin.handle_command(text):
                        return
                except Exception:
                    pass

        # ── Nothing handled it ────────────────────────────────────────────────
        output.write(f"Unknown command: {text}", "dim")
        output.write("Tip: use /help for built-in commands, or open a plugin panel first", "dim")

    def _handle_slash(self, cmd: str, output: OutputPanel) -> None:
        """Dispatch built-in slash commands."""
        parts = cmd.split(None, 1)
        name = parts[0].lower()

        if name == "/quit":
            self.app.action_quit()
        elif name == "/clear":
            output.clear()
        elif name == "/theme":
            self.app.action_cycle_theme()
        elif name == "/help":
            output.write_info("Built-in commands:")
            output.write("  /help   — show this message", "dim")
            output.write("  /clear  — clear the output panel", "dim")
            output.write("  /theme  — open theme picker", "dim")
            output.write("  /quit   — quit FlutterCraft", "dim")
            output.write_info("Navigation:")
            output.write("  0       — go back to Welcome screen", "dim")
            output.write("  1–7     — switch to plugin panel", "dim")
            output.write("  Esc     — go back to Welcome (press twice if input has text)", "dim")
            output.write_info("Plugin commands: open a plugin panel (1–7), then type e.g. 'flutter doctor'")
        else:
            output.write(f"Unknown slash command: {name}", "dim")
            output.write("Type /help for available commands", "dim")

    # ── Workspace project switching ───────────────────────────────────────────

    def on_workspace_widget_project_switched(self, event: Any) -> None:
        """When user switches project in Workspace — update file browser & git."""
        project = event.project
        output = self.query_one(OutputPanel)
        output.write_info(f"Project: {project.name}  ({project.path})")

        # Update file browser root if mounted
        if "files" in self._mounted_plugins:
            try:
                self._mounted_plugins["files"].set_root(project.path)
            except Exception:
                pass

        # Update git control working dir if mounted
        if "git" in self._mounted_plugins:
            try:
                self._mounted_plugins["git"]._check_repo_and_load()
            except Exception:
                pass

    # ── Sidebar resize ────────────────────────────────────────────────────────

    def on_resize_handle_resized(self, event: ResizeHandle.Resized) -> None:
        self._apply_sidebar_width(self._sidebar_width + event.delta)

    def action_grow_sidebar(self) -> None:
        """Ctrl+Right — widen the sidebar by 2 columns."""
        self._apply_sidebar_width(self._sidebar_width + 2)

    def action_shrink_sidebar(self) -> None:
        """Ctrl+Left — narrow the sidebar by 2 columns."""
        self._apply_sidebar_width(self._sidebar_width - 2)

    def _apply_sidebar_width(self, new_width: int) -> None:
        clamped = _clamp_sidebar(new_width)
        if clamped == self._sidebar_width:
            return
        self._sidebar_width = clamped
        self.query_one(SidebarPanel).styles.width = clamped

    # ── Output panel resize ───────────────────────────────────────────────────

    def on_output_resize_handle_resized(self, event: OutputResizeHandle.Resized) -> None:
        # Dragging up (negative delta) grows the output panel
        self._apply_output_height(self._output_height - event.delta)

    def action_grow_output(self) -> None:
        """Ctrl+Up — grow the output panel by 2 rows."""
        self._apply_output_height(self._output_height + 2)

    def action_shrink_output(self) -> None:
        """Ctrl+Down — shrink the output panel by 2 rows."""
        self._apply_output_height(self._output_height - 2)

    def _apply_output_height(self, new_height: int) -> None:
        clamped = _clamp_output(new_height)
        if clamped == self._output_height:
            return
        self._output_height = clamped
        self.query_one(OutputPanel).styles.height = clamped
