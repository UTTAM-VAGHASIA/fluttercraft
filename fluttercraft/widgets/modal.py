from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


# ── Modal screen ─────────────────────────────────────────────────────────────


class CraftModal(ModalScreen):
    """Declarative modal dialog built via a fluent builder API.

    Use :meth:`build` to create a modal — never instantiate directly::

        modal = CraftModal.build("Confirm action") \\
            .section("Are you sure you want to remove this version?") \\
            .buttons("Confirm", "Cancel")

        def on_dismiss(result: str | None) -> None:
            if result == "Confirm":
                do_the_thing()

        self.app.push_screen(modal, on_dismiss)

    The dismissed value is the button label that was pressed, or ``None``
    if the modal was closed via Escape.
    """

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close", show=False, priority=True),
    ]

    DEFAULT_CSS = """
    CraftModal {
        align: center middle;
    }
    CraftModal > Vertical {
        width: 60;
        max-width: 80%;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 1 2;
        height: auto;
    }
    #modal-title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        padding-bottom: 1;
        width: 1fr;
    }
    .modal-section {
        color: #a9b1d6;
        margin-bottom: 1;
        width: 1fr;
    }
    .modal-input {
        margin-bottom: 1;
    }
    #modal-buttons {
        layout: horizontal;
        height: auto;
        margin-top: 1;
        align-horizontal: center;
    }
    #modal-buttons Button {
        margin: 0 1;
    }
    """

    # ── Message ───────────────────────────────────────────────────────────────

    class ButtonPressed(Message):
        """Posted when the user presses a modal button (before dismiss)."""

        def __init__(self, label: str) -> None:
            self.label = label
            super().__init__()

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(
        self,
        title: str,
        sections: list[dict] | None = None,
        button_labels: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._sections: list[dict] = sections or []
        self._button_labels: list[str] = button_labels or ["OK"]

    # ── Builder entry point ───────────────────────────────────────────────────

    @classmethod
    def build(cls, title: str) -> _ModalBuilder:
        """Start a fluent builder chain.

        Example::

            modal = CraftModal.build("Delete version?") \\
                .section("This will remove Flutter 3.16.0 from your system.") \\
                .input("Type the version to confirm", placeholder="3.16.0") \\
                .buttons("Delete", "Cancel")
        """
        return _ModalBuilder(title)

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self._title, id="modal-title")
            for i, section in enumerate(self._sections):
                if section["type"] == "text":
                    yield Static(section["content"], classes="modal-section")
                elif section["type"] == "input":
                    yield Input(
                        placeholder=section.get("placeholder", ""),
                        id=f"modal-input-{i}",
                        classes="modal-input",
                    )
            with Center(id="modal-buttons"):
                for label in self._button_labels:
                    variant = (
                        "primary"
                        if label.lower() in ("ok", "yes", "confirm", "delete", "save")
                        else "default"
                    )
                    yield Button(label, variant=variant, id=f"btn-{label.lower()}")

    # ── Events ────────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        label = str(event.button.label)
        self.post_message(self.ButtonPressed(label))
        self.dismiss(label)

    def action_dismiss_modal(self) -> None:
        self.dismiss(None)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_input_value(self, index: int = 0) -> str:
        """Return the value of the *index*-th input field (0-based)."""
        for i, section in enumerate(self._sections):
            if section["type"] == "input":
                if index == 0:
                    try:
                        return self.query_one(f"#modal-input-{i}", Input).value
                    except Exception:
                        return ""
                index -= 1
        return ""


# ── Fluent builder ────────────────────────────────────────────────────────────


class _ModalBuilder:
    """Internal fluent builder. Created by :meth:`CraftModal.build`."""

    def __init__(self, title: str) -> None:
        self._title = title
        self._sections: list[dict] = []

    def section(self, text: str) -> _ModalBuilder:
        """Append a read-only text paragraph."""
        self._sections.append({"type": "text", "content": text})
        return self

    def input(self, placeholder: str = "") -> _ModalBuilder:
        """Append a text input field."""
        self._sections.append({"type": "input", "placeholder": placeholder})
        return self

    def buttons(self, *labels: str) -> CraftModal:
        """Finalise the builder and return a :class:`CraftModal` ready to push.

        At least one label is required. The first label matching
        ``ok / yes / confirm / delete / save`` gets the ``primary`` variant.
        """
        if not labels:
            labels = ("OK",)
        return CraftModal(
            title=self._title,
            sections=self._sections,
            button_labels=list(labels),
        )
