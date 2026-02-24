from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from fluttercraft.core.state import (
    DEFAULT_GLOBAL_STATE,
    DEFAULT_PROJECT_STATE,
    StateManager,
)

PROJECT_A = "/home/user/my_app"
PROJECT_B = "/home/user/other_app"


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def state(tmp_path: Path) -> StateManager:
    return StateManager(path=tmp_path / "state.json")


# ── Default loading ───────────────────────────────────────────────────────────


def test_defaults_when_no_file(state: StateManager):
    assert state.get("last_project") == DEFAULT_GLOBAL_STATE["last_project"]
    assert state.get("recent_projects") == DEFAULT_GLOBAL_STATE["recent_projects"]


def test_project_defaults_on_first_access(state: StateManager):
    assert state.get_project(PROJECT_A, "active_plugin") == DEFAULT_PROJECT_STATE["active_plugin"]
    assert state.get_project(PROJECT_A, "sidebar_width") == DEFAULT_PROJECT_STATE["sidebar_width"]


# ── Global state ──────────────────────────────────────────────────────────────


def test_set_and_get_global(state: StateManager):
    state.set("last_project", PROJECT_A)
    assert state.get("last_project") == PROJECT_A


def test_get_missing_global_returns_none(state: StateManager):
    assert state.get("nonexistent") is None


def test_get_missing_global_returns_custom_default(state: StateManager):
    assert state.get("nonexistent", "fallback") == "fallback"


def test_set_global_nested_key(state: StateManager):
    state.set("deeply.nested.key", 42)
    assert state.get("deeply.nested.key") == 42


def test_set_global_overwrites(state: StateManager):
    state.set("last_project", PROJECT_A)
    state.set("last_project", PROJECT_B)
    assert state.get("last_project") == PROJECT_B


# ── Per-project state ─────────────────────────────────────────────────────────


def test_set_and_get_project(state: StateManager):
    state.set_project(PROJECT_A, "active_plugin", "git")
    assert state.get_project(PROJECT_A, "active_plugin") == "git"


def test_get_project_missing_key_returns_none(state: StateManager):
    assert state.get_project(PROJECT_A, "no_such_key") is None


def test_get_project_missing_key_returns_default(state: StateManager):
    assert state.get_project(PROJECT_A, "no_such_key", "fallback") == "fallback"


def test_multiple_projects_independent(state: StateManager):
    state.set_project(PROJECT_A, "active_plugin", "fvm")
    state.set_project(PROJECT_B, "active_plugin", "git")

    assert state.get_project(PROJECT_A, "active_plugin") == "fvm"
    assert state.get_project(PROJECT_B, "active_plugin") == "git"


def test_set_project_creates_entry(state: StateManager):
    assert PROJECT_A not in state.project_keys()
    state.set_project(PROJECT_A, "sidebar_width", 30)
    assert PROJECT_A in state.project_keys()


def test_project_keys_lists_all_projects(state: StateManager):
    state.set_project(PROJECT_A, "active_plugin", "fvm")
    state.set_project(PROJECT_B, "active_plugin", "git")
    keys = state.project_keys()
    assert PROJECT_A in keys
    assert PROJECT_B in keys


# ── Persistence ───────────────────────────────────────────────────────────────


def test_save_creates_file(tmp_path: Path):
    path = tmp_path / "state.json"
    s = StateManager(path=path)
    s.save()
    assert path.exists()


def test_save_writes_correct_structure(tmp_path: Path):
    path = tmp_path / "state.json"
    s = StateManager(path=path)
    s.set("last_project", PROJECT_A)
    s.set_project(PROJECT_A, "active_plugin", "git")
    s.save()

    with path.open() as fh:
        data = json.load(fh)

    assert data["global"]["last_project"] == PROJECT_A
    assert data["projects"][PROJECT_A]["active_plugin"] == "git"


def test_reload_reads_updated_file(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({
        "global": {"last_project": PROJECT_B, "recent_projects": []},
        "projects": {},
    }))
    s = StateManager(path=path)
    assert s.get("last_project") == PROJECT_B


def test_save_reload_roundtrip_global(tmp_path: Path):
    path = tmp_path / "state.json"
    s = StateManager(path=path)
    s.set("last_project", PROJECT_A)
    s.save()

    s2 = StateManager(path=path)
    assert s2.get("last_project") == PROJECT_A


def test_save_reload_roundtrip_project(tmp_path: Path):
    path = tmp_path / "state.json"
    s = StateManager(path=path)
    s.set_project(PROJECT_A, "active_plugin", "workspace")
    s.set_project(PROJECT_A, "output_height", 20)
    s.save()

    s2 = StateManager(path=path)
    assert s2.get_project(PROJECT_A, "active_plugin") == "workspace"
    assert s2.get_project(PROJECT_A, "output_height") == 20


# ── Error handling ────────────────────────────────────────────────────────────


def test_corrupt_file_falls_back_to_defaults(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text("{ not valid json !!}")

    s = StateManager(path=path)
    assert s.get("last_project") == DEFAULT_GLOBAL_STATE["last_project"]


def test_reset_clears_all_state(state: StateManager):
    state.set("last_project", PROJECT_A)
    state.set_project(PROJECT_A, "active_plugin", "git")
    state.reset()

    assert state.get("last_project") == DEFAULT_GLOBAL_STATE["last_project"]
    assert state.project_keys() == []


def test_all_returns_deep_copy(state: StateManager):
    state.set("last_project", PROJECT_A)
    snapshot = state.all()
    snapshot["global"]["last_project"] = "mutated"
    assert state.get("last_project") == PROJECT_A


# ── Thread safety ─────────────────────────────────────────────────────────────


def test_concurrent_project_writes_do_not_crash(state: StateManager):
    errors = []

    def worker(i: int):
        try:
            state.set_project(PROJECT_A, "sidebar_width", i)
            _ = state.get_project(PROJECT_A, "sidebar_width")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
