from __future__ import annotations

import pytest

from fluttercraft.core.keymap import KeyBinding, KeymapRegistry


# ── KeyBinding dataclass ──────────────────────────────────────────────────────


def test_keybinding_fields():
    kb = KeyBinding(key="ctrl+p", action="command_palette", description="Open palette")
    assert kb.key == "ctrl+p"
    assert kb.action == "command_palette"
    assert kb.description == "Open palette"
    assert kb.context == "global"


def test_keybinding_custom_context():
    kb = KeyBinding(key="r", action="fvm_refresh", description="Refresh", context="fvm")
    assert kb.context == "fvm"


# ── KeymapRegistry ────────────────────────────────────────────────────────────


def test_register_and_resolve_global():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "command_palette", "Palette"))
    assert km.resolve("ctrl+p") == "command_palette"


def test_resolve_unknown_key_returns_none():
    km = KeymapRegistry()
    assert km.resolve("ctrl+x") is None


def test_resolve_context_specific():
    km = KeymapRegistry()
    km.register(KeyBinding("r", "fvm_refresh", "Refresh FVM", context="fvm"))
    # Found in fvm context
    assert km.resolve("r", "fvm") == "fvm_refresh"
    # Not found in different context
    assert km.resolve("r", "git") is None
    # Not found globally (context "global" doesn't match "fvm")
    assert km.resolve("r") is None


def test_resolve_global_binding_visible_in_all_contexts():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+q", "quit", "Quit"))
    assert km.resolve("ctrl+q", "fvm") == "quit"
    assert km.resolve("ctrl+q", "git") == "quit"
    assert km.resolve("ctrl+q") == "quit"


def test_register_duplicate_replaces():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette_v1", "Old"))
    km.register(KeyBinding("ctrl+p", "palette_v2", "New"))
    assert km.resolve("ctrl+p") == "palette_v2"
    # Only one binding should exist
    bindings = [b for b in km.all_bindings() if b.key == "ctrl+p"]
    assert len(bindings) == 1


def test_register_many():
    km = KeymapRegistry()
    km.register_many([
        KeyBinding("ctrl+p", "palette", "Palette"),
        KeyBinding("ctrl+t", "theme", "Theme"),
    ])
    assert km.resolve("ctrl+p") == "palette"
    assert km.resolve("ctrl+t") == "theme"


def test_get_bindings_global_only():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette", "Palette", context="global"))
    km.register(KeyBinding("r", "refresh", "Refresh", context="fvm"))
    global_bindings = km.get_bindings("global")
    keys = [b.key for b in global_bindings]
    assert "ctrl+p" in keys
    assert "r" not in keys


def test_get_bindings_includes_global_and_context():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette", "Palette", context="global"))
    km.register(KeyBinding("r", "refresh", "Refresh", context="fvm"))
    km.register(KeyBinding("d", "diff", "Diff", context="git"))
    fvm_bindings = km.get_bindings("fvm")
    keys = [b.key for b in fvm_bindings]
    assert "ctrl+p" in keys   # global
    assert "r" in keys         # fvm context
    assert "d" not in keys     # git context — excluded


def test_override_remaps_key():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette", "Palette"))
    km.override("ctrl+p", "ctrl+shift+p")
    # Original key no longer works
    assert km.resolve("ctrl+p") is None
    # New key works
    assert km.resolve("ctrl+shift+p") == "palette"


def test_clear_override_restores_default():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette", "Palette"))
    km.override("ctrl+p", "ctrl+shift+p")
    km.clear_override("ctrl+p")
    assert km.resolve("ctrl+p") == "palette"


def test_override_persists_to_config():
    from unittest.mock import MagicMock
    config = MagicMock()
    km = KeymapRegistry(config)
    km.register(KeyBinding("ctrl+p", "palette", "Palette"))
    km.override("ctrl+p", "ctrl+shift+p")
    config.set.assert_called_with("keymap.overrides", {"ctrl+p": "ctrl+shift+p"})


def test_loads_overrides_from_config():
    from unittest.mock import MagicMock
    config = MagicMock()
    config.get.return_value = {"ctrl+p": "ctrl+shift+p"}
    km = KeymapRegistry(config)
    km.register(KeyBinding("ctrl+p", "palette", "Palette"))
    # The override loaded from config remaps ctrl+p to ctrl+shift+p
    assert km.resolve("ctrl+p") is None
    assert km.resolve("ctrl+shift+p") == "palette"


def test_all_bindings_returns_copy():
    km = KeymapRegistry()
    km.register(KeyBinding("ctrl+p", "palette", "Palette"))
    bindings = km.all_bindings()
    assert len(bindings) == 1
    # Mutating the returned list doesn't affect the registry
    bindings.clear()
    assert len(km.all_bindings()) == 1
