from __future__ import annotations

import json
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, RichLog, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.fvm_manager.fvm_api import (
    FvmVersion,
    get_fvmrc,
    install_fvm,
    install_version,
    is_fvm_installed,
    list_installed,
    list_releases,
    remove_version,
    run_doctor,
    uninstall_fvm,
    use_version,
)


# ── Install-version modal ─────────────────────────────────────────────────────


class _InstallModal(ModalScreen):
    """Lightweight modal for entering the Flutter version to install.

    Dismissed with the version string, or ``None`` on Cancel/Escape.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False, priority=True),
    ]

    DEFAULT_CSS = """
    _InstallModal {
        align: center middle;
    }
    _InstallModal > Vertical {
        width: 54;
        height: auto;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 1 2;
    }
    #install-title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        padding-bottom: 1;
        width: 1fr;
    }
    .install-hint {
        color: #a9b1d6;
        margin-bottom: 1;
        width: 1fr;
    }
    .install-dim {
        color: #565f89;
        margin-bottom: 1;
        width: 1fr;
    }
    #install-input {
        margin-bottom: 1;
    }
    #install-buttons {
        height: auto;
        align-horizontal: center;
    }
    #install-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Install Flutter Version", id="install-title")
            yield Static(
                "Enter a version, channel, or release tag:",
                classes="install-hint",
            )
            yield Static(
                "[dim]Examples: 3.29.3 · stable · beta · master[/]",
                classes="install-dim",
            )
            yield Input(placeholder="e.g. 3.29.3 or stable", id="install-input")
            with Center(id="install-buttons"):
                yield Button("Install", variant="primary", id="btn-install")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#install-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.label) == "Install":
            value = self.query_one("#install-input", Input).value.strip()
            self.dismiss(value or None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── FVM Manager widget ────────────────────────────────────────────────────────


class FvmManagerWidget(Widget):
    """FVM Manager plugin panel.

    Layout::

        ┌─ status bar ──────────────────────────────────────────────────────┐
        │ ✓ FVM 2.4.1  |  ↑↓ navigate · i install · x remove · u use       │
        ├─ left (30) ──────────────┬─ right (1fr) ────────────────────────┤
        │ Installed versions       │ Output / releases / doctor / config   │
        │  ▶ ● 3.29.3 (global)    │                                        │
        │    ○ 3.27.1             │                                        │
        ├──────────────────────────┤                                        │
        │ i install  x remove  u  │                                        │
        │ d doctor   l releases   │                                        │
        │ c config   r refresh    │                                        │
        └──────────────────────────┴───────────────────────────────────────┘

    Key bindings (active when this widget has focus):
        r — refresh installed list        i — install new version (opens modal)
        x — remove selected version       u — use selected version globally
        d — fvm doctor                    l — browse stable releases
        c — show .fvmrc config            shift+i (I) — install/uninstall FVM itself
        ↑/↓ — navigate version list
    """

    can_focus = True

    DEFAULT_CSS = """
    FvmManagerWidget {
        height: 1fr;
        layout: vertical;
    }
    #fvm-status {
        height: 1;
        background: #16161e;
        color: #7aa2f7;
        padding: 0 1;
        border-bottom: solid #3b4261;
    }
    #fvm-body {
        height: 1fr;
    }
    #fvm-left {
        width: 30;
        background: #1f2335;
        border-right: solid #3b4261;
    }
    #fvm-list {
        height: 1fr;
        background: #1f2335;
        padding: 1 1;
    }
    #fvm-actions {
        height: auto;
        color: #565f89;
        padding: 0 1 1 1;
        border-top: solid #3b4261;
    }
    #fvm-right {
        height: 1fr;
        background: #16161e;
    }
    #fvm-output {
        height: 1fr;
        background: #16161e;
        color: #a9b1d6;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("r",       "refresh",    "Refresh",   show=True),
        Binding("i",       "install",    "Install",   show=True),
        Binding("x",       "remove",     "Remove",    show=True),
        Binding("u",       "use_global", "Use",       show=True),
        Binding("d",       "doctor",     "Doctor",    show=True),
        Binding("l",       "releases",   "Releases",  show=True),
        Binding("c",       "config",     "Config",    show=True),
        Binding("I",       "install_fvm","FVM Install",show=False),
        Binding("up",      "cursor_up",  "Up",        show=False, priority=True),
        Binding("down",    "cursor_down","Down",       show=False, priority=True),
    ]

    def __init__(self, project_root: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._project_root = project_root
        self._versions: list[FvmVersion] = []
        self._cursor: int = 0

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="fvm-status")
        with Horizontal(id="fvm-body"):
            with Vertical(id="fvm-left"):
                yield Static("", id="fvm-list")
                yield Static(
                    "[dim]i[/] install  [dim]x[/] remove  [dim]u[/] use\n"
                    "[dim]d[/] doctor   [dim]l[/] releases [dim]r[/] refresh\n"
                    "[dim]c[/] config   [dim]I[/] fvm self-install",
                    id="fvm-actions",
                )
            with Vertical(id="fvm-right"):
                yield RichLog(id="fvm-output", markup=True, highlight=False, wrap=True)

    def on_mount(self) -> None:
        self._check_fvm_and_load()

    # ── Initial load ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _check_fvm_and_load(self) -> None:
        installed = is_fvm_installed()
        self.app.call_from_thread(self._apply_fvm_status, installed)
        if installed:
            versions = list_installed()
            self.app.call_from_thread(self._set_versions, versions)

    def _apply_fvm_status(self, installed: bool) -> None:
        if installed:
            self.query_one("#fvm-status", Static).update(
                "[#9ece6a]✓[/] FVM installed  "
                "[dim #565f89]↑↓ navigate · i install · x remove · u use · d doctor[/]"
            )
        else:
            self.query_one("#fvm-status", Static).update(
                "[#f7768e]✗[/] FVM not installed  "
                "[dim #565f89]Press [bold]I[/] to install via dart pub global[/]"
            )
            self._log("[#f7768e]FVM is not installed.[/]")
            self._log("")
            self._log("[#a9b1d6]Install FVM with:[/]")
            self._log("  [#7aa2f7]dart pub global activate fvm[/]")
            self._log("")
            self._log("[dim]Or press [bold]I[/] to install automatically.[/]")
            self._log("[dim]Visit: https://fvm.app/docs/getting_started/installation[/]")

    def _set_versions(self, versions: list[FvmVersion]) -> None:
        self._versions = versions
        if self._cursor >= len(versions) and versions:
            self._cursor = len(versions) - 1
        self._render_list()

    # ── Version list rendering ────────────────────────────────────────────────

    def _render_list(self) -> None:
        versions = self._versions
        if not versions:
            self.query_one("#fvm-list", Static).update(
                "[dim #565f89]No versions cached\n\nPress [bold]i[/] to install[/]"
            )
            return

        lines: list[str] = []
        for idx, v in enumerate(versions):
            dot = "[#9ece6a]●[/]" if v.is_active else "[dim #3b4261]○[/]"
            name_col = "#c0caf5" if v.is_active else "#a9b1d6"
            suffix = " [dim #9ece6a](global)[/]" if v.is_active else ""
            if idx == self._cursor:
                lines.append(
                    f" [bold #7aa2f7]▶[/] {dot} [bold {name_col}]{v.name}[/]{suffix}"
                )
            else:
                lines.append(f"   {dot} [{name_col}]{v.name}[/]{suffix}")

        self.query_one("#fvm-list", Static).update("\n".join(lines))

    # ── Logging helpers ───────────────────────────────────────────────────────

    def _log(self, text: str) -> None:
        try:
            self.query_one("#fvm-output", RichLog).write(text)
        except Exception:
            pass

    def _log_cmd(self, cmd: str) -> None:
        self._log(f"[#7aa2f7]$[/] [bold]{cmd}[/]")

    def _log_ok(self, text: str) -> None:
        self._log(f"[#9ece6a]▶[/] {text}")

    def _log_err(self, text: str) -> None:
        self._log(f"[#f7768e]✖[/] {text}")

    def _clear_output(self) -> None:
        try:
            self.query_one("#fvm-output", RichLog).clear()
        except Exception:
            pass

    # ── Cursor navigation ─────────────────────────────────────────────────────

    def action_cursor_up(self) -> None:
        if self._versions:
            self._cursor = (self._cursor - 1) % len(self._versions)
            self._render_list()

    def action_cursor_down(self) -> None:
        if self._versions:
            self._cursor = (self._cursor + 1) % len(self._versions)
            self._render_list()

    # ── Action: refresh (3.1) ─────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self._clear_output()
        self._log_cmd("fvm list")
        self._worker_refresh()

    @work(thread=True)
    def _worker_refresh(self) -> None:
        versions = list_installed()
        self.app.call_from_thread(self._set_versions, versions)
        self.app.call_from_thread(
            self._log_ok, f"Found {len(versions)} cached version(s)"
        )

    # ── Action: install version (3.4) ─────────────────────────────────────────

    def action_install(self) -> None:
        """Open install-version modal, then stream ``fvm install``."""
        self.app.push_screen(_InstallModal(), self._on_install_version)

    def _on_install_version(self, version: str | None) -> None:
        if not version:
            return
        self._clear_output()
        self._log_cmd(f"fvm install {version}")
        self._worker_install(version)

    @work(thread=True)
    def _worker_install(self, version: str) -> None:
        def on_line(line: str) -> None:
            self.app.call_from_thread(self._log, line)

        ok = install_version(version, on_line=on_line)
        if ok:
            self.app.call_from_thread(
                self._log_ok, f"Installed Flutter {version}"
            )
        else:
            self.app.call_from_thread(
                self._log_err, f"Failed to install Flutter {version}"
            )
        versions = list_installed()
        self.app.call_from_thread(self._set_versions, versions)

    # ── Action: use version globally (3.5) ────────────────────────────────────

    def action_use_global(self) -> None:
        if not self._versions:
            self._log_err("No versions available — press i to install one")
            return
        version = self._versions[self._cursor].name
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Use Flutter Version")
            .section(f"Set [bold]{version}[/] as the global Flutter version?")
            .buttons("Confirm", "Cancel")
        )
        self.app.push_screen(
            modal, lambda r: self._on_use_confirmed(r, version)
        )

    def _on_use_confirmed(self, result: str | None, version: str) -> None:
        if result != "Confirm":
            return
        self._clear_output()
        self._log_cmd(f"fvm use {version} --global")
        self._worker_use(version)

    @work(thread=True)
    def _worker_use(self, version: str) -> None:
        ok, output = use_version(version, global_flag=True)
        if ok:
            self.app.call_from_thread(
                self._log_ok, f"Now using Flutter {version} globally"
            )
        else:
            self.app.call_from_thread(
                self._log_err, output or f"Failed to use {version}"
            )
        versions = list_installed()
        self.app.call_from_thread(self._set_versions, versions)

    # ── Action: remove version (3.6) ──────────────────────────────────────────

    def action_remove(self) -> None:
        if not self._versions:
            self._log_err("No versions to remove")
            return
        version = self._versions[self._cursor].name
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Remove Flutter Version")
            .section(f"Remove cached Flutter [bold]{version}[/]?")
            .section("[dim]This will delete the SDK from the FVM cache.[/]")
            .buttons("Confirm", "Cancel")
        )
        self.app.push_screen(
            modal, lambda r: self._on_remove_confirmed(r, version)
        )

    def _on_remove_confirmed(self, result: str | None, version: str) -> None:
        if result != "Confirm":
            return
        self._clear_output()
        self._log_cmd(f"fvm remove {version}")
        self._worker_remove(version)

    @work(thread=True)
    def _worker_remove(self, version: str) -> None:
        ok, output = remove_version(version)
        if ok:
            self.app.call_from_thread(
                self._log_ok, f"Removed Flutter {version}"
            )
        else:
            self.app.call_from_thread(
                self._log_err, output or f"Failed to remove {version}"
            )
        versions = list_installed()
        self.app.call_from_thread(self._set_versions, versions)

    # ── Action: fvm doctor (3.7) ──────────────────────────────────────────────

    def action_doctor(self) -> None:
        self._clear_output()
        self._log_cmd("fvm doctor")
        self._worker_doctor()

    @work(thread=True)
    def _worker_doctor(self) -> None:
        output = run_doctor(self._project_root or None)
        if output:
            for line in output.splitlines():
                self.app.call_from_thread(self._log, line)
        else:
            self.app.call_from_thread(self._log_err, "No output from fvm doctor")

    # ── Action: releases browser (3.3) ────────────────────────────────────────

    def action_releases(self) -> None:
        self._clear_output()
        self._log_cmd("fvm releases --channel stable")
        self._log("[dim #565f89]Loading releases… this may take a moment[/]")
        self._worker_releases()

    @work(thread=True)
    def _worker_releases(self) -> None:
        versions = list_releases("stable")
        self.app.call_from_thread(self._show_releases, versions)

    def _show_releases(self, versions: list[str]) -> None:
        self._clear_output()
        if not versions:
            self._log_err("Could not fetch releases. Check your internet connection.")
            self._log("[dim]Run: fvm releases[/]")
            return
        self._log(f"[#7aa2f7]Stable releases[/]  ({len(versions)} found)")
        self._log("")
        for v in versions[:40]:
            self._log(f"  [#a9b1d6]{v}[/]")
        if len(versions) > 40:
            self._log(f"  [dim #565f89]… and {len(versions) - 40} more[/]")
        self._log("")
        self._log("[dim]Press [bold]i[/] to install a version[/]")

    # ── Action: config (.fvmrc) (3.8) ─────────────────────────────────────────

    def action_config(self) -> None:
        self._clear_output()
        if not self._project_root:
            self._log("[dim #565f89]No project root set.[/]")
            self._log("[dim]Start FlutterCraft from a Flutter project directory.[/]")
            return
        self._log_cmd("cat .fvmrc")
        config = get_fvmrc(self._project_root)
        if config is None:
            self._log("[dim #565f89]No .fvmrc found in project root.[/]")
            self._log(f"[dim]Looked in: {self._project_root}[/]")
            self._log("")
            self._log("[dim]Use [bold]u[/] to set a version, which writes .fvmrc.[/]")
        else:
            self._log("[#7aa2f7].fvmrc:[/]")
            self._log("")
            for line in json.dumps(config, indent=2).splitlines():
                self._log(f"  {line}")

    # ── Action: install / uninstall FVM itself (3.2) ──────────────────────────

    def action_install_fvm(self) -> None:
        """I — install or uninstall FVM itself."""
        fvm_present = is_fvm_installed()
        from fluttercraft.widgets.modal import CraftModal

        if fvm_present:
            modal = (
                CraftModal.build("Uninstall FVM")
                .section("Remove FVM from your system?")
                .section("[dim]Runs: dart pub global deactivate fvm[/]")
                .buttons("Confirm", "Cancel")
            )
            self.app.push_screen(modal, self._on_uninstall_fvm)
        else:
            modal = (
                CraftModal.build("Install FVM")
                .section("Install FVM via dart pub global?")
                .section("[dim]Runs: dart pub global activate fvm[/]")
                .buttons("Confirm", "Cancel")
            )
            self.app.push_screen(modal, self._on_install_fvm)

    def _on_install_fvm(self, result: str | None) -> None:
        if result != "Confirm":
            return
        self._clear_output()
        self._log_cmd("dart pub global activate fvm")
        self._worker_install_fvm()

    @work(thread=True)
    def _worker_install_fvm(self) -> None:
        ok, output = install_fvm()
        for line in output.splitlines():
            self.app.call_from_thread(self._log, line)
        if ok:
            self.app.call_from_thread(self._log_ok, "FVM installed successfully")
            self.app.call_from_thread(self._apply_fvm_status, True)
            versions = list_installed()
            self.app.call_from_thread(self._set_versions, versions)
        else:
            self.app.call_from_thread(self._log_err, "FVM installation failed")

    def _on_uninstall_fvm(self, result: str | None) -> None:
        if result != "Confirm":
            return
        self._clear_output()
        self._log_cmd("dart pub global deactivate fvm")
        self._worker_uninstall_fvm()

    @work(thread=True)
    def _worker_uninstall_fvm(self) -> None:
        ok, output = uninstall_fvm()
        for line in output.splitlines():
            self.app.call_from_thread(self._log, line)
        if ok:
            self.app.call_from_thread(self._log_ok, "FVM removed")
            self.app.call_from_thread(self._apply_fvm_status, False)
        else:
            self.app.call_from_thread(self._log_err, "FVM removal failed")

    # ── Public helpers (called by plugin) ─────────────────────────────────────

    def trigger_refresh(self) -> None:
        self.action_refresh()

    def trigger_doctor(self) -> None:
        self.action_doctor()

    def trigger_releases(self) -> None:
        self.action_releases()


# ── FVM Manager plugin ────────────────────────────────────────────────────────


class FvmManagerPlugin(Plugin):
    """Phase 3 — FVM Manager plugin.

    Provides the FVM Manager panel (plugin ID ``"fvm"``) accessible via
    sidebar key **1** or the command palette.

    Steps implemented:
        3.1  Plugin shell + widget layout
        3.2  Install / uninstall FVM itself (``I`` key)
        3.3  Releases browser (``l`` key)
        3.4  Version install with streaming output (``i`` key)
        3.5  Version switching — global (``u`` key)
        3.6  Version removal with confirmation (``x`` key)
        3.7  FVM doctor (``d`` key)
        3.8  .fvmrc config viewer (``c`` key)
    """

    def __init__(self) -> None:
        self._widget: FvmManagerWidget | None = None

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return "fvm"

    @property
    def name(self) -> str:
        return "FVM Manager"

    @property
    def icon(self) -> str:
        return "◈"

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)
        self._project_root: str = ctx.project_root

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        project_root = getattr(self, "_project_root", "")
        self._widget = FvmManagerWidget(
            project_root=project_root,
            id="fvm-manager-widget",
        )
        yield self._widget

    # ── Commands for palette ───────────────────────────────────────────────────

    def commands(self) -> list[dict]:
        return [
            {
                "title": "FVM: Refresh installed versions",
                "description": "Reload the list of cached Flutter SDK versions",
                "plugin_id": "fvm",
                "action": self._cmd_refresh,
            },
            {
                "title": "FVM: Run doctor",
                "description": "Check FVM installation and configuration",
                "plugin_id": "fvm",
                "action": self._cmd_doctor,
            },
            {
                "title": "FVM: Browse stable releases",
                "description": "View available Flutter SDK releases from fvm.app",
                "plugin_id": "fvm",
                "action": self._cmd_releases,
            },
        ]

    def _cmd_refresh(self) -> None:
        if self._widget:
            try:
                self._widget.trigger_refresh()
            except Exception:
                pass

    def _cmd_doctor(self) -> None:
        if self._widget:
            try:
                self._widget.trigger_doctor()
            except Exception:
                pass

    def _cmd_releases(self) -> None:
        if self._widget:
            try:
                self._widget.trigger_releases()
            except Exception:
                pass
