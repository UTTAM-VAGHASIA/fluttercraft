from __future__ import annotations

import shutil

from fluttercraft.adapters.base import CLIAdapter


def detect_adapters(adapters: list[CLIAdapter]) -> list[CLIAdapter]:
    """Return only the adapters whose backing binary exists on PATH."""
    return [a for a in adapters if a.detect()]


def binary_on_path(name: str) -> bool:
    """Return True if *name* is found via shutil.which."""
    return shutil.which(name) is not None
