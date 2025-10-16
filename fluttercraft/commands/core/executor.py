from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from rich.console import Console

from .base import Command
from .models import CommandContext, CommandResult
from .registry import CommandRegistry


@dataclass(slots=True)
class CommandExecutor:
    """Coordinates command lookup, execution, and error handling."""

    registry: CommandRegistry
    console: Console

    def dispatch(self, raw_command: str, context: CommandContext) -> CommandResult:
        normalized = raw_command.strip()
        if not normalized:
            return CommandResult(success=True)

        tokens = normalized.split()
        command_token = tokens[0]
        args = tokens[1:]

        command = self._resolve_command(command_token)
        if not command:
            return CommandResult(
                success=False,
                message=f"✗ Unknown command: {command_token}",
                should_continue=True,
            )

        try:
            return command.execute(context, args)
        except Exception as exc:  # noqa: BLE001
            self.console.print(
                f"\n[bold red]An error occurred while running '{command_token}': {exc}[/]"
            )
            return CommandResult(success=False, should_continue=True)

    def _resolve_command(self, token: str) -> Optional[Command]:
        # For slash commands we accept exact token
        if token.startswith("/"):
            return self.registry.get(token)

        # Try direct lookup
        command = self.registry.get(token)
        if command:
            return command

        return None
