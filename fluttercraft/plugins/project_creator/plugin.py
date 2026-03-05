from __future__ import annotations

import re
from typing import Any

_ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-9;:<=>?]*[a-zA-Z]|\][^\x07]*\x07|[^[\]])")

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Input, RichLog, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.project_creator.creator_api import (
    TEMPLATES,
    ProjectConfig,
    Template,
    create_flutter_project,
    detect_platforms,
    get_template,
    get_template_preview,
    is_flutter_installed,
    is_valid_project_name,
    open_in_editor,
)


# ── Constants ─────────────────────────────────────────────────────────────────


_STEPS = [
    ("Name", "Enter a project name using snake_case (e.g. my_flutter_app)"),
    ("Organization", "Enter your org identifier (e.g. com.example)"),
    ("Platforms", "Select target platforms — Space to toggle, ↑↓ to navigate"),
    ("Template", "Choose an architecture template — ↑↓ to navigate"),
    ("Features", "Optional extras — Space to toggle, ↑↓ to navigate"),
    ("Review & Create", "Review your choices — press C or Enter to create"),
]

_PLATFORMS = [
    ("android", "Android"),
    ("ios", "iOS  (macOS required)"),
    ("web", "Web"),
    ("linux", "Linux"),
    ("windows", "Windows"),
    ("macos", "macOS  (macOS required)"),
]

_FEATURES = [
    ("app_icon", "App Icon  — flutter_launcher_icons"),
    ("splash", "Splash Screen  — flutter_native_splash"),
    ("linting", "Strict Linting  — analysis_options.yaml"),
]


# ── Project Creator Widget ────────────────────────────────────────────────────


