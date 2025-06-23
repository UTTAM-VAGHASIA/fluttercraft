"""Start command for FlutterCraft CLI."""

from rich.console import Console
from rich.prompt import Prompt

from fluttercraft.utils.platform_utils import get_platform_info
from fluttercraft.utils.display_utils import (
    display_welcome_art,
    refresh_display,
    add_to_history,
    clear_command,
)
from fluttercraft.utils.terminal_utils import OutputCapture
from fluttercraft.commands.flutter_commands import check_flutter_version
from fluttercraft.commands.fvm_commands import (
    check_fvm_version,
    fvm_install_command,
    fvm_uninstall_command,
    fvm_releases_command,
)

console = Console()


def start_command():
    """
    Start the interactive CLI session.
    This is the main command that users will use to start creating Flutter apps.
    """
    # Get platform information using the utility function
    platform_info = get_platform_info()

    # Check Flutter installation and version
    flutter_info = check_flutter_version()

    # Check FVM installation
    fvm_info = check_fvm_version()

    # Display other information
    console.print("FlutterCraft CLI started!")
    console.print(f"[bold blue]Platform: {platform_info['system']}[/]")
    console.print(f"[bold blue]Shell: {platform_info['shell']}[/]")
    console.print(f"[bold blue]Python version: {platform_info['python_version']}[/]")

    # Print Flutter version
    if flutter_info["installed"]:
        if flutter_info["current_version"]:
            version_str = (
                f"[bold green]Flutter version: {flutter_info['current_version']}"
            )

            if flutter_info["latest_version"]:
                if flutter_info["current_version"] != flutter_info["latest_version"]:
                    version_str += f" [yellow](Latest version available: {flutter_info['latest_version']})[/]"
            else:
                version_str += " [green](up to date)[/]"

            console.print(version_str)
        else:
            console.print(
                "[yellow]Flutter is installed, but version could not be determined[/]"
            )
    else:
        console.print("[bold red]Flutter is not installed[/]")

    # Print FVM version
    if fvm_info["installed"]:
        console.print(f"[bold green]FVM version: {fvm_info['version']}[/]")
    else:
        console.print("[yellow]FVM is not installed[/]")

    console.print("[bold]Enter commands or type 'exit' or 'quit' or 'q' to quit[/]")

    # Simple REPL for demonstration
    while True:
        command = Prompt.ask("[bold cyan]fluttercraft>[/]")

        if command.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Thank you for using FlutterCraft! Goodbye![/]")
            break
        elif command.lower() in ["help", "h"]:
            # Capture output from help command
            with OutputCapture() as output:
                console.print("[green]Available commands:[/]")
                console.print("[bold cyan]Implemented commands:[/]")
                console.print(
                    "  [bold]fvm install[/] - Install Flutter Version Manager"
                )
                console.print(
                    "  [bold]fvm uninstall[/] - Uninstall Flutter Version Manager"
                )
                console.print(
                    "  [bold]fvm releases[/] - Show available Flutter versions"
                )
                console.print("    [dim]Usage: fvm releases [channel][/]")
                console.print(
                    "    [dim]Options: --channel/-c [stable|beta|dev|all] - Filter versions by channel[/]"
                )
                console.print(
                    "    [dim]Example: fvm releases beta  or  fvm releases --channel=beta[/]"
                )
                console.print(
                    "  [bold]clear[/] - Clear the terminal screen but preserve header and info"
                )
                console.print("  [bold]help, h[/] - Show this help message")
                console.print("  [bold]exit, quit, q[/] - Exit the CLI")

                console.print("\n[bold yellow]Coming in future updates:[/]")
                console.print("  [bold]create[/] - Create a new Flutter project")
                console.print("  [bold]flutter install[/] - Install Flutter")
                console.print("  [bold]fvm setup[/] - Setup Flutter Version Manager")
                console.print(
                    "  [bold]flutter version[/] - Check and switch Flutter versions"
                )

            # Add to history
            add_to_history(command, output.get_output())
        elif command.lower() == "create":
            # Capture output from create command
            with OutputCapture() as output:
                console.print(
                    "[yellow]In a future update, this would start the Flutter app "
                    "creation wizard![/]"
                )

            # Add to history
            add_to_history(command, output.get_output())
        elif command.lower() == "clear":
            # Clear the screen and display refreshed view
            clear_command(platform_info, flutter_info, fvm_info)
            # Don't add clear command to history
        elif command.lower() == "fvm install":
            # Install FVM and capture the output
            updated_fvm_info, cmd_output = fvm_install_command(
                platform_info, flutter_info, fvm_info
            )

            # Update info and history
            add_to_history(command, cmd_output)

            # If FVM version changed, refresh the display
            if updated_fvm_info != fvm_info:
                fvm_info = updated_fvm_info
                refresh_display(platform_info, flutter_info, fvm_info)
        elif command.lower() == "fvm uninstall":
            # Uninstall FVM and capture the output
            updated_fvm_info, cmd_output = fvm_uninstall_command(
                platform_info, flutter_info, fvm_info
            )

            # Update info and history
            add_to_history(command, cmd_output)

            # If FVM version changed, refresh the display
            if updated_fvm_info != fvm_info:
                fvm_info = updated_fvm_info
                refresh_display(platform_info, flutter_info, fvm_info)
        elif command.lower().startswith("fvm releases"):
            # Parse the command to check for channel parameter
            cmd_parts = command.lower().split()
            channel = None

            # Check if --channel or -c is provided
            if len(cmd_parts) >= 3:
                # Handle --channel=value format
                if any(part.startswith("--channel=") for part in cmd_parts):
                    for part in cmd_parts:
                        if part.startswith("--channel="):
                            channel = part.split("=")[1]
                            break
                # Handle -c value or --channel value format
                elif cmd_parts[2] in ["-c", "--channel"] and len(cmd_parts) >= 4:
                    channel = cmd_parts[3]
                # If just a single parameter is provided without flags (e.g. "fvm releases beta")
                elif len(cmd_parts) == 3 and cmd_parts[2] in [
                    "stable",
                    "beta",
                    "dev",
                    "all",
                ]:
                    channel = cmd_parts[2]

            # Show Flutter releases available through FVM with optional channel filter
            try:
                cmd_output = fvm_releases_command(channel)
            except Exception as e:
                with OutputCapture() as output:
                    console.print(
                        f"[bold red]Error fetching Flutter releases: {str(e)}[/]"
                    )
                    console.print(
                        "[yellow]Try using: fvm releases --channel [stable|beta|dev|all][/]"
                    )
                cmd_output = output.get_output()

            # Add to history
            add_to_history(command, cmd_output)
        elif command.lower().startswith("flutter"):
            # Capture output from flutter command
            with OutputCapture() as output:
                console.print(
                    "[yellow]In a future update, this would handle Flutter commands![/]"
                )

            # Add to history
            add_to_history(command, output.get_output())
        elif command.lower().startswith("fvm"):
            if command.lower() in ["fvm install", "fvm uninstall", "fvm releases"]:
                # Already handled above
                pass
            else:
                # Capture output from other fvm commands
                with OutputCapture() as output:
                    console.print(
                        "[yellow]In a future update, this would handle additional FVM commands![/]"
                    )

                # Add to history
                add_to_history(command, output.get_output())
        else:
            # Capture output from unknown command
            with OutputCapture() as output:
                console.print(f"[red]Unknown command: {command}[/]")
                console.print("Type 'help' to see available commands")

            # Add to history
            add_to_history(command, output.get_output())
