from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Label, Static


class SettingsScreen(ModalScreen):
    """Settings modal — accessible via Ctrl+, or /settings."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("ctrl+comma", "dismiss", "Close", show=False),
    ]

    CSS = """
    SettingsScreen {
        background: #1a1b2699;
        align: center middle;
    }
    #settings-container {
        width: 60;
        height: auto;
        background: #1a1b26;
        border: round #7aa2f7;
        border-title-color: #7aa2f7;
        padding: 1 2;
    }
    #settings-title {
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }
    .settings-section-title {
        color: #a9b1d6;
        text-style: bold;
        margin-top: 1;
    }
    .settings-row {
        height: 3;
        layout: horizontal;
        align: left middle;
    }
    .settings-row Label {
        width: 1fr;
        color: #a9b1d6;
        content-align: left middle;
    }
    #settings-version {
        color: #565f89;
        margin-top: 1;
    }
    #settings-close {
        margin-top: 1;
        width: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._flags: dict[str, bool] = {}

    def compose(self) -> ComposeResult:
        # Grab feature flags from app if available
        try:
            ff = self.app.feature_flags  # type: ignore[attr-defined]
            self._flags = {
                "notifications":    ff.is_enabled("notifications"),
                "command_palette":  ff.is_enabled("command_palette"),
            }
        except Exception:
            self._flags = {"notifications": True, "command_palette": True}

        with Vertical(id="settings-container"):
            yield Static("⚙  Settings", id="settings-title", markup=False)

            yield Static("Feature Flags", classes="settings-section-title", markup=False)
            with Horizontal(classes="settings-row"):
                yield Label("Notifications")
                yield Checkbox("", value=self._flags.get("notifications", True), id="cb-notifications")
            with Horizontal(classes="settings-row"):
                yield Label("Command Palette")
                yield Checkbox("", value=self._flags.get("command_palette", True), id="cb-command-palette")

            yield Static("Theme", classes="settings-section-title", markup=False)
            with Horizontal(classes="settings-row"):
                yield Label("Open theme picker")
                yield Button("Ctrl+T", variant="default", id="btn-theme")

            try:
                from fluttercraft import __version__
                ver = __version__
            except Exception:
                ver = "0.2.0"
            yield Static(f"FlutterCraft  v{ver}", id="settings-version", markup=False)
            yield Button("Close", variant="primary", id="settings-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings-close":
            self.dismiss()
        elif event.button.id == "btn-theme":
            self.dismiss()
            self.app.action_cycle_theme()  # type: ignore[attr-defined]

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        try:
            ff = self.app.feature_flags  # type: ignore[attr-defined]
            flag_map = {
                "cb-notifications":   "notifications",
                "cb-command-palette": "command_palette",
            }
            flag = flag_map.get(event.checkbox.id or "")
            if flag:
                ff.enable(flag) if event.value else ff.disable(flag)
        except Exception:
            pass
