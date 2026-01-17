from __future__ import annotations

import time
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
            # Start timer
            start_time = time.perf_counter()

            # Execute command
            result = command.execute(context, args)

            # Calculate execution time
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # Add execution time to result
            # Create new result with execution_time if not already set
            if result.execution_time is None:
                result = CommandResult(
                    success=result.success,
                    message=result.message,
                    payload=result.payload,
                    should_continue=result.should_continue,
                    execution_time=execution_time,
                )

            return result
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
