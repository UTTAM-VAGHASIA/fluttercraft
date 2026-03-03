from __future__ import annotations

import pytest

from fluttercraft.core.features import DEFAULT_FLAGS, FeatureFlags


# ── Default state ─────────────────────────────────────────────────────────────


def test_all_defaults_are_enabled():
    flags = FeatureFlags()
    for flag in DEFAULT_FLAGS:
        assert flags.is_enabled(flag) is True, f"{flag!r} should default to True"


def test_unknown_flag_defaults_to_true():
    flags = FeatureFlags()
    assert flags.is_enabled("nonexistent_feature") is True


# ── Runtime enable / disable ──────────────────────────────────────────────────


def test_disable():
    flags = FeatureFlags()
    flags.disable("animations")
    assert flags.is_enabled("animations") is False


def test_enable_after_disable():
    flags = FeatureFlags()
    flags.disable("animations")
    flags.enable("animations")
    assert flags.is_enabled("animations") is True


def test_toggle_false_to_true():
    flags = FeatureFlags()
    flags.disable("notifications")
    result = flags.toggle("notifications")
    assert result is True
    assert flags.is_enabled("notifications") is True


def test_toggle_true_to_false():
    flags = FeatureFlags()
    result = flags.toggle("command_palette")
    assert result is False
    assert flags.is_enabled("command_palette") is False


def test_toggle_returns_new_state():
    flags = FeatureFlags()
    initial = flags.is_enabled("file_watching")
    new_state = flags.toggle("file_watching")
    assert new_state is not initial


# ── Config-driven flags ───────────────────────────────────────────────────────


def test_config_values_override_defaults():
    from unittest.mock import MagicMock
    config = MagicMock()
    config.get.side_effect = lambda key, *_: False if key == "features.animations" else None
    flags = FeatureFlags(config)
    assert flags.is_enabled("animations") is False


def test_runtime_overrides_config():
    from unittest.mock import MagicMock
    config = MagicMock()
    config.get.side_effect = lambda key, *_: False if key == "features.animations" else None
    flags = FeatureFlags(config)
    flags.enable("animations")  # runtime override wins
    assert flags.is_enabled("animations") is True


def test_config_get_exception_silently_ignored():
    from unittest.mock import MagicMock
    config = MagicMock()
    config.get.side_effect = RuntimeError("db gone")
    flags = FeatureFlags(config)  # must not raise
    assert flags.is_enabled("command_palette") is True  # falls back to default


# ── all_flags ─────────────────────────────────────────────────────────────────


def test_all_flags_returns_all_known():
    flags = FeatureFlags()
    all_flags = flags.all_flags()
    for flag in DEFAULT_FLAGS:
        assert flag in all_flags


def test_all_flags_reflects_runtime_changes():
    flags = FeatureFlags()
    flags.disable("animations")
    all_flags = flags.all_flags()
    assert all_flags["animations"] is False


# ── save ──────────────────────────────────────────────────────────────────────


def test_save_persists_runtime_to_config():
    from unittest.mock import MagicMock
    config = MagicMock()
    config.get.return_value = None
    flags = FeatureFlags(config)
    flags.disable("animations")
    flags.save()
    config.set.assert_any_call("features.animations", False)


def test_save_with_no_config_is_noop():
    flags = FeatureFlags(config=None)
    flags.disable("animations")
    flags.save()  # must not raise
