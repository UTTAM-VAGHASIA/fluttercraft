from __future__ import annotations

import subprocess
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, RichLog, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.flutter_commands.flutter_api import (
    colorize_analyze_line,
    colorize_doctor_line,
    colorize_test_line,
    esc,
    get_flutter_version,
    is_flutter_installed,
    run_flutter_streaming,
    start_flutter_run,
)


# ── Build platform modal ───────────────────────────────────────────────────────

_BUILD_PLATFORMS = ["apk", "appbundle", "ipa", "web", "linux", "windows", "macos"]


class _PlatformModal(ModalScreen):
    """Pick a build target platform."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False, priority=True),
        Binding("up",     "cursor_up",   "Up",   show=False, priority=True),
        Binding("down",   "cursor_down", "Down", show=False, priority=True),
        Binding("enter",  "select",      "Select", show=False, priority=True),
    ]

    DEFAULT_CSS = """
    _PlatformModal { align: center middle; }
    _PlatformModal > Vertical {
        width: 38; height: auto;
        background: #1f2335; border: round #7aa2f7; padding: 1 2;
    }
    #pm-title { text-align: center; color: #7aa2f7; text-style: bold; padding-bottom: 1; width: 1fr; }
    #pm-list  { height: auto; width: 1fr; }
    #pm-hint  { color: #565f89; text-align: center; padding-top: 1; width: 1fr; }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cursor = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("⚡ Build Platform", id="pm-title")
            yield Static(self._render(), id="pm-list")
            yield Static("[dim]↑↓ navigate  Enter select  Esc cancel[/]", id="pm-hint")

    def _render(self) -> str:
        lines = []
        for i, p in enumerate(_BUILD_PLATFORMS):
            if i == self._cursor:
                lines.append(f" [bold #7aa2f7]▶  {p}[/]")
            else:
                lines.append(f"   [#a9b1d6]{p}[/]")
        return "\n".join(lines)

    def _refresh(self) -> None:
        try:
            self.query_one("#pm-list", Static).update(self._render())
        except Exception:
            pass

    def action_cursor_up(self) -> None:
        self._cursor = (self._cursor - 1) % len(_BUILD_PLATFORMS)
        self._refresh()

    def action_cursor_down(self) -> None:
        self._cursor = (self._cursor + 1) % len(_BUILD_PLATFORMS)
        self._refresh()

    def action_select(self) -> None:
        self.dismiss(_BUILD_PLATFORMS[self._cursor])

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Create project modal ──────────────────────────────────────────────────────


