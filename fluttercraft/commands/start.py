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
from fluttercraft.commands.help_commands import (
    show_global_help,
    show_fvm_help,
    show_fvm_install_help,
    show_fvm_uninstall_help,
    show_fvm_releases_help,
    show_clear_help,
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
        cmd_parts = command.lower().strip().split()

        # Handle empty command
        if not cmd_parts:
            continue

        # Exit commands
        if cmd_parts[0] in ["exit", "quit", "q"]:
            console.print("[yellow]Thank you for using FlutterCraft! Goodbye![/]")
            break

        # Help command handling
        elif cmd_parts[0] in ["help", "h"]:
            # Capture output from help command
            with OutputCapture() as output:
                show_global_help()
            # Add to history
            add_to_history(command, output.get_output())
        # Check for command-specific help using the "command help" format
        elif len(cmd_parts) > 1 and cmd_parts[-1] in ["help", "--help", "-h"]:
            # Handle command-specific help
            with OutputCapture() as output:
                if cmd_parts[0] == "clear":
                    show_clear_help()
                elif cmd_parts[0] == "fvm":
                    if len(cmd_parts) == 2:
                        # "fvm help"
                        show_fvm_help()
                    else:
                        # "fvm <command> help"
                        if cmd_parts[1] == "install":
                            show_fvm_install_help()
                        elif cmd_parts[1] == "uninstall":
                            show_fvm_uninstall_help()
                        elif cmd_parts[1] == "releases":
                            show_fvm_releases_help()
                        else:
                            # Unknown fvm command
                            show_fvm_help()
                else:
                    # Fallback to global help
                    show_global_help()
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
                    if cmd_parts[0] == "fvm" and len(cmd_parts) == 1:
                        # Just "fvm" without args, show fvm help
                        show_fvm_help()
                    else:
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
