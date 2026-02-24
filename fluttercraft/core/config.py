from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

# ── Default schema ────────────────────────────────────────────────────────────

DEFAULT_CONFIG: dict[str, Any] = {
    "theme": {
        "name": "atom_one_dark",
        "auto_switch": False,
    },
    "workspace": {
        "recent_projects": [],
        "max_recent": 10,
    },
    "fvm": {
        "default_version": "",
        "auto_detect": True,
    },
    "editor": {
        "command": "",  # e.g. "code", "nvim", "vim"
    },
    "cli_adapters": {
        "preferred": "",  # "claude" | "gemini" | "opencode"
        "auto_detect": True,
    },
    "ui": {
        "sidebar_width": 22,
        "output_height": 10,
        "show_line_numbers": False,
    },
}

from fluttercraft.core.compat import get_config_dir

CONFIG_DIR = get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Recursively merge *override* into *base* in-place.

    Nested dicts are merged; all other values are replaced.
    Keys in *override* that are absent from *base* are added.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


# ── Config manager ────────────────────────────────────────────────────────────


class ConfigManager:
    """Persistent configuration backed by ``~/.fluttercraft/config.json``.

    * Dot-notation access: ``config.get("theme.name")``,
      ``config.set("ui.sidebar_width", 28)``
    * Deep-merges the user file over :data:`DEFAULT_CONFIG` on load —
      missing keys always fall back to defaults.
    * Thread-safe: a single :class:`threading.Lock` guards all reads/writes.
    * Silent degradation: a corrupt or missing config file falls back to
      defaults without raising.

    Usage::

        cfg = ConfigManager()
        cfg.get("theme.name")          # "atom_one_dark"
        cfg.set("theme.name", "dracula")
        cfg.save()
    """

    def __init__(self, path: Path = CONFIG_FILE) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {}
        self._load()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load config from disk, deep-merging over defaults."""
        with self._lock:
            self._data = deepcopy(DEFAULT_CONFIG)
            if self._path.exists():
                try:
                    with self._path.open("r", encoding="utf-8") as fh:
                        user = json.load(fh)
                    if isinstance(user, dict):
                        _deep_merge(self._data, user)
                except (json.JSONDecodeError, OSError):
                    pass  # Silent degradation — keep defaults

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value at *key* (dot-notation).

        Returns *default* if any segment of the path is missing.
        """
        with self._lock:
            node: Any = self._data
            for part in key.split("."):
                if not isinstance(node, dict) or part not in node:
                    return default
                node = node[part]
            return node

    def set(self, key: str, value: Any) -> None:
        """Set the value at *key* (dot-notation).

        Intermediate dicts are created automatically.
        """
        with self._lock:
            parts = key.split(".")
            node = self._data
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value

    def save(self) -> None:
        """Write current config to disk, creating the directory if needed."""
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2)

    def reload(self) -> None:
        """Re-read the config file from disk."""
        self._load()

    def reset(self) -> None:
        """Reset all values to defaults (does not save automatically)."""
        with self._lock:
            self._data = deepcopy(DEFAULT_CONFIG)

    def all(self) -> dict[str, Any]:
        """Return a deep copy of the full config dict."""
        with self._lock:
            return deepcopy(self._data)
