"""
Settings Slash Command.
"""
from typing import List

from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from fluttercraft.commands.settings.settings_command import SettingsCommand

class SettingsSlashCommand(Command):
    """
    Slash command wrapper for Settings.
    Alias: /settings, /config
    """

    def __init__(self) -> None:
        metadata = CommandMetadata(
            name="/settings",
            help_text="Open configuration panel",
            category="core",
            keywords=("config", "options"),
            aliases=("/config",),
        )
        super().__init__(metadata)
        self._impl = SettingsCommand()

    def execute(self, context: CommandContext, args: List[str]) -> CommandResult:
        return self._impl.execute(context, args)
