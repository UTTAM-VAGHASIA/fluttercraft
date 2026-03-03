from __future__ import annotations

import pytest

from fluttercraft.widgets.modal import CraftModal, _ModalBuilder


# ── Builder API ───────────────────────────────────────────────────────────────


def test_build_returns_builder():
    builder = CraftModal.build("My Title")
    assert isinstance(builder, _ModalBuilder)


def test_builder_section_returns_self():
    builder = CraftModal.build("Title")
    result = builder.section("Some text")
    assert result is builder


def test_builder_input_returns_self():
    builder = CraftModal.build("Title")
    result = builder.input("placeholder")
    assert result is builder


def test_builder_buttons_returns_craft_modal():
    modal = CraftModal.build("Title").buttons("OK", "Cancel")
    assert isinstance(modal, CraftModal)


def test_builder_default_button_when_none_given():
    modal = CraftModal.build("Title").buttons()
    assert modal._button_labels == ["OK"]


def test_builder_preserves_sections():
    modal = (
        CraftModal.build("Title")
        .section("First paragraph")
        .section("Second paragraph")
        .input(placeholder="Enter value")
        .buttons("Submit", "Cancel")
    )
    assert len(modal._sections) == 3
    assert modal._sections[0] == {"type": "text", "content": "First paragraph"}
    assert modal._sections[1] == {"type": "text", "content": "Second paragraph"}
    assert modal._sections[2] == {"type": "input", "placeholder": "Enter value"}


def test_builder_preserves_button_labels():
    modal = CraftModal.build("T").buttons("Yes", "No", "Maybe")
    assert modal._button_labels == ["Yes", "No", "Maybe"]


def test_modal_title_stored():
    modal = CraftModal.build("Delete item?").buttons("Delete", "Cancel")
    assert modal._title == "Delete item?"


# ── Direct construction ───────────────────────────────────────────────────────


def test_direct_construction():
    modal = CraftModal(
        title="Direct",
        sections=[{"type": "text", "content": "Hello"}],
        button_labels=["OK"],
    )
    assert modal._title == "Direct"
    assert len(modal._sections) == 1
    assert modal._button_labels == ["OK"]


def test_defaults_when_no_sections_or_buttons():
    modal = CraftModal(title="Empty")
    assert modal._sections == []
    assert modal._button_labels == ["OK"]


# ── Section types ─────────────────────────────────────────────────────────────


def test_section_types_are_correct():
    modal = (
        CraftModal.build("T")
        .section("A text")
        .input("ph")
        .buttons("OK")
    )
    assert modal._sections[0]["type"] == "text"
    assert modal._sections[1]["type"] == "input"


def test_input_section_has_placeholder():
    modal = CraftModal.build("T").input(placeholder="Type here…").buttons("OK")
    assert modal._sections[0]["placeholder"] == "Type here…"
