from __future__ import annotations

from rich.console import Console

from fluttercraft.utils.themed_display import (
    display_themed_about,
    display_themed_help,
    display_themed_welcome_header,
)

from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)


class SlashCommand(Command):
    """Base slash command with shared helpers."""

    def __init__(self, name: str, help_text: str) -> None:
        metadata = CommandMetadata(
            name=name,
            help_text=help_text,
            category="slash",
            keywords=("slash", "utility"),
        )
        super().__init__(metadata)

    def _print(self, console: Console, message: str) -> None:
        console.print(message)


class QuitSlashCommand(SlashCommand):
    def __init__(self) -> None:
        super().__init__("/quit", "Exit FlutterCraft CLI")

    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        self._print(
            context.console, "[yellow]Thank you for using FlutterCraft! Goodbye! 👋[/]"
        )
        return CommandResult(success=True, should_continue=False)


class ClearSlashCommand(SlashCommand):
    def __init__(self) -> None:
        super().__init__("/clear", "Clear the screen and redraw the header")

    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        display_themed_welcome_header(
            context.platform_info,
            context.flutter_info,
            context.fvm_info,
            show_ascii=True,
        )
        return CommandResult(success=True)


class HelpSlashCommand(SlashCommand):
    def __init__(self) -> None:
        super().__init__("/help", "Show help information")

    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        display_themed_help()
        return CommandResult(success=True)


class AboutSlashCommand(SlashCommand):
    def __init__(self) -> None:
        super().__init__("/about", "Show information about FlutterCraft")

    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        display_themed_about()
        return CommandResult(success=True)


class ThemeSlashCommand(SlashCommand):
    def __init__(self) -> None:
        super().__init__("/theme", "Launch the interactive theme selector")

    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        from fluttercraft.commands.theme.interactive_selector import (
            run_interactive_theme_selector,
        )

        run_interactive_theme_selector()
        display_themed_welcome_header(
            context.platform_info,
            context.flutter_info,
            context.fvm_info,
            show_ascii=True,
        )
        return CommandResult(success=True)
