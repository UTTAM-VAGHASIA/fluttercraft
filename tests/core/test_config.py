from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from fluttercraft.core.config import ConfigManager, DEFAULT_CONFIG, _deep_merge


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def cfg(tmp_path: Path) -> ConfigManager:
    """A ConfigManager pointed at a temporary directory (no real disk writes)."""
    return ConfigManager(path=tmp_path / "config.json")


# ── Default loading ───────────────────────────────────────────────────────────


def test_defaults_loaded_when_no_file(cfg: ConfigManager):
    assert cfg.get("theme.name") == DEFAULT_CONFIG["theme"]["name"]
    assert cfg.get("ui.sidebar_width") == DEFAULT_CONFIG["ui"]["sidebar_width"]


def test_all_returns_full_dict(cfg: ConfigManager):
    data = cfg.all()
    assert isinstance(data, dict)
    assert "theme" in data
    assert "ui" in data


def test_all_returns_deep_copy(cfg: ConfigManager):
    data = cfg.all()
    data["theme"]["name"] = "mutated"
    assert cfg.get("theme.name") == DEFAULT_CONFIG["theme"]["name"]


# ── get ───────────────────────────────────────────────────────────────────────


def test_get_top_level_key(cfg: ConfigManager):
    assert isinstance(cfg.get("theme"), dict)


def test_get_nested_key(cfg: ConfigManager):
    assert cfg.get("fvm.auto_detect") is True


def test_get_missing_key_returns_none(cfg: ConfigManager):
    assert cfg.get("nonexistent") is None


def test_get_missing_nested_key_returns_default(cfg: ConfigManager):
    assert cfg.get("theme.does_not_exist", "fallback") == "fallback"


def test_get_partial_path_missing(cfg: ConfigManager):
    assert cfg.get("a.b.c.d") is None


# ── set ───────────────────────────────────────────────────────────────────────


def test_set_existing_key(cfg: ConfigManager):
    cfg.set("theme.name", "dracula")
    assert cfg.get("theme.name") == "dracula"


def test_set_nested_key(cfg: ConfigManager):
    cfg.set("ui.sidebar_width", 30)
    assert cfg.get("ui.sidebar_width") == 30


def test_set_creates_intermediate_dicts(cfg: ConfigManager):
    cfg.set("new.deep.key", "value")
    assert cfg.get("new.deep.key") == "value"


def test_set_new_top_level_key(cfg: ConfigManager):
    cfg.set("custom", 42)
    assert cfg.get("custom") == 42


# ── save / reload roundtrip ───────────────────────────────────────────────────


def test_save_writes_file(tmp_path: Path):
    path = tmp_path / "config.json"
    cfg = ConfigManager(path=path)
    cfg.set("theme.name", "monokai")
    cfg.save()

    assert path.exists()
    with path.open() as fh:
        data = json.load(fh)
    assert data["theme"]["name"] == "monokai"


def test_reload_reads_updated_file(tmp_path: Path):
    path = tmp_path / "config.json"

    # Write a config file manually
    path.write_text(json.dumps({"theme": {"name": "solarized"}}))

    cfg = ConfigManager(path=path)
    assert cfg.get("theme.name") == "solarized"
    # Other defaults still present
    assert cfg.get("ui.sidebar_width") == DEFAULT_CONFIG["ui"]["sidebar_width"]


def test_save_reload_roundtrip(tmp_path: Path):
    path = tmp_path / "config.json"
    cfg = ConfigManager(path=path)
    cfg.set("theme.name", "nord")
    cfg.set("ui.output_height", 15)
    cfg.save()

    cfg2 = ConfigManager(path=path)
    assert cfg2.get("theme.name") == "nord"
    assert cfg2.get("ui.output_height") == 15


# ── deep merge ────────────────────────────────────────────────────────────────


def test_deep_merge_overrides_leaf():
    base = {"a": {"b": 1, "c": 2}}
    _deep_merge(base, {"a": {"b": 99}})
    assert base == {"a": {"b": 99, "c": 2}}


def test_deep_merge_adds_missing_keys():
    base = {"a": 1}
    _deep_merge(base, {"b": 2})
    assert base == {"a": 1, "b": 2}


def test_deep_merge_replaces_non_dict_with_dict():
    base = {"a": 1}
    _deep_merge(base, {"a": {"nested": True}})
    assert base["a"] == {"nested": True}


def test_user_file_only_overrides_specified_keys(tmp_path: Path):
    path = tmp_path / "config.json"
    # User file only sets theme.name; all other defaults must survive
    path.write_text(json.dumps({"theme": {"name": "custom"}}))
    cfg = ConfigManager(path=path)

    assert cfg.get("theme.name") == "custom"
    assert cfg.get("theme.auto_switch") == DEFAULT_CONFIG["theme"]["auto_switch"]
    assert cfg.get("fvm.auto_detect") == DEFAULT_CONFIG["fvm"]["auto_detect"]


# ── error handling ────────────────────────────────────────────────────────────


def test_corrupt_json_falls_back_to_defaults(tmp_path: Path):
    path = tmp_path / "config.json"
    path.write_text("{ not valid json !!!}")

    cfg = ConfigManager(path=path)
    assert cfg.get("theme.name") == DEFAULT_CONFIG["theme"]["name"]


def test_reset_restores_defaults(cfg: ConfigManager):
    cfg.set("theme.name", "changed")
    cfg.reset()
    assert cfg.get("theme.name") == DEFAULT_CONFIG["theme"]["name"]


# ── thread safety ─────────────────────────────────────────────────────────────


def test_concurrent_set_does_not_crash(cfg: ConfigManager):
    errors = []

    def worker(i: int):
        try:
            cfg.set(f"ui.sidebar_width", i)
            _ = cfg.get("ui.sidebar_width")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
