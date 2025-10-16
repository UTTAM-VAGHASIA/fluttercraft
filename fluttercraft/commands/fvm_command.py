from __future__ import annotations

from typing import List, Optional

from rich.console import Console

from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from fluttercraft.commands.fvm import (
    fvm_install_command,
    fvm_list_command,
    fvm_releases_command,
    fvm_uninstall_command,
)
from fluttercraft.commands.help import (
    show_fvm_help,
    show_fvm_install_help,
    show_fvm_list_help,
    show_fvm_releases_help,
    show_fvm_uninstall_help,
)
from fluttercraft.utils.beautiful_display import update_system_info


class FVMCommand(Command):
    """Aggregates FVM-related subcommands under a single entry point."""

    def __init__(self) -> None:
        metadata = CommandMetadata(
            name="fvm",
            help_text="Manage Flutter SDK versions through FVM",
            category="fvm",
            keywords=("flutter", "sdk", "version", "manager"),
            aliases=(),
        )
        super().__init__(metadata)

    def execute(self, context: CommandContext, args: List[str]) -> CommandResult:
        if not args:
            show_fvm_help()
            return CommandResult(success=True)

        subcommand = args[0].lower()
        remaining = args[1:]

        if subcommand == "install":
            return self._handle_install(context)
        if subcommand == "uninstall":
            return self._handle_uninstall(context)
        if subcommand == "releases":
            return self._handle_releases(context.console, remaining)
        if subcommand == "list":
            return self._handle_list(context.console)
        if subcommand in {"help", "--help", "-h"}:
            show_fvm_help()
            return CommandResult(success=True)

        # Contextual help: e.g. "fvm install help"
        if len(remaining) == 1 and remaining[0] in {"help", "--help", "-h"}:
            return self._handle_help_for_subcommand(subcommand)

        return CommandResult(
            success=False,
            message=f"✗ Unknown FVM command: {' '.join([subcommand, *remaining]).strip()}\n"
            "Available: install, uninstall, releases, list",
        )

    def _handle_install(self, context: CommandContext) -> CommandResult:
        updated_info, _ = fvm_install_command(
            context.platform_info, context.flutter_info, context.fvm_info
        )
        context.fvm_info = updated_info
        update_system_info(
            context.platform_info, context.flutter_info, context.fvm_info
        )
        return CommandResult(success=True)

    def _handle_uninstall(self, context: CommandContext) -> CommandResult:
        updated_info, _ = fvm_uninstall_command(
            context.platform_info, context.flutter_info, context.fvm_info
        )
        context.fvm_info = updated_info
        update_system_info(
            context.platform_info, context.flutter_info, context.fvm_info
        )
        return CommandResult(success=True)

    def _handle_releases(self, console: Console, args: List[str]) -> CommandResult:
        channel = self._parse_channel(args)
        try:
            fvm_releases_command(channel)
            return CommandResult(success=True)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bold red]Error fetching Flutter releases: {exc}[/]")
            return CommandResult(success=False)

    def _handle_list(self, console: Console) -> CommandResult:
        try:
            fvm_list_command()
            return CommandResult(success=True)
        except Exception as exc:  # noqa: BLE001
            console.print(
                f"[bold red]Error fetching installed Flutter versions: {exc}[/]"
            )
            return CommandResult(success=False)

    def _handle_help_for_subcommand(self, subcommand: str) -> CommandResult:
        if subcommand == "install":
            show_fvm_install_help()
        elif subcommand == "uninstall":
            show_fvm_uninstall_help()
        elif subcommand == "releases":
            show_fvm_releases_help()
        elif subcommand == "list":
            show_fvm_list_help()
        else:
            show_fvm_help()
        return CommandResult(success=True)

    @staticmethod
    def _parse_channel(args: List[str]) -> Optional[str]:
        if not args:
            return None

        first = args[0]
        if first in {"stable", "beta", "dev", "all"}:
            return first

        for token in args:
            if token.startswith("--channel="):
                return token.split("=", 1)[1]

        if len(args) >= 2 and args[0] in {"--channel", "-c"}:
            return args[1]

        return None
