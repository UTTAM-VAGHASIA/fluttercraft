from __future__ import annotations

from typing import Any


# ── Built-in defaults ─────────────────────────────────────────────────────────

DEFAULT_FLAGS: dict[str, bool] = {
    "command_palette": True,
    "notifications": True,
    "animations": True,
    "file_watching": True,
    # Per-plugin toggles
    "plugin_fvm": True,
    "plugin_flutter": True,
    "plugin_git": True,
    "plugin_project": True,
    "plugin_files": True,
    "plugin_workspace": True,
    "plugin_cli": True,
}


# ── Feature flag system ───────────────────────────────────────────────────────


class FeatureFlags:
    """Runtime feature flag system.

    Flags are loaded from ``config["features.*"]`` at startup and can be
    toggled in-process at any time (changes are NOT automatically persisted
    unless you call :meth:`save`).

    Resolution order for :meth:`is_enabled`:
        1. Runtime toggle (set via :meth:`enable` / :meth:`disable`)
        2. Config value (``features.<flag>`` in config.json)
        3. Built-in default from :data:`DEFAULT_FLAGS` (``True`` if unknown)

    Usage::

        flags = FeatureFlags(config)
        flags.is_enabled("command_palette")   # True
        flags.disable("animations")
        flags.is_enabled("animations")        # False
        flags.enable("animations")
        flags.toggle("file_watching")         # returns new state
    """

    def __init__(self, config: Any = None) -> None:
        self._config = config
        self._config_values: dict[str, bool] = {}
        self._runtime: dict[str, bool] = {}
        self._load_from_config()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load_from_config(self) -> None:
        if self._config is None:
            return
        for flag in DEFAULT_FLAGS:
            try:
                val = self._config.get(f"features.{flag}")
                if isinstance(val, bool):
                    self._config_values[flag] = val
            except Exception:
                pass

    # ── Public API ────────────────────────────────────────────────────────────

    def is_enabled(self, flag: str) -> bool:
        """Return ``True`` if *flag* is currently enabled."""
        if flag in self._runtime:
            return self._runtime[flag]
        if flag in self._config_values:
            return self._config_values[flag]
        return DEFAULT_FLAGS.get(flag, True)

    def enable(self, flag: str) -> None:
        """Enable *flag* at runtime."""
        self._runtime[flag] = True

    def disable(self, flag: str) -> None:
        """Disable *flag* at runtime."""
        self._runtime[flag] = False

    def toggle(self, flag: str) -> bool:
        """Toggle *flag* and return the new state."""
        new_state = not self.is_enabled(flag)
        self._runtime[flag] = new_state
        return new_state

    def save(self) -> None:
        """Persist current runtime overrides to config (if config is available)."""
        if self._config is None:
            return
        for flag, value in self._runtime.items():
            try:
                self._config.set(f"features.{flag}", value)
            except Exception:
                pass

    def all_flags(self) -> dict[str, bool]:
        """Return the effective state of every known flag."""
        return {flag: self.is_enabled(flag) for flag in DEFAULT_FLAGS}
