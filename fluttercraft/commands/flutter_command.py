from __future__ import annotations

from typing import List

from rich.console import Console

from fluttercraft.commands.core.base import Command
from fluttercraft.commands.core.models import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from fluttercraft.commands.flutter.version import check_flutter_version
from fluttercraft.utils.terminal_utils import run_with_loading
from fluttercraft.utils.themed_display import (
    display_themed_help,
    format_text,
)
from fluttercraft.utils.beautiful_display import update_system_info


class FlutterCommand(Command):
    """Handle Flutter CLI interactions within FlutterCraft."""

    def __init__(self) -> None:
        metadata = CommandMetadata(
            name="flutter",
            help_text="Run Flutter-related operations",
            category="flutter",
            keywords=("flutter", "upgrade", "sdk"),
            aliases=(),
        )
        super().__init__(metadata)

    def execute(self, context: CommandContext, args: List[str]) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message=format_text(
                    "warning", "Usage: flutter <command>. Try 'flutter upgrade'."
                ),
            )

        subcommand = args[0].lower()
        remaining = args[1:]

        if subcommand == "upgrade":
            return self._handle_upgrade(context, remaining)

        if subcommand in {"help", "--help", "-h"}:
            display_themed_help()
            return CommandResult(success=True)

        return CommandResult(
            success=False,
            message=format_text(
                "warning",
                (
                    f"⚠ Flutter command '{subcommand}' is not yet implemented.\n"
                    "Currently supported: flutter upgrade"
                ),
            ),
        )

    def _handle_upgrade(
        self, context: CommandContext, args: List[str]
    ) -> CommandResult:
        console: Console = context.console

        additional_params = args
        is_verify_only = "--verify-only" in additional_params

        if additional_params:
            console.print(
                format_text(
                    "warning",
                    "Executing Flutter upgrade with parameters: "
                    + " ".join(additional_params),
                    bold=True,
                )
            )

        cmd = ["flutter", "upgrade", *additional_params]
        status_message = (
            format_text("warning", "Checking for Flutter updates...", bold=True)
            if is_verify_only
            else format_text("warning", "Upgrading Flutter...", bold=True)
        )

        result = run_with_loading(
            cmd,
            status_message=status_message,
            should_display_command=True,
            clear_on_success=False,
            show_output_on_failure=True,
            show_status_message=True,
        )

        if result.returncode != 0:
            console.print(
                format_text(
                    "error", "✗ Flutter upgrade command failed!", bold=True
                )
            )
            return CommandResult(success=False)

        if is_verify_only:
            console.print(
                format_text(
                    "success", "✓ Flutter update check completed!", bold=True
                )
            )
        else:
            console.print(
                format_text(
                    "success", "✓ Flutter upgrade completed successfully!", bold=True
                )
            )

        updated_info = check_flutter_version(silent=True)
        if updated_info != context.flutter_info:
            context.flutter_info = updated_info
            console.print(format_text("secondary", "Flutter version information refreshed."))
            update_system_info(
                context.platform_info, context.flutter_info, context.fvm_info
            )

        return CommandResult(success=True)
