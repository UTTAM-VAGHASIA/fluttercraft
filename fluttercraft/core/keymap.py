from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ── Data type ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class KeyBinding:
    """A single keybinding entry in the registry.

    ``context`` is ``"global"`` for app-wide bindings or a plugin ID
    (e.g. ``"fvm"``) for plugin-scoped bindings.
    """

    key: str
    action: str
    description: str
    context: str = "global"


# ── Registry ─────────────────────────────────────────────────────────────────


class KeymapRegistry:
    """Central keybinding registry with user override support.

    Default bindings are registered at startup by the app and each plugin.
    Users can remap any key via :meth:`override`, which persists the mapping
    to ``config["keymap.overrides"]``.

    Resolution order:
        1. User overrides (``keymap.overrides`` in config)
        2. Registered bindings for the current context
        3. Registered global bindings

    Usage::

        km = KeymapRegistry(config)
        km.register(KeyBinding("ctrl+p", "command_palette", "Open palette"))
        km.register(KeyBinding("r", "fvm_refresh", "Refresh", context="fvm"))

        action = km.resolve("ctrl+p")          # "command_palette"
        action = km.resolve("r", "fvm")        # "fvm_refresh"
        bindings = km.get_bindings("fvm")      # global + fvm bindings
    """

    def __init__(self, config: Any = None) -> None:
        self._config = config
        self._bindings: list[KeyBinding] = []
        self._overrides: dict[str, str] = {}  # original_key → replacement_key
        self._load_overrides()

    # ── Overrides ─────────────────────────────────────────────────────────────

    def _load_overrides(self) -> None:
        if self._config is None:
            return
        try:
            overrides = self._config.get("keymap.overrides", {})
            if isinstance(overrides, dict):
                self._overrides = dict(overrides)
        except Exception:
            pass

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, binding: KeyBinding) -> None:
        """Register a keybinding.

        If a binding with the same key and context already exists it is
        replaced (last registration wins).
        """
        self._bindings = [
            b for b in self._bindings
            if not (b.key == binding.key and b.context == binding.context)
        ]
        self._bindings.append(binding)

    def register_many(self, bindings: list[KeyBinding]) -> None:
        """Register multiple bindings at once."""
        for b in bindings:
            self.register(b)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_bindings(self, context: str = "global") -> list[KeyBinding]:
        """Return all bindings active in *context* (global + context-specific)."""
        return [b for b in self._bindings if b.context in ("global", context)]

    def resolve(self, key: str, context: str = "global") -> str | None:
        """Return the action bound to *key* in *context*, or ``None``.

        Override semantics: ``override("ctrl+p", "ctrl+shift+p")`` means
        "Ctrl+Shift+P now triggers the action that was bound to Ctrl+P, and
        Ctrl+P no longer triggers anything."

        Resolution:
          1. If *key* is explicitly remapped away (it is an ``original``),
             return ``None``.
          2. If *key* is the target of a remap (it is a ``new_key``), look up
             the original key's binding instead.
          3. Otherwise look up the binding for *key* directly.
        """
        if key in self._overrides:
            # This key has been remapped to something else — it's now inactive.
            return None

        # Check if key is the destination of an override (reverse lookup)
        reverse = {new_key: orig for orig, new_key in self._overrides.items()}
        lookup_key = reverse.get(key, key)

        for b in self._bindings:
            if b.key == lookup_key and b.context in ("global", context):
                return b.action
        return None

    def all_bindings(self) -> list[KeyBinding]:
        """Return all registered bindings."""
        return list(self._bindings)

    # ── User overrides ────────────────────────────────────────────────────────

    def override(self, original_key: str, new_key: str) -> None:
        """Remap *original_key* to *new_key* and persist to config."""
        self._overrides[original_key] = new_key
        if self._config is not None:
            try:
                self._config.set("keymap.overrides", dict(self._overrides))
            except Exception:
                pass

    def clear_override(self, key: str) -> None:
        """Remove a user override, restoring the default mapping."""
        self._overrides.pop(key, None)
        if self._config is not None:
            try:
                self._config.set("keymap.overrides", dict(self._overrides))
            except Exception:
                pass
