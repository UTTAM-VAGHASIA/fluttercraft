from __future__ import annotations

import os
import time
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.workspace.workspace_api import (
    FlutterProject,
    ProjectHealth,
    add_project,
    check_project_health,
    default_config_path,
    default_scan_roots,
    discover_projects,
    get_recent_projects,
    load_workspace,
    remove_project,
    save_workspace,
    touch_project,
)


# ── Workspace Widget ──────────────────────────────────────────────────────────


class WorkspaceWidget(Widget):
    """Multi-project workspace manager.

    Left panel: project list (↑↓ navigate, Enter switch).
    Right panel: project details and health.
    """

    can_focus = True

    # ── Message posted when user switches active project ─────────────────────

    class ProjectSwitched(Message):
        """Posted when the user activates a different project."""

        def __init__(self, project: FlutterProject) -> None:
            self.project = project
            super().__init__()

    DEFAULT_CSS = """
    WorkspaceWidget { height: 1fr; layout: vertical; }
    #ws-header-bar {
        height: 1; background: #16161e; color: #7aa2f7;
        padding: 0 1; border-bottom: solid #3b4261;
    }
    #ws-body { height: 1fr; }
    #ws-left {
        width: 35; height: 1fr; background: #1f2335; border-right: solid #3b4261;
        overflow: hidden auto;
    }
    #ws-list { height: auto; padding: 0 1; }
    #ws-right { height: 1fr; background: #16161e; padding: 1 1; overflow-y: auto; }
    #ws-detail { height: auto; color: #a9b1d6; }
    #ws-status-bar {
        height: 1; background: #1f2335; color: #565f89;
        padding: 0 1; border-top: solid #3b4261;
    }
    #ws-footer {
        height: 1; background: #16161e; color: #565f89; padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("up",    "list_up",         "Up",      show=False, priority=True),
        Binding("down",  "list_down",        "Down",    show=False, priority=True),
        Binding("enter", "switch_project",   "Switch",  show=True),
        Binding("a",     "add_project",      "Add",     show=True),
        Binding("d",     "remove_project",   "Remove",  show=True),
        Binding("s",     "scan_projects",    "Scan",    show=True),
        Binding("h",     "check_health",     "Health",  show=True),
        Binding("t",     "set_theme",        "Theme",   show=True),
        Binding("R",     "refresh",          "Refresh", show=False),
    ]

    def __init__(self, config_path: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._config_path = config_path or default_config_path()
        self._projects: list[FlutterProject] = []
        self._cursor: int = 0
        self._active_path: str = ""
        self._health: ProjectHealth | None = None
        self._scanning: bool = False

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="ws-header-bar")
        with Horizontal(id="ws-body"):
            with Vertical(id="ws-left"):
                yield Static("", id="ws-list")
            with Vertical(id="ws-right"):
                yield Static("", id="ws-detail")
        yield Static("", id="ws-status-bar")
        yield Static(
            "[dim]↑↓[/] nav  [dim]Enter[/] switch  [dim]a[/] add  [dim]d[/] remove  "
            "[dim]s[/] scan  [dim]h[/] health  [dim]t[/] theme  [dim]R[/] refresh",
            id="ws-footer",
        )

    def on_mount(self) -> None:
        self._worker_load()
        self.set_timer(0.1, self.focus)

    # ── Workers ───────────────────────────────────────────────────────────────

    @work(thread=True)
    def _worker_load(self) -> None:
        projects, last_active = load_workspace(self._config_path)
        self.app.call_from_thread(self._apply_projects, projects, last_active)

    def _apply_projects(self, projects: list[FlutterProject], last_active: str = "") -> None:
        self._projects = projects
        # Restore last active project
        if last_active:
            self._active_path = last_active
            for i, p in enumerate(projects):
                if p.path == last_active:
                    self._cursor = i
                    break
        self._cursor = min(self._cursor, max(0, len(projects) - 1))
        self._render_all()
        # Notify app of restored active project
        if last_active and projects:
            proj = next((p for p in projects if p.path == last_active), None)
            if proj:
                self.post_message(self.ProjectSwitched(proj))
        # Auto-scan on first run
        if not projects:
            self._scanning = True
            self._render_header()
            self._worker_scan()

    @work(thread=True)
    def _worker_scan(self) -> None:
        roots = default_scan_roots()
        found = discover_projects(roots)
        self.app.call_from_thread(self._apply_scan_results, found)

    def _apply_scan_results(self, found: list[FlutterProject]) -> None:
        self._scanning = False
        added = 0
        existing_paths = {p.path for p in self._projects}
        for proj in found:
            if proj.path not in existing_paths:
                self._projects.append(proj)
                added += 1
        save_workspace(self._projects, self._config_path, last_active=self._active_path)
        self._render_all()
        self._set_status(f"Scan complete — {added} new project(s) found")

    @work(thread=True)
    def _worker_health(self, path: str) -> None:
        health = check_project_health(path)
        self.app.call_from_thread(self._apply_health, health)

    def _apply_health(self, health: ProjectHealth) -> None:
        self._health = health
        self._render_detail()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_all(self) -> None:
        self._render_header()
        self._render_list()
        self._render_detail()

    def _render_header(self) -> None:
        count = len(self._projects)
        active = f"  [dim #565f89]active: {os.path.basename(self._active_path)}[/]" if self._active_path else ""
        scan = "  [#e0af68]Scanning…[/]" if self._scanning else ""
        bar = f"[bold #7aa2f7]● Workspace[/]  [dim #565f89]{count} project(s)[/]{active}{scan}"
        self.query_one("#ws-header-bar", Static).update(bar)

    def _render_list(self) -> None:
        if not self._projects:
            self.query_one("#ws-list", Static).update(
                "\n[dim #565f89]No projects yet.\n\n"
                "Press [bold]a[/bold] to add or [bold]s[/bold] to scan.[/]"
            )
            return

        recent = {p.path for p in get_recent_projects(self._projects, 3)}
        lines: list[str] = []
        for i, proj in enumerate(self._projects):
            is_cursor = i == self._cursor
            is_active = proj.path == self._active_path
            is_recent = proj.path in recent

            # Status badge
            if is_active:
                badge = " [bold #9ece6a]●[/]"
            elif is_recent:
                badge = " [dim #565f89]·[/]"
            else:
                badge = ""

            # Flutter version indicator
            ver = proj.flutter_version or "system"
            ver_color = "#7dcfff" if ver != "system" else "#565f89"

            if is_cursor:
                line = (
                    f"[bold reverse #c0caf5] {proj.name} [/]{badge}\n"
                    f"  [dim {ver_color}]{ver}[/]"
                )
            else:
                name_color = "#9ece6a" if is_active else "#a9b1d6"
                line = (
                    f"[{name_color}] {proj.name}[/]{badge}\n"
                    f"  [dim {ver_color}]{ver}[/]"
                )
            lines.append(line)

        self.query_one("#ws-list", Static).update("\n".join(lines))

    def _render_detail(self) -> None:
        detail = self.query_one("#ws-detail", Static)
        if not self._projects or self._cursor >= len(self._projects):
            detail.update("[dim #565f89]Select a project to view details.[/]")
            return

        proj = self._projects[self._cursor]
        is_active = proj.path == self._active_path
        active_badge = " [bold #9ece6a](active)[/]" if is_active else ""

        import datetime
        last = (
            datetime.datetime.fromtimestamp(proj.last_opened).strftime("%Y-%m-%d %H:%M")
            if proj.last_opened > 0
            else "never"
        )

        lines: list[str] = [
            f"[bold #7aa2f7]{proj.name}[/]{active_badge}",
            "",
            f"  [dim]Path:[/]         [#a9b1d6]{proj.path}[/]",
            f"  [dim]Flutter:[/]      [#7dcfff]{proj.flutter_version or 'system'}[/]",
            f"  [dim]Last opened:[/]  [#565f89]{last}[/]",
            f"  [dim]Theme:[/]        [#bb9af7]{proj.theme_override or '(app default)'}[/]",
            f"  [dim]Plugin:[/]       [#565f89]{proj.active_plugin or '(none)'}[/]",
            "",
        ]

        if self._health:
            h = self._health
            pubspec_icon = "[#9ece6a]✓[/]" if h.has_pubspec else "[#f7768e]✗[/]"
            flutter_icon = "[#9ece6a]✓[/]" if h.flutter_on_path else "[#f7768e]✗[/]"
            fvm_info = f" [#7dcfff](FVM: {h.fvm_version})[/]" if h.fvm_version and h.fvm_version != "system" else ""
            dart_info = f" dart {h.dart_sdk}" if h.dart_sdk else ""

            lines += [
                "[bold #7aa2f7]Health[/]",
                "",
                f"  {pubspec_icon} pubspec.yaml",
                f"  {flutter_icon} flutter on PATH{dart_info}{fvm_info}",
                "",
                "[dim]Press [bold]h[/bold] to re-check health[/]",
            ]
        else:
            lines.append("[dim #565f89]Press [bold]h[/bold] to check project health[/]")

        detail.update("\n".join(lines))

    def _set_status(self, msg: str, error: bool = False) -> None:
        color = "#f7768e" if error else "#565f89"
        try:
            self.query_one("#ws-status-bar", Static).update(
                f"[{color}]{msg}[/]"
            )
        except Exception:
            pass

    # ── Navigation ────────────────────────────────────────────────────────────

    def action_list_up(self) -> None:
        if self._cursor > 0:
            self._cursor -= 1
            self._health = None
            self._render_list()
            self._render_detail()

    def action_list_down(self) -> None:
        if self._cursor < len(self._projects) - 1:
            self._cursor += 1
            self._health = None
            self._render_list()
            self._render_detail()

    # ── Project switching ─────────────────────────────────────────────────────

    def action_switch_project(self) -> None:
        if not self._projects or self._cursor >= len(self._projects):
            return
        proj = self._projects[self._cursor]
        if not os.path.isdir(proj.path):
            self._set_status(f"Directory not found: {proj.path}", error=True)
            return
        self._active_path = proj.path
        touch_project(self._projects, proj.path)
        save_workspace(self._projects, self._config_path, last_active=proj.path)
        self._render_all()
        self._set_status(f"Switched to: {proj.name}")
        # Notify the rest of the app
        self.post_message(self.ProjectSwitched(proj))

    # ── Add project ───────────────────────────────────────────────────────────

    def action_add_project(self) -> None:
        from textual.screen import ModalScreen
        from textual.widgets import Input, Label
        from textual.containers import Vertical

        class _AddModal(ModalScreen):
            DEFAULT_CSS = """
            _AddModal { align: center middle; }
            _AddModal > Vertical {
                width: 70; height: auto;
                background: #1f2335; border: round #7aa2f7; padding: 1 2;
            }
            _AddModal Label { color: #c0caf5; margin-bottom: 1; }
            _AddModal Input { margin-bottom: 1; }
            """
            def compose(self) -> ComposeResult:
                with Vertical():
                    yield Label("[bold #7aa2f7]Add Project[/]")
                    yield Input(
                        placeholder="/path/to/flutter/project",
                        id="add-input",
                    )
                    yield Label("[dim]Enter to confirm · Escape to cancel[/]")
            def on_mount(self) -> None:
                self.query_one("#add-input", Input).focus()
            def on_input_submitted(self, event: Input.Submitted) -> None:
                self.dismiss(event.value.strip())
            def on_key(self, event: Any) -> None:
                if event.key == "escape":
                    self.dismiss(None)

        self.app.push_screen(_AddModal(), self._on_add_result)

    def _on_add_result(self, path: str | None) -> None:
        if path:
            proj, err = add_project(self._projects, path)
            if err:
                self._set_status(err, error=True)
            else:
                save_workspace(self._projects, self._config_path, last_active=self._active_path)
                self._cursor = len(self._projects) - 1
                self._render_all()
                self._set_status(f"Added: {proj.name}")  # type: ignore[union-attr]
        self.set_timer(0.05, self.focus)

    # ── Remove project ────────────────────────────────────────────────────────

    def action_remove_project(self) -> None:
        if not self._projects or self._cursor >= len(self._projects):
            return
        proj = self._projects[self._cursor]
        from textual.screen import ModalScreen
        from textual.widgets import Label
        from textual.containers import Vertical

        class _ConfirmRemove(ModalScreen):
            DEFAULT_CSS = """
            _ConfirmRemove { align: center middle; }
            _ConfirmRemove > Vertical {
                width: 60; height: auto;
                background: #1f2335; border: round #f7768e; padding: 1 2;
            }
            _ConfirmRemove Label { color: #c0caf5; margin-bottom: 1; }
            """
            def __init__(self, name: str, **kw: Any) -> None:
                super().__init__(**kw)
                self._name = name
            def compose(self) -> ComposeResult:
                with Vertical():
                    yield Label("[bold #f7768e]Remove from workspace?[/]")
                    yield Label(f"[#a9b1d6]{self._name}[/]")
                    yield Label("[dim](files are NOT deleted)[/]")
                    yield Label("[dim]y/Enter = yes · n/Escape = cancel[/]")
            def on_mount(self) -> None:
                self.focus()
            def on_key(self, event: Any) -> None:
                if event.key in ("y", "enter"):
                    self.dismiss(True)
                elif event.key in ("n", "escape"):
                    self.dismiss(False)

        self.app.push_screen(
            _ConfirmRemove(proj.name),
            lambda confirmed: self._on_remove_confirm(confirmed, proj.path),
        )

    def _on_remove_confirm(self, confirmed: bool | None, path: str) -> None:
        if confirmed:
            name = next(
                (p.name for p in self._projects if p.path == path), path
            )
            self._projects = remove_project(self._projects, path)
            if self._active_path == path:
                self._active_path = ""
            save_workspace(self._projects, self._config_path, last_active=self._active_path)
            self._cursor = min(self._cursor, max(0, len(self._projects) - 1))
            self._render_all()
            self._set_status(f"Removed: {name}")
        self.set_timer(0.05, self.focus)

    # ── Scan ──────────────────────────────────────────────────────────────────

    def action_scan_projects(self) -> None:
        self._scanning = True
        self._render_header()
        self._set_status("Scanning for Flutter projects…")
        self._worker_scan()

    # ── Health check ──────────────────────────────────────────────────────────

    def action_check_health(self) -> None:
        if not self._projects or self._cursor >= len(self._projects):
            return
        proj = self._projects[self._cursor]
        self._set_status(f"Checking health for {proj.name}…")
        self._worker_health(proj.path)

    # ── Per-project theme ─────────────────────────────────────────────────────

    def action_set_theme(self) -> None:
        if not self._projects or self._cursor >= len(self._projects):
            return
        proj = self._projects[self._cursor]

        from textual.screen import ModalScreen
        from textual.widgets import Input, Label
        from textual.containers import Vertical

        class _ThemeModal(ModalScreen):
            DEFAULT_CSS = """
            _ThemeModal { align: center middle; }
            _ThemeModal > Vertical {
                width: 60; height: auto;
                background: #1f2335; border: round #bb9af7; padding: 1 2;
            }
            _ThemeModal Label { color: #c0caf5; margin-bottom: 1; }
            _ThemeModal Input { margin-bottom: 1; }
            """
            def __init__(self, current: str, **kw: Any) -> None:
                super().__init__(**kw)
                self._current = current
            def compose(self) -> ComposeResult:
                with Vertical():
                    yield Label("[bold #bb9af7]Per-Project Theme[/]")
                    yield Input(
                        value=self._current,
                        placeholder="theme name, or empty for app default",
                        id="theme-input",
                    )
                    yield Label("[dim]Enter to confirm · Escape to cancel[/]")
            def on_mount(self) -> None:
                self.query_one("#theme-input", Input).focus()
            def on_input_submitted(self, event: Input.Submitted) -> None:
                self.dismiss(event.value.strip())
            def on_key(self, event: Any) -> None:
                if event.key == "escape":
                    self.dismiss(None)

        self.app.push_screen(
            _ThemeModal(proj.theme_override),
            lambda theme: self._on_theme_set(theme, proj.path),
        )

    def _on_theme_set(self, theme: str | None, path: str) -> None:
        if theme is not None:
            for p in self._projects:
                if p.path == path:
                    p.theme_override = theme
                    break
            save_workspace(self._projects, self._config_path, last_active=self._active_path)
            self._render_detail()
            label = theme if theme else "(cleared)"
            self._set_status(f"Theme override: {label}")
        self.set_timer(0.05, self.focus)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self._health = None
        self._worker_load()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_active_project(self, path: str) -> None:
        """Mark *path* as the active project without switching."""
        self._active_path = path
        self._render_all()

    def save_plugin_state(self, project_path: str, plugin_id: str) -> None:
        """Record the last active plugin for a project."""
        for p in self._projects:
            if p.path == project_path:
                p.active_plugin = plugin_id
                save_workspace(self._projects, self._config_path, last_active=self._active_path)
                return


# ── Workspace Plugin ──────────────────────────────────────────────────────────


class WorkspacePlugin(Plugin):
    """Phase 8 — Workspace Manager plugin (plugin ID ``"workspace"``)."""

    def __init__(self) -> None:
        self._widget: WorkspaceWidget | None = None

    @property
    def id(self) -> str:
        return "workspace"

    @property
    def name(self) -> str:
        return "Workspace"

    @property
    def icon(self) -> str:
        return "◈"

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)

    def compose(self) -> ComposeResult:
        self._widget = WorkspaceWidget(id="workspace-widget")
        yield self._widget

    def commands(self) -> list[dict]:
        return [
            {
                "title": "Workspace: Add project",
                "description": "Add a Flutter project to the workspace",
                "plugin_id": "workspace",
                "action": self._cmd_add,
            },
            {
                "title": "Workspace: Scan for projects",
                "description": "Auto-discover Flutter projects in common directories",
                "plugin_id": "workspace",
                "action": self._cmd_scan,
            },
            {
                "title": "Workspace: Switch project",
                "description": "Switch the active project",
                "plugin_id": "workspace",
                "action": self._cmd_switch,
            },
        ]

    def _call(self, method: str, *args: Any) -> None:
        if self._widget:
            try:
                getattr(self._widget, method)(*args)
            except Exception:
                pass

    def _cmd_add(self) -> None:
        self._call("action_add_project")

    def _cmd_scan(self) -> None:
        self._call("action_scan_projects")

    def _cmd_switch(self) -> None:
        self._call("action_switch_project")

    def handle_command(self, text: str) -> bool:
        """Route commands from the bottom input.

        Accepted:
            ``add <path>``         — add project
            ``switch <n>``         — switch to project #n (1-based)
            ``switch <name>``      — switch to project by name
            ``scan``               — scan for projects
            ``health``             — check health of current project
        """
        parts = text.strip().split(None, 1)
        if not parts:
            return False
        cmd = parts[0].lower()

        if cmd == "add" and len(parts) == 2:
            if self._widget:
                proj, err = add_project(self._widget._projects, parts[1])
                if not err and self._widget:
                    save_workspace(
                        self._widget._projects,
                        self._widget._config_path,
                        last_active=self._widget._active_path,
                    )
                    self._widget._cursor = len(self._widget._projects) - 1
                    self._widget._render_all()
            return True

        if cmd == "switch" and len(parts) == 2:
            if self._widget:
                arg = parts[1]
                # numeric index
                if arg.isdigit():
                    idx = int(arg) - 1
                    if 0 <= idx < len(self._widget._projects):
                        self._widget._cursor = idx
                        self._widget.action_switch_project()
                else:
                    # match by name
                    for i, p in enumerate(self._widget._projects):
                        if arg.lower() in p.name.lower():
                            self._widget._cursor = i
                            self._widget.action_switch_project()
                            break
            return True

        if cmd == "scan":
            self._call("action_scan_projects")
            return True

        if cmd == "health":
            self._call("action_check_health")
            return True

        return False
