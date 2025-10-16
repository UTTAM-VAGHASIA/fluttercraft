from __future__ import annotations

from rich.console import Console

from .core import CommandRegistry, CommandExecutor
from .slash_commands import (
    AboutSlashCommand,
    ClearSlashCommand,
    HelpSlashCommand,
    QuitSlashCommand,
    ThemeSlashCommand,
)
from .fvm_command import FVMCommand
from .flutter_command import FlutterCommand


def build_command_system(console: Console) -> CommandExecutor:
    """Create the default command registry and executor."""

    registry = CommandRegistry()

    # Slash commands
    registry.register(QuitSlashCommand())
    registry.register(ClearSlashCommand())
    registry.register(HelpSlashCommand())
    registry.register(AboutSlashCommand())
    registry.register(ThemeSlashCommand())

    # Core command families
    registry.register(FVMCommand())
    registry.register(FlutterCommand())

    return CommandExecutor(registry=registry, console=console)