class _CreateModal(ModalScreen):
    """Enter a project name for ``flutter create``."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False, priority=True)]

    DEFAULT_CSS = """
    _CreateModal { align: center middle; }
    _CreateModal > Vertical {
        width: 52; height: auto;
        background: #1f2335; border: round #7aa2f7; padding: 1 2;
    }
    #cm-title { text-align: center; color: #7aa2f7; text-style: bold; padding-bottom: 1; width: 1fr; }
    #cm-hint  { color: #565f89; margin-bottom: 1; width: 1fr; }
    #cm-input { margin-bottom: 1; }
    #cm-btns  { height: auto; align-horizontal: center; }
    #cm-btns Button { margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("⚡ Create Flutter Project", id="cm-title")
            yield Static("[dim]Enter a project name (snake_case):[/]", id="cm-hint")
            yield Input(placeholder="e.g. my_app", id="cm-input")
            with Center(id="cm-btns"):
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#cm-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.label) == "Create":
            value = self.query_one("#cm-input", Input).value.strip()
            self.dismiss(value or None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Flutter commands widget ───────────────────────────────────────────────────

_CATEGORIES: list[tuple[str, str]] = [
    ("doctor",        "flutter doctor"),
    ("upgrade",       "flutter upgrade"),
    ("devices",       "flutter devices"),
    ("run",           "flutter run  (interactive)"),
    ("build",         "flutter build [platform]"),
    ("test",          "flutter test"),
    ("analyze",       "flutter analyze"),
    ("pub get",       "flutter pub get"),
    ("pub upgrade",   "flutter pub upgrade"),
    ("pub outdated",  "flutter pub outdated"),
    ("clean",         "flutter clean"),
    ("create",        "flutter create"),
]

_CMD_ARGS: dict[str, list[str]] = {
    "doctor":       ["doctor"],
    "upgrade":      ["upgrade"],
    "devices":      ["devices"],
    "test":         ["test"],
    "analyze":      ["analyze"],
    "pub get":      ["pub", "get"],
    "pub upgrade":  ["pub", "upgrade"],
    "pub outdated": ["pub", "outdated"],
    "clean":        ["clean"],
}

_COLORIZERS = {
    "doctor":  colorize_doctor_line,
    "analyze": colorize_analyze_line,
    "test":    colorize_test_line,
}


class FlutterCommandsWidget(Widget):
    """Flutter command runner panel.

    Layout::

        ┌─ status bar ──────────────────────────────────────────────────────┐
        │ ✓ Flutter 3.x  |  ↑↓ navigate · Enter run · s stop               │
        ├─ left (30) ─────────────────┬─ right (1fr) ─────────────────────┤
        │  ▶  doctor                  │ Output                             │
        │     upgrade                 │                                    │
        │     devices                 │                                    │
        │     run                     │                                    │
        │     ...                     │                                    │
        └─────────────────────────────┴────────────────────────────────────┘

    Keys:
        ↑↓     — navigate categories
        Enter  — execute selected category
        s      — stop any running process
        r / R  — hot reload / hot restart (only during flutter run)
    """

    can_focus = True

    DEFAULT_CSS = """
    FlutterCommandsWidget {
        height: 1fr;
        layout: vertical;
    }
    #fl-status {
        height: 1;
        background: #16161e;
        color: #7aa2f7;
        padding: 0 1;
        border-bottom: solid #3b4261;
    }
    #fl-body  { height: 1fr; }
    #fl-left  { width: 30; background: #1f2335; border-right: solid #3b4261; }
    #fl-list  { height: 1fr; background: #1f2335; padding: 1 1; }
    #fl-keys  { height: auto; color: #565f89; padding: 0 1 1 1; border-top: solid #3b4261; }
    #fl-right { height: 1fr; background: #16161e; }
    #fl-output {
        height: 1fr;
        background: #16161e;
        color: #a9b1d6;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("up",    "cursor_up",    "Up",     show=False, priority=True),
        Binding("down",  "cursor_down",  "Down",   show=False, priority=True),
        Binding("enter", "run_selected", "Run",    show=True),
        Binding("s",     "stop_proc",    "Stop",   show=True),
        Binding("r",     "hot_reload",   "Reload", show=False),
        Binding("R",     "hot_restart",  "Restart", show=False),
    ]

    def __init__(self, project_root: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._project_root = project_root
        self._cursor: int = 0
        self._active_proc: subprocess.Popen | None = None
        self._run_mode: bool = False  # True when flutter run is active

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="fl-status")
        with Horizontal(id="fl-body"):
            with Vertical(id="fl-left"):
                yield Static("", id="fl-list")
                yield Static(
                    "[dim]↑↓[/] navigate  [dim]Enter[/] run\n"
                    "[dim]s[/] stop  [dim]r[/] reload  [dim]R[/] restart",
                    id="fl-keys",
                )
            with Vertical(id="fl-right"):
                yield RichLog(id="fl-output", markup=True, highlight=False, wrap=True)

    def on_mount(self) -> None:
        self._render_list()
        self._load_status()
        self.focus()

    # ── Initial status load ───────────────────────────────────────────────────

    @work(thread=True)
    def _load_status(self) -> None:
        installed = is_flutter_installed()
        version = get_flutter_version() if installed else None
        self.app.call_from_thread(self._apply_status, installed, version)

    def _apply_status(self, installed: bool, version: str | None) -> None:
        if installed:
            ver = version or "unknown"
            self.query_one("#fl-status", Static).update(
                f"[#9ece6a]✓[/] Flutter [bold]{ver}[/]  "
                "[dim #565f89]↑↓ navigate · Enter run · s stop · r reload · R restart[/]"
            )
        else:
            self.query_one("#fl-status", Static).update(
                "[#f7768e]✗[/] Flutter not found  "
                "[dim #565f89]Install Flutter SDK from flutter.dev[/]"
            )
            self._log("[#f7768e]Flutter SDK not found on PATH.[/]")
            self._log("")
            self._log("[#a9b1d6]Install from:[/]  [#7aa2f7]https://flutter.dev/docs/get-started/install[/]")

    # ── Category list rendering ───────────────────────────────────────────────

    def _render_list(self) -> None:
        lines: list[str] = []
        for i, (name, desc) in enumerate(_CATEGORIES):
            if i == self._cursor:
                lines.append(
                    f" [bold #7aa2f7]▶  {name:<14}[/]  "
                    f"[dim #565f89]{desc}[/]"
                )
            else:
                lines.append(
                    f"    [#a9b1d6]{name:<14}[/]  "
                    f"[dim #3b4261]{desc}[/]"
                )
        try:
            self.query_one("#fl-list", Static).update("\n".join(lines))
        except Exception:
            pass

    # ── Navigation ────────────────────────────────────────────────────────────

    def action_cursor_up(self) -> None:
        self._cursor = (self._cursor - 1) % len(_CATEGORIES)
        self._render_list()

    def action_cursor_down(self) -> None:
        self._cursor = (self._cursor + 1) % len(_CATEGORIES)
        self._render_list()

    # ── Command execution ─────────────────────────────────────────────────────

    def action_run_selected(self) -> None:
        """Enter — execute the currently highlighted category."""
        if self._active_proc is not None:
            self._log("[#e0af68]⚠ A command is already running. Press [bold]s[/] to stop it.[/]")
            return
        name = _CATEGORIES[self._cursor][0]
        self._dispatch(name)

    def _dispatch(self, name: str, extra: str = "") -> None:
        """Route *name* to the correct execution path."""
        if name == "run":
            self._start_run_mode()
        elif name == "build":
            self.app.push_screen(_PlatformModal(), self._on_platform_chosen)
        elif name == "create":
            self.app.push_screen(_CreateModal(), self._on_create_name)
        elif name in _CMD_ARGS:
            args = _CMD_ARGS[name]
            self._run_streaming(name, args)
        else:
            self._log(f"[#e0af68]Unknown command: {name}[/]")

    def _on_platform_chosen(self, platform: str | None) -> None:
        if platform:
            self._run_streaming("build", ["build", platform])

    def _on_create_name(self, name: str | None) -> None:
        if name:
            self._run_streaming("create", ["create", name])

    # ── Streaming runner (doctor, upgrade, test, analyze, pub, clean, etc.) ───

    @work(thread=True)
    def _run_streaming(self, cmd_name: str, args: list[str]) -> None:
        colorizer = _COLORIZERS.get(cmd_name)
        cwd = self._project_root or None

        self.app.call_from_thread(self._clear_output)
        self.app.call_from_thread(
            self._log, f"[bold #7aa2f7]$ flutter {' '.join(args)}[/]"
        )
        self.app.call_from_thread(self._log, "")

        def on_line(line: str) -> None:
            if colorizer:
                markup = colorizer(line)
            else:
                markup = f"[#a9b1d6]{esc(line)}[/]"
            self.app.call_from_thread(self._log, markup)

        ok = run_flutter_streaming(args, cwd=cwd, on_line=on_line)
        status = "[#9ece6a]✓ Done[/]" if ok else "[#f7768e]✗ Failed[/]"
        self.app.call_from_thread(self._log, "")
        self.app.call_from_thread(self._log, status)

    # ── Flutter run mode ──────────────────────────────────────────────────────

    def _start_run_mode(self, extra_args: list[str] | None = None) -> None:
        self._clear_output()
        self._log("[bold #7aa2f7]$ flutter run[/]")
        self._log("[dim #565f89]Starting… press [bold]r[/] to hot reload, [bold]R[/] to restart, [bold]s[/] to stop[/]")
        self._log("")

        proc = start_flutter_run(extra_args=extra_args, cwd=self._project_root or None)
        if proc is None:
            self._log("[#f7768e]✗ flutter not found — is Flutter SDK installed?[/]")
            return

        self._active_proc = proc
        self._run_mode = True
        self._update_run_status()
        self._stream_run_output()

    @work(thread=True)
    def _stream_run_output(self) -> None:
        """Worker thread — reads flutter run stdout until process exits."""
        proc = self._active_proc
        if proc is None or proc.stdout is None:
            return
        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            self.app.call_from_thread(self._log, f"[#a9b1d6]{esc(line)}[/]")
        proc.wait()
        self.app.call_from_thread(self._on_run_finished, proc.returncode)

    def _on_run_finished(self, returncode: int) -> None:
        self._active_proc = None
        self._run_mode = False
        status = "[#9ece6a]✓ flutter run exited[/]" if returncode == 0 else f"[#f7768e]✗ flutter run exited (code {returncode})[/]"
        self._log("")
        self._log(status)
        self._update_run_status()

    def _update_run_status(self) -> None:
        try:
            if self._run_mode:
                self.query_one("#fl-status", Static).update(
                    "[bold #9ece6a]● RUNNING[/]  flutter run  "
                    "[dim #565f89]r=hotreload · R=restart · s=stop[/]"
                )
            else:
                self._load_status()
        except Exception:
            pass

    def _send_to_proc(self, char: str) -> None:
        """Write *char* + newline to the running process stdin."""
        if self._active_proc and self._active_proc.stdin:
            try:
                self._active_proc.stdin.write(char + "\n")
                self._active_proc.stdin.flush()
            except Exception:
                pass

    # ── Interactive keys for flutter run ─────────────────────────────────────

    def action_hot_reload(self) -> None:
        """r — hot reload the running flutter app."""
        if self._run_mode and self._active_proc:
            self._send_to_proc("r")
            self._log("[dim #565f89]→ Hot reload[/]")

    def action_hot_restart(self) -> None:
        """R — hot restart the running flutter app."""
        if self._run_mode and self._active_proc:
            self._send_to_proc("R")
            self._log("[dim #565f89]→ Hot restart[/]")

    def action_stop_proc(self) -> None:
        """s — stop any running process."""
        if self._active_proc is None:
            self._log("[dim #565f89]No process running.[/]")
            return
        if self._run_mode:
            self._send_to_proc("q")
        try:
            self._active_proc.terminate()
        except Exception:
            pass
        self._active_proc = None
        self._run_mode = False
        self._log("[#e0af68]⚠ Process stopped.[/]")
        self._update_run_status()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_unmount(self) -> None:
        """Clean up any running process when the widget is removed."""
        if self._active_proc is not None:
            try:
                self._active_proc.terminate()
            except Exception:
                pass
            self._active_proc = None

    # ── Output helpers ────────────────────────────────────────────────────────

    def _log(self, markup: str) -> None:
        try:
            self.query_one("#fl-output", RichLog).write(markup)
        except Exception:
            pass

    def _clear_output(self) -> None:
        try:
            self.query_one("#fl-output", RichLog).clear()
        except Exception:
            pass

    # ── Public trigger methods (for plugin commands() + handle_command) ───────

    def trigger_doctor(self) -> None:
        if self._active_proc is None:
            self._run_streaming("doctor", ["doctor"])

    def trigger_upgrade(self) -> None:
        if self._active_proc is None:
            self._run_streaming("upgrade", ["upgrade"])

    def trigger_devices(self) -> None:
        if self._active_proc is None:
            self._run_streaming("devices", ["devices"])

    def trigger_run(self) -> None:
        if self._active_proc is None:
            self._start_run_mode()

    def trigger_build(self, platform: str) -> None:
        if self._active_proc is None and platform in _BUILD_PLATFORMS:
            self._run_streaming("build", ["build", platform])

    def trigger_test(self) -> None:
        if self._active_proc is None:
            self._run_streaming("test", ["test"])

    def trigger_analyze(self) -> None:
        if self._active_proc is None:
            self._run_streaming("analyze", ["analyze"])

    def trigger_pub(self, op: str) -> None:
        name = f"pub {op}"
        if self._active_proc is None and name in _CMD_ARGS:
            self._run_streaming(name, ["pub", op])

    def trigger_clean(self) -> None:
        if self._active_proc is None:
            self._run_streaming("clean", ["clean"])

    def trigger_create(self, name: str) -> None:
        if self._active_proc is None and name:
            self._run_streaming("create", ["create", name])

    def select_category(self, name: str) -> None:
        """Move the cursor to the category with the given name."""
        for i, (cat_name, _) in enumerate(_CATEGORIES):
            if cat_name == name:
                self._cursor = i
                self._render_list()
                return


# ── Flutter commands plugin ───────────────────────────────────────────────────


class FlutterCommandsPlugin(Plugin):
    """Phase 4 — Flutter Command Runner plugin.

    Provides the Flutter panel (plugin ID ``"flutter"``) accessible via
    sidebar key **2** or the command palette.

    Steps implemented:
        4.1  Plugin shell — category list (left) + output log (right)
        4.2  flutter doctor  — parsed, colour-coded output
        4.3  flutter upgrade — streaming with auto-status refresh
        4.4  flutter devices — connected device listing
        4.5  flutter run     — interactive, r/R/q key forwarding
        4.6  flutter build   — platform picker modal
        4.7  flutter test    — colour-coded pass/fail/skip output
        4.8  flutter analyze — error/warning/info colour-coded output
        4.9  flutter pub     — get / upgrade / outdated
        4.10 flutter clean   — clean with output
        4.11 flutter create  — project name modal
    """

    def __init__(self) -> None:
        self._widget: FlutterCommandsWidget | None = None

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return "flutter"

    @property
    def name(self) -> str:
        return "Flutter"

    @property
    def icon(self) -> str:
        return "◉"

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)
        self._project_root: str = ctx.project_root

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        project_root = getattr(self, "_project_root", "")
        self._widget = FlutterCommandsWidget(
            project_root=project_root,
            id="flutter-commands-widget",
        )
        yield self._widget

    # ── Command palette entries ────────────────────────────────────────────────

    def commands(self) -> list[dict[str, Any]]:
        return [
            {
                "title": "Flutter: Run doctor",
                "description": "Check Flutter installation and dependencies",
                "plugin_id": "flutter",
                "action": self._cmd_doctor,
            },
            {
                "title": "Flutter: List devices",
                "description": "Show all connected Flutter devices",
                "plugin_id": "flutter",
                "action": self._cmd_devices,
            },
            {
                "title": "Flutter: Run tests",
                "description": "Execute all tests in the current project",
                "plugin_id": "flutter",
                "action": self._cmd_test,
            },
            {
                "title": "Flutter: Analyze code",
                "description": "Run flutter analyze and show issues",
                "plugin_id": "flutter",
                "action": self._cmd_analyze,
            },
            {
                "title": "Flutter: pub get",
                "description": "Fetch project dependencies",
                "plugin_id": "flutter",
                "action": self._cmd_pub_get,
            },
            {
                "title": "Flutter: Clean",
                "description": "Remove build artifacts (flutter clean)",
                "plugin_id": "flutter",
                "action": self._cmd_clean,
            },
        ]

    def _cmd_doctor(self) -> None:
        if self._widget:
            self._widget.trigger_doctor()

    def _cmd_devices(self) -> None:
        if self._widget:
            self._widget.trigger_devices()

    def _cmd_test(self) -> None:
        if self._widget:
            self._widget.trigger_test()

    def _cmd_analyze(self) -> None:
        if self._widget:
            self._widget.trigger_analyze()

    def _cmd_pub_get(self) -> None:
        if self._widget:
            self._widget.trigger_pub("get")

    def _cmd_clean(self) -> None:
        if self._widget:
            self._widget.trigger_clean()

    # ── Text command routing (from command input) ──────────────────────────────

    def handle_command(self, text: str) -> bool:
        """Handle ``flutter <sub>`` commands typed in the command input."""
        parts = text.strip().split()
        if not parts or parts[0].lower() != "flutter":
            return False
        if len(parts) < 2:
            return False
        if self._widget is None:
            return False

        sub = parts[1].lower()
        rest = parts[2:]

        if sub == "doctor":
            self._widget.trigger_doctor()
        elif sub == "upgrade":
            self._widget.trigger_upgrade()
        elif sub == "devices":
            self._widget.trigger_devices()
        elif sub == "run":
            self._widget.trigger_run()
        elif sub == "build":
            platform = rest[0] if rest else "apk"
            self._widget.trigger_build(platform)
        elif sub == "test":
            self._widget.trigger_test()
        elif sub == "analyze":
            self._widget.trigger_analyze()
        elif sub == "pub" and rest:
            self._widget.trigger_pub(rest[0])
        elif sub == "clean":
            self._widget.trigger_clean()
        elif sub == "create":
            name = rest[0] if rest else ""
            if name:
                self._widget.trigger_create(name)
            else:
                return False
        else:
            return False

        return True
