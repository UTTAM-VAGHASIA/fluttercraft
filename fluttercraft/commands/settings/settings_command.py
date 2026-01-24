"""
Settings command implementation.
"""
from typing import List

from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)

class SettingsCommand(Command):
    """Open the interactive settings panel."""

    def __init__(self) -> None:
        metadata = CommandMetadata(
            name="settings",
            help_text="Open the interactive configuration panel",
            category="core",
            keywords=("config", "preferences", "options"),
            aliases=("config",),
        )
        super().__init__(metadata)

    def execute(self, context: CommandContext, args: List[str]) -> CommandResult:
        try:
            from fluttercraft.commands.settings.settings_ui import SettingsUI
            ui = SettingsUI(context.console)
            ui.show()
            
            return CommandResult(
                success=True,
                message="Configuration saved."
            )
        except Exception as e:
            context.console.print(f"[bold red]Failed to open settings: {e}[/]")
            return CommandResult(success=False)
