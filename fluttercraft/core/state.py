from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

# ── Default schemas ───────────────────────────────────────────────────────────

DEFAULT_GLOBAL_STATE: dict[str, Any] = {
    "last_project": "",
    "recent_projects": [],  # list of abs path strings, newest first
}

DEFAULT_PROJECT_STATE: dict[str, Any] = {
    "active_plugin": "fvm",
    "sidebar_width": 22,
    "output_height": 10,
    "selected_files": [],
}

from fluttercraft.core.compat import get_config_dir

STATE_FILE = get_config_dir() / "state.json"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _deep_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    node: Any = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def _deep_set(data: dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    node = data
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


# ── State manager ─────────────────────────────────────────────────────────────


class StateManager:
    """Persistent runtime state backed by ``~/.fluttercraft/state.json``.

    Splits into two namespaces:

    * **Global** — app-wide state (last opened project, recent project list).
    * **Per-project** — state keyed by absolute project path (active plugin,
      pane dimensions, selected files).

    Missing per-project entries are initialised from
    :data:`DEFAULT_PROJECT_STATE` on first access. All operations are
    thread-safe via a single :class:`threading.Lock`.

    Usage::

        state = StateManager()

        # Global
        state.set("last_project", "/home/user/my_app")
        state.get("last_project")

        # Per-project
        state.set_project("/home/user/my_app", "active_plugin", "git")
        state.get_project("/home/user/my_app", "active_plugin")

        state.save()
    """

    def __init__(self, path: Path = STATE_FILE) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._global: dict[str, Any] = {}
        self._projects: dict[str, dict[str, Any]] = {}
        self._load()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        with self._lock:
            self._global = deepcopy(DEFAULT_GLOBAL_STATE)
            self._projects = {}

            if self._path.exists():
                try:
                    with self._path.open("r", encoding="utf-8") as fh:
                        raw = json.load(fh)
                    if isinstance(raw, dict):
                        if isinstance(raw.get("global"), dict):
                            self._global.update(raw["global"])
                        if isinstance(raw.get("projects"), dict):
                            self._projects = raw["projects"]
                except (json.JSONDecodeError, OSError):
                    pass  # Silent degradation — keep defaults

    def _ensure_project(self, project: str) -> None:
        """Initialise per-project entry from defaults if it doesn't exist."""
        if project not in self._projects:
            self._projects[project] = deepcopy(DEFAULT_PROJECT_STATE)

    # ── Global state ──────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return global state value at dot-notation *key*."""
        with self._lock:
            return _deep_get(self._global, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set global state value at dot-notation *key*."""
        with self._lock:
            _deep_set(self._global, key, value)

    # ── Per-project state ─────────────────────────────────────────────────────

    def get_project(self, project: str, key: str, default: Any = None) -> Any:
        """Return per-project state value at *key* for *project* path.

        Initialises the project entry from defaults if it doesn't exist yet.
        """
        with self._lock:
            self._ensure_project(project)
            return _deep_get(self._projects[project], key, default)

    def set_project(self, project: str, key: str, value: Any) -> None:
        """Set per-project state value at *key* for *project* path."""
        with self._lock:
            self._ensure_project(project)
            _deep_set(self._projects[project], key, value)

    def project_keys(self) -> list[str]:
        """Return list of all project paths that have stored state."""
        with self._lock:
            return list(self._projects.keys())

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self) -> None:
        """Write current state to disk."""
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"global": self._global, "projects": self._projects}
            with self._path.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)

    def reload(self) -> None:
        """Re-read state from disk."""
        self._load()

    def reset(self) -> None:
        """Reset all state to defaults (does not save automatically)."""
        with self._lock:
            self._global = deepcopy(DEFAULT_GLOBAL_STATE)
            self._projects = {}

    def all(self) -> dict[str, Any]:
        """Return a deep copy of the full state dict."""
        with self._lock:
            return deepcopy({"global": self._global, "projects": self._projects})
