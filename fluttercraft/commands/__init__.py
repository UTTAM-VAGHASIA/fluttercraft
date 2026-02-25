"""FlutterCraft command system.

Provides the core command registry, executor, and base classes used by
plugins in Phase 2+. The v0.1.x CLI commands have been removed.
"""
from __future__ import annotations

from fluttercraft.commands.core import (
    Command,
    CommandContext,
    CommandExecutor,
    CommandMetadata,
    CommandRegistry,
    CommandResult,
)

__all__ = [
    "Command",
    "CommandContext",
    "CommandExecutor",
    "CommandMetadata",
    "CommandRegistry",
    "CommandResult",
]
