from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass(slots=True)
class CommandContext:
    """Runtime context passed to commands."""

    platform_info: Dict[str, Any]
    flutter_info: Dict[str, Any]
    fvm_info: Dict[str, Any]
    console: Any
    prompt_history: Any
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CommandResult:
    """Canonical outcome of a command execution."""

    success: bool
    message: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    should_continue: bool = True


@dataclass(slots=True)
class CommandMetadata:
    """Declarative metadata for CLI commands."""

    name: str
    help_text: str
    category: str
    keywords: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    handler: Optional[Callable[[CommandContext], CommandResult]] = None