class ProjectCreatorWidget(Widget):
    """Multi-step project creation wizard.

    Steps:
        0. Name       — text input
        1. Org        — text input
        2. Platforms  — multi-select list (Space=toggle, ↑↓=navigate)
        3. Template   — single-select list (↑↓=navigate, auto-selects)
        4. Features   — multi-select list (Space=toggle, ↑↓=navigate)
        5. Review     — summary + create (C or Enter)
    """

    can_focus = True

    DEFAULT_CSS = """
    ProjectCreatorWidget {
        height: 1fr;
        layout: vertical;
    }
    #wizard-step-bar {
        height: 1;
        background: #16161e;
        color: #7aa2f7;
        padding: 0 1;
        border-bottom: solid #3b4261;
    }
    #wizard-body {
        height: 1fr;
    }
    #wizard-left {
        width: 22;
        background: #1f2335;
        border-right: solid #3b4261;
        padding: 1 0;
    }
    #wizard-right {
        height: 1fr;
        background: #16161e;
    }
    #wizard-hint {
        height: 2;
        padding: 0 1;
        color: #565f89;
        border-bottom: solid #1f2335;
    }
    #wizard-input {
        margin: 1 1 0 1;
    }
    #wizard-list {
        height: 1fr;
        padding: 1 1;
        color: #a9b1d6;
    }
    #wizard-output {
        height: 1fr;
        padding: 0 1;
    }
    #wizard-footer {
        height: 2;
        background: #1f2335;
        padding: 0 1;
        border-top: solid #3b4261;
        color: #565f89;
    }
    """

    BINDINGS = [
        Binding("n",     "next_step",      "Next",    show=True),
        Binding("b",     "prev_step",      "Back",    show=True),
        Binding("up",    "list_up",        "Up",      show=False, priority=True),
        Binding("down",  "list_down",      "Down",    show=False, priority=True),
        Binding("space", "toggle_item",    "Toggle",  show=False, priority=True),
        Binding("p",     "show_preview",   "Preview", show=True),
        Binding("c",     "do_create",      "Create",  show=True),
        Binding("r",     "reset_wizard",   "Reset",   show=False),
    ]

    def __init__(self, output_dir: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._step: int = 0
        self._list_cursor: int = 0
        self._creating: bool = False
        self._last_project_dir: str = ""

        # Wizard state
        self._config = ProjectConfig(output_dir=output_dir)
        self._platforms_on: dict[str, bool] = {
            "android": True,
            "ios": True,
            "web": False,
            "linux": False,
            "windows": False,
            "macos": False,
        }
        self._template_cursor: int = 0
        self._features_on: dict[str, bool] = {
            "app_icon": False,
            "splash": False,
            "linting": False,
        }

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="wizard-step-bar")
        with Horizontal(id="wizard-body"):
            with Vertical(id="wizard-left"):
                yield Static("", id="wizard-steps")
            with Vertical(id="wizard-right"):
                yield Static("", id="wizard-hint")
                yield Input(placeholder="", id="wizard-input")
                yield Static("", id="wizard-list")
                yield RichLog(
                    id="wizard-output", markup=True, highlight=False, wrap=True
                )
        yield Static(
            "[dim]n[/] next  [dim]b[/] back  [dim]space[/] toggle  "
            "[dim]p[/] preview  [dim]c[/] create  [dim]r[/] reset",
            id="wizard-footer",
        )

    def on_mount(self) -> None:
        self._detect_platforms_bg()
        self._render_all()
        self.set_timer(0.1, self.focus)

    # ── Platform auto-detection ───────────────────────────────────────────────

    @work(thread=True)
    def _detect_platforms_bg(self) -> None:
        detected = detect_platforms()
        self.app.call_from_thread(self._apply_detected_platforms, detected)

    def _apply_detected_platforms(self, detected: dict[str, bool]) -> None:
        # Auto-check detected platforms (keep user choices if already changed)
        for key, is_detected in detected.items():
            if is_detected and key not in ("ios", "macos"):
                self._platforms_on[key] = True
        if self._step == 2:
            self._render_list()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_all(self) -> None:
        self._render_step_bar()
        self._render_step_nav()
        self._render_hint()
        self._update_content_visibility()

    def _render_step_bar(self) -> None:
        step_label = _STEPS[self._step][0]
        bar = (
            f"[bold #7aa2f7]● Project Creator[/]  "
            f"[dim #565f89]Step {self._step + 1}/{len(_STEPS)}: {step_label}[/]"
        )
        self.query_one("#wizard-step-bar", Static).update(bar)

    def _render_step_nav(self) -> None:
        lines: list[str] = ["[dim #565f89] Steps[/]", ""]
        for i, (label, _) in enumerate(_STEPS):
            if i == self._step:
                lines.append(f" [bold #7aa2f7]▶ {i + 1}. {label}[/]")
            elif i < self._step:
                lines.append(f" [#9ece6a]✓ {i + 1}. {label}[/]")
            else:
                lines.append(f" [dim #3b4261]  {i + 1}. {label}[/]")
        self.query_one("#wizard-steps", Static).update("\n".join(lines))

    def _render_hint(self) -> None:
        hint = _STEPS[self._step][1]
        self.query_one("#wizard-hint", Static).update(f"[dim #565f89]{hint}[/]")

    def _update_content_visibility(self) -> None:
        is_text = self._step in (0, 1)
        is_list = self._step in (2, 3, 4, 5)

        inp = self.query_one("#wizard-input", Input)
        lst = self.query_one("#wizard-list", Static)
        out = self.query_one("#wizard-output", RichLog)

        inp.display = is_text
        lst.display = is_list
        out.display = False  # only shown when creating

        if is_text:
            if self._step == 0:
                inp.placeholder = "my_flutter_app"
                inp.value = self._config.name
            else:
                inp.placeholder = "com.example"
                inp.value = self._config.org
            self.set_timer(0.05, inp.focus)
        elif is_list:
            self._render_list()
            self.set_timer(0.05, self.focus)

    def _render_list(self) -> None:
        if self._step == 2:
            self._render_platform_list()
        elif self._step == 3:
            self._render_template_list()
        elif self._step == 4:
            self._render_feature_list()
        elif self._step == 5:
            self._render_review()

    def _render_platform_list(self) -> None:
        lines: list[str] = []
        for i, (key, label) in enumerate(_PLATFORMS):
            cursor = "[bold #7aa2f7]▶[/] " if i == self._list_cursor else "  "
            checked = "[#9ece6a]✓[/]" if self._platforms_on.get(key) else "[dim #3b4261]○[/]"
            lines.append(f"{cursor}{checked}  [#a9b1d6]{label}[/]")
        self.query_one("#wizard-list", Static).update("\n".join(lines))

    def _render_template_list(self) -> None:
        lines: list[str] = []
        for i, tmpl in enumerate(TEMPLATES):
            cursor = "[bold #7aa2f7]▶[/] " if i == self._template_cursor else "  "
            selected = i == self._template_cursor
            name_col = "#c0caf5" if selected else "#a9b1d6"
            desc_col = "#565f89" if not selected else "#7aa2f7"
            lines.append(
                f"{cursor}[bold {name_col}]{tmpl.name}[/]"
                f"[dim {desc_col}]  — {tmpl.description}[/]"
            )
        self.query_one("#wizard-list", Static).update("\n".join(lines))

    def _render_feature_list(self) -> None:
        lines: list[str] = []
        for i, (key, label) in enumerate(_FEATURES):
            cursor = "[bold #7aa2f7]▶[/] " if i == self._list_cursor else "  "
            checked = "[#9ece6a]✓[/]" if self._features_on.get(key) else "[dim #3b4261]○[/]"
            lines.append(f"{cursor}{checked}  [#a9b1d6]{label}[/]")
        self.query_one("#wizard-list", Static).update("\n".join(lines))

    def _render_review(self) -> None:
        tmpl = TEMPLATES[self._template_cursor]
        platforms = [k for k, v in self._platforms_on.items() if v] or ["(none)"]
        features = [k for k, v in self._features_on.items() if v]

        lines: list[str] = [
            "[bold #7aa2f7]Review your project[/]",
            "",
            f"  [dim]Name:[/]       [bold #c0caf5]{self._config.name or '(not set)'}[/]",
            f"  [dim]Org:[/]        [#a9b1d6]{self._config.org}[/]",
            f"  [dim]Platforms:[/]  [#a9b1d6]{', '.join(platforms)}[/]",
            f"  [dim]Template:[/]   [#a9b1d6]{tmpl.name} — {tmpl.description}[/]",
            f"  [dim]Features:[/]   [#a9b1d6]{', '.join(features) or 'none'}[/]",
            "",
            f"  [dim]Output:[/]     [dim #565f89]{self._config.output_dir or '(current directory)'}[/]",
            "",
        ]

        if not self._config.name:
            lines.append("[#f7768e]⚠  Project name is required — press B to go back[/]")
        elif self._creating:
            lines.append("[#9ece6a]Creating project…[/]")
        else:
            lines.append("[dim]Press [bold]C[/bold] or Enter to create · [bold]P[/bold] to preview · [bold]B[/bold] to go back[/]")

        self.query_one("#wizard-list", Static).update("\n".join(lines))

    # ── Step navigation ───────────────────────────────────────────────────────

    def action_next_step(self) -> None:
        if self._creating:
            return
        if self._step == 5:
            self.action_do_create()
            return
        # Validate current step before advancing
        if not self._advance_step():
            return
        self._step = min(self._step + 1, len(_STEPS) - 1)
        self._list_cursor = 0
        self._render_all()

    def _advance_step(self) -> bool:
        """Validate and commit current step. Return False to block advance."""
        if self._step == 0:
            name = self.query_one("#wizard-input", Input).value.strip()
            if not name:
                self._flash_hint("Project name cannot be empty")
                return False
            if not is_valid_project_name(name):
                self._flash_hint("Use snake_case: lowercase letters, digits, underscores")
                return False
            self._config.name = name
        elif self._step == 1:
            org = self.query_one("#wizard-input", Input).value.strip()
            self._config.org = org or "com.example"
        elif self._step == 2:
            self._config.platforms = [k for k, v in self._platforms_on.items() if v]
        elif self._step == 3:
            self._config.template_id = TEMPLATES[self._template_cursor].id
        elif self._step == 4:
            self._config.app_icon = self._features_on.get("app_icon", False)
            self._config.splash_screen = self._features_on.get("splash", False)
            self._config.linting = self._features_on.get("linting", False)
        return True

    def _flash_hint(self, msg: str) -> None:
        self.query_one("#wizard-hint", Static).update(f"[bold #f7768e]⚠  {msg}[/]")

    def action_prev_step(self) -> None:
        if self._creating:
            return
        if self._step == 0:
            return
        self._step -= 1
        self._list_cursor = 0
        self._render_all()

    # ── List navigation ───────────────────────────────────────────────────────

    def action_list_up(self) -> None:
        if self._step in (2, 4):
            length = len(_PLATFORMS) if self._step == 2 else len(_FEATURES)
            self._list_cursor = (self._list_cursor - 1) % length
            self._render_list()
        elif self._step == 3:
            self._template_cursor = (self._template_cursor - 1) % len(TEMPLATES)
            self._render_list()

    def action_list_down(self) -> None:
        if self._step in (2, 4):
            length = len(_PLATFORMS) if self._step == 2 else len(_FEATURES)
            self._list_cursor = (self._list_cursor + 1) % length
            self._render_list()
        elif self._step == 3:
            self._template_cursor = (self._template_cursor + 1) % len(TEMPLATES)
            self._render_list()

    # ── Toggle selection ──────────────────────────────────────────────────────

    def action_toggle_item(self) -> None:
        if self._step == 2:
            key = _PLATFORMS[self._list_cursor][0]
            self._platforms_on[key] = not self._platforms_on.get(key, False)
            self._render_list()
        elif self._step == 4:
            key = _FEATURES[self._list_cursor][0]
            self._features_on[key] = not self._features_on.get(key, False)
            self._render_list()

    # ── Input enter ───────────────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._step in (0, 1):
            self.action_next_step()

    # ── Preview ───────────────────────────────────────────────────────────────

    def action_show_preview(self) -> None:
        """Show the template folder structure preview in the list area."""
        # Apply current selections to config for accurate preview
        if self._config.name:
            cfg = ProjectConfig(
                name=self._config.name,
                org=self._config.org,
                platforms=[k for k, v in self._platforms_on.items() if v],
                template_id=TEMPLATES[self._template_cursor].id,
                app_icon=self._features_on.get("app_icon", False),
                splash_screen=self._features_on.get("splash", False),
                linting=self._features_on.get("linting", False),
            )
        else:
            cfg = ProjectConfig(
                name="my_app",
                template_id=TEMPLATES[self._template_cursor].id,
                app_icon=self._features_on.get("app_icon", False),
                splash_screen=self._features_on.get("splash", False),
            )

        preview = get_template_preview(cfg)
        tmpl = TEMPLATES[self._template_cursor]

        lst = self.query_one("#wizard-list", Static)
        lst.display = True

        lines = [
            f"[bold #7aa2f7]Template Preview: {tmpl.name}[/]",
            f"[dim #565f89]{tmpl.description}[/]",
            "",
        ]
        for line in preview.splitlines():
            lines.append(f"[#a9b1d6]{line}[/]")
        lines.append("")
        lines.append("[dim]Press any step key (n/b) to return to wizard[/]")

        lst.update("\n".join(lines))

    # ── Create ────────────────────────────────────────────────────────────────

    def action_do_create(self) -> None:
        if self._creating:
            return
        if not self._config.name:
            self._flash_hint("Set a project name first (step 1)")
            return
        # Commit all steps
        self._config.platforms = [k for k, v in self._platforms_on.items() if v]
        self._config.template_id = TEMPLATES[self._template_cursor].id
        self._config.app_icon = self._features_on.get("app_icon", False)
        self._config.splash_screen = self._features_on.get("splash", False)
        self._config.linting = self._features_on.get("linting", False)

        self._creating = True
        # Switch to review step and show output
        self._step = 5
        self._render_all()
        self.query_one("#wizard-output", RichLog).display = True
        self.query_one("#wizard-list", Static).display = True
        self._render_review()

        self._worker_create(self._config)

    @work(thread=True)
    def _worker_create(self, config: ProjectConfig) -> None:
        flutter_ok = is_flutter_installed()
        if not flutter_ok:
            self.app.call_from_thread(
                self._log_err, "Flutter not found on PATH — install Flutter first"
            )
            self.app.call_from_thread(self._on_create_done, False, "")
            return

        ok, project_dir = create_flutter_project(
            config,
            on_line=lambda line: self.app.call_from_thread(self._log_output, line),
        )
        self.app.call_from_thread(self._on_create_done, ok, project_dir)

    def _log_output(self, line: str) -> None:
        try:
            line = _ANSI_ESCAPE.sub("", line)
            if not line.strip():
                return
            rlog = self.query_one("#wizard-output", RichLog)
            # Basic colorization
            if line.startswith("$"):
                rlog.write(f"[#7aa2f7]{line}[/]")
            elif "error" in line.lower() or "failed" in line.lower():
                rlog.write(f"[#f7768e]{line}[/]")
            elif "✓" in line or "success" in line.lower():
                rlog.write(f"[#9ece6a]{line}[/]")
            else:
                rlog.write(f"[#a9b1d6]{line}[/]")
        except Exception:
            pass

    def _log_err(self, msg: str) -> None:
        try:
            self.query_one("#wizard-output", RichLog).write(f"[#f7768e]✖  {msg}[/]")
        except Exception:
            pass

    def _on_create_done(self, ok: bool, project_dir: str) -> None:
        self._creating = False
        self._last_project_dir = project_dir
        out = self.query_one("#wizard-output", RichLog)
        if ok:
            out.write("")
            out.write(f"[bold #9ece6a]✓  Project created: {project_dir}[/]")
            out.write("")
            out.write("[dim]Next steps:[/]")
            out.write(f"  [#7aa2f7]cd {project_dir}[/]")
            out.write("  [#7aa2f7]flutter run[/]")
            if self._config.app_icon:
                out.write("  [#7aa2f7]dart run flutter_launcher_icons[/]")
            if self._config.splash_screen:
                out.write("  [#7aa2f7]dart run flutter_native_splash:create[/]")
            out.write("")
            out.write("[dim]Press [bold]E[/bold] to open in editor · [bold]R[/bold] to create another[/]")
        else:
            out.write("[#f7768e]✖  Project creation failed — see output above[/]")
        self._render_review()

    # ── Extra actions available after creation ─────────────────────────────────

    def on_key(self, event: Any) -> None:
        if event.key == "e" and self._last_project_dir and not self._creating:
            open_in_editor(self._last_project_dir)
        elif event.key == "enter" and not self._creating:
            if self._step in (2, 3, 4):
                self.action_next_step()
                event.stop()
            elif self._step == 5:
                self.action_do_create()
                event.stop()

    # ── Reset ─────────────────────────────────────────────────────────────────

    def action_reset_wizard(self) -> None:
        if self._creating:
            return
        self._step = 0
        self._list_cursor = 0
        self._template_cursor = 0
        self._config = ProjectConfig(output_dir=self._config.output_dir)
        self._platforms_on = {
            "android": True, "ios": True, "web": False,
            "linux": False, "windows": False, "macos": False,
        }
        self._features_on = {"app_icon": False, "splash": False, "linting": False}
        self._last_project_dir = ""
        try:
            self.query_one("#wizard-output", RichLog).clear()
        except Exception:
            pass
        self._render_all()

    # ── Public trigger API ────────────────────────────────────────────────────

    def trigger_preview(self) -> None:
        self.action_show_preview()

    def trigger_reset(self) -> None:
        self.action_reset_wizard()


