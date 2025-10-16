"""Start command for FlutterCraft CLI with beautiful interface."""

import time

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from prompt_toolkit.history import InMemoryHistory

from fluttercraft.utils.platform_utils import get_platform_info
from fluttercraft.utils.beautiful_display import show_platform_not_supported
from fluttercraft.utils.themed_display import (
    display_themed_welcome_header,
    create_themed_ascii_art,
    clear_screen,
)
from fluttercraft.utils.beautiful_prompt import (
    prompt_user_with_border,
    FlutterCraftCompleter,
    update_command_completions,
)
from fluttercraft.commands.flutter_commands import check_flutter_version
from fluttercraft.commands.fvm_commands import check_fvm_version
from fluttercraft.commands.core import CommandContext
from fluttercraft.commands.bootstrap import build_command_system

console = Console()


def start_command():
    """
    Start the interactive CLI session with beautiful interface.
    This is the main command that users will use to start creating Flutter apps.
    """
    import platform

    # Check platform first
    current_platform = platform.system()

    # If macOS or Linux, show coming soon message
    if current_platform in ["Darwin", "Linux"]:
        show_platform_not_supported(current_platform)
        return

    # Show themed ASCII art
    ascii_art = create_themed_ascii_art()
    console.print(ascii_art)
    console.print()

    # Show loading spinner
    spinner = Spinner("dots", text="[cyan]Loading system information...[/]")
    with Live(spinner, console=console, refresh_per_second=10):
        # Get platform information (fast, no external calls)
        platform_info = get_platform_info()
        time.sleep(0.3)  # Small delay to show spinner

        # Check Flutter installation and version (silent mode)
        flutter_info = check_flutter_version(silent=True)
        time.sleep(0.3)  # Small delay to show spinner

        # Check FVM installation (silent mode)
        fvm_info = check_fvm_version(silent=True)
        time.sleep(0.3)  # Small delay to show spinner

    # Clear screen and display themed static header
    clear_screen()
    display_themed_welcome_header(
        platform_info, flutter_info, fvm_info, show_ascii=True
    )

    # Create completer and history for bordered prompt
    completer = FlutterCraftCompleter()
    history = InMemoryHistory()

    executor = build_command_system(console)
    update_command_completions(executor.registry.to_metadata())

    context = CommandContext(
        platform_info=platform_info,
        flutter_info=flutter_info,
        fvm_info=fvm_info,
        console=console,
        prompt_history=history,
    )

    # Main REPL loop
    while True:
        try:
            # Get user input with beautiful bordered prompt
            command = prompt_user_with_border(completer, history)

            # Execute command
            result = executor.dispatch(command, context)

            if result.message:
                console.print(result.message)

            if not result.should_continue:
                break

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n[yellow]Use '/quit' to exit FlutterCraft[/]")
            continue

        except EOFError:
            # Handle Ctrl+D as quit
            console.print("\n[yellow]Thank you for using FlutterCraft! Goodbye! 👋[/]")
            break

        except Exception as e:
            # Handle unexpected errors
            console.print(f"\n[bold red]An error occurred: {str(e)}[/]")
            console.print("[dim]Please report this issue if it persists.[/]")
            continue