# ── Project Creator Plugin ────────────────────────────────────────────────────


class ProjectCreatorPlugin(Plugin):
    """Phase 6 — Project Creator plugin.

    Provides the Project Creator wizard panel (plugin ID ``"creator"``).

    Steps implemented:
        6.1  Multi-step wizard UI (name → org → platforms → template → features → create)
        6.2  Platform auto-detection (Android SDK, Xcode, Chrome, Linux/Windows)
        6.3  Template registry (simple, bloc, riverpod, provider, getx, mobx, mvvm, clean_arch)
        6.4  State management deps auto-added to pubspec.yaml
        6.5  Folder structure generated per template
        6.6  App icon setup (flutter_launcher_icons config)
        6.7  Splash screen setup (flutter_native_splash config)
        6.8  Post-creation guide, open in editor (E key)
        6.9  Template preview (P key)
    """

    def __init__(self) -> None:
        self._widget: ProjectCreatorWidget | None = None

    @property
    def id(self) -> str:
        return "project"

    @property
    def name(self) -> str:
        return "Project Creator"

    @property
    def icon(self) -> str:
        return "✦"

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)
        self._output_dir: str = ctx.work_dir or ""

    def compose(self) -> ComposeResult:
        output_dir = getattr(self, "_output_dir", "")
        self._widget = ProjectCreatorWidget(
            output_dir=output_dir,
            id="project-creator-widget",
        )
        yield self._widget

    def commands(self) -> list[dict]:
        return [
            {
                "title": "Creator: New Flutter project",
                "description": "Open the project creation wizard",
                "plugin_id": "project",
                "action": self._cmd_open,
            },
            {
                "title": "Creator: Preview template",
                "description": "Show folder structure for the selected template",
                "plugin_id": "project",
                "action": self._cmd_preview,
            },
            {
                "title": "Creator: Reset wizard",
                "description": "Clear all wizard choices and start over",
                "plugin_id": "project",
                "action": self._cmd_reset,
            },
        ]

    def _call(self, method: str, *args: Any) -> None:
        if self._widget:
            try:
                getattr(self._widget, method)(*args)
            except Exception:
                pass

    def _cmd_open(self) -> None:
        pass  # Opening is handled by sidebar navigation

    def _cmd_preview(self) -> None:
        self._call("trigger_preview")

    def _cmd_reset(self) -> None:
        self._call("trigger_reset")

    def handle_command(self, text: str) -> bool:
        """Route project name and create commands from the command input.

        Accepted forms:
            ``my_app``               — bare valid name: sets wizard name on step 0
            ``create my_app``        — alias for setting name and jumping to wizard
            ``new my_app``           — same as create
        """
        parts = text.strip().split()
        if not parts:
            return False

        cmd = parts[0].lower()

        # Bare valid project name typed while Creator panel is active on step 0
        if (
            len(parts) == 1
            and is_valid_project_name(parts[0])
            and self._widget is not None
            and not self._widget._creating
            and self._widget._step == 0
        ):
            try:
                self._widget._config.name = cmd
                inp = self._widget.query_one("#wizard-input", Input)
                inp.value = cmd
            except Exception:
                pass
            return True

        # create <name> / new <name>
        if cmd in ("create", "new") and len(parts) >= 2:
            name = parts[1]
            if self._widget and not self._widget._creating:
                try:
                    if is_valid_project_name(name):
                        self._widget._config.name = name
                        self._widget.action_reset_wizard()
                        self._widget._config.name = name
                        inp = self._widget.query_one("#wizard-input", Input)
                        inp.value = name
                except Exception:
                    pass
            return True

        return False
