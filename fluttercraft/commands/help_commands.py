"""Help commands for FlutterCraft CLI.

This module provides help functions for all CLI commands, including:
- Global help (help, h)
- Command-specific help (command help, command --help)
- Group-specific help (fvm help)
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def show_global_help():
    """Display global help information."""
    console.print("[bold cyan]FlutterCraft CLI Help[/]", justify="center")

    console.print("\n[bold green]Available Commands:[/]")

    # Current commands table
    current_table = Table(show_header=True, box=None)
    current_table.add_column("Command", style="cyan")
    current_table.add_column("Description", style="green")

    current_table.add_row("help", "Display this help information")
    current_table.add_row("exit, quit, q", "Exit the FlutterCraft CLI")
    current_table.add_row("clear", "Clear the terminal screen")
    current_table.add_row("fvm install", "Install Flutter Version Manager")
    current_table.add_row("fvm uninstall", "Uninstall Flutter Version Manager")
    current_table.add_row("fvm releases", "List all available Flutter versions")
    current_table.add_row("fvm list", "List all installed Flutter versions")

    console.print(current_table)

    # Coming Soon table
    future_table = Table(
        title="\n[bold yellow]Coming Soon[/]", show_header=True, box=None
    )
    future_table.add_column("Command", style="cyan")
    future_table.add_column("Description", style="green")

    future_table.add_row(
        "create", "Create a new Flutter project with configuration wizard"
    )
    future_table.add_row("flutter", "Run Flutter commands with extra features")
    future_table.add_row(
        "fvm setup", "Install and configure a specific Flutter version"
    )
    future_table.add_row("fvm remove", "Remove a specific Flutter version")
    future_table.add_row("firebase", "Firebase integration commands")
    future_table.add_row("supabase", "Supabase integration commands")
    future_table.add_row("icon", "Generate app icons for all platforms")
    future_table.add_row("github", "Create and manage GitHub repositories")

    console.print(future_table)

    # Getting help
    console.print("\n[bold green]Getting Help:[/]")
    console.print(
        "  To get help on a specific command, type: [cyan]<command> help[/] or [cyan]<command> --help[/]"
    )
    console.print("  Examples:")
    console.print("    [cyan]fvm help[/] - Show help for FVM commands")
    console.print(
        "    [cyan]fvm install help[/] - Show help for the fvm install command"
    )

    return "Displayed global help"


def show_fvm_help():
    """Display help information for FVM commands."""
    console.print(
        "[bold cyan]Flutter Version Manager (FVM) Commands[/]", justify="center"
    )

    console.print("\n[bold green]About FVM:[/]")
    console.print(
        "Flutter Version Manager (FVM) helps you manage multiple Flutter SDK versions "
        "on a per-project basis. This allows different projects to use different Flutter "
        "versions without conflicts."
    )

    console.print("\n[bold green]Available Commands:[/]")

    # FVM commands table
    table = Table(show_header=True, box=None)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")

    table.add_row("fvm install", "Install Flutter Version Manager on your system")
    table.add_row("fvm uninstall", "Uninstall Flutter Version Manager from your system")
    table.add_row(
        "fvm releases", "List all available Flutter SDK versions for installation"
    )
    table.add_row(
        "fvm releases [channel]",
        "List Flutter versions filtered by channel (stable, beta, dev, all)",
    )
    table.add_row("fvm list", "List all installed Flutter SDK versions managed by FVM")

    console.print(table)

    console.print("\n[bold green]Getting Help:[/]")
    console.print(
        "  To get help on a specific FVM command, type: [cyan]fvm <command> help[/]"
    )
    console.print("  Examples:")
    console.print(
        "    [cyan]fvm install help[/] - Show help for the fvm install command"
    )
    console.print(
        "    [cyan]fvm releases help[/] - Show help for the fvm releases command"
    )

    return "Displayed FVM help"


def show_fvm_install_help():
    """Display help information for the 'fvm install' command."""
    console.print("[bold cyan]fvm install - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Installs Flutter Version Manager (FVM) on your system, which allows you to "
        "manage multiple Flutter SDK versions."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]fvm install[/]")

    console.print("\n[bold green]Details:[/]")
    console.print("  On Windows:")
    console.print("    - Uses Chocolatey package manager to install FVM")
    console.print("    - Requires administrative privileges")
    console.print("    - Will offer to install Chocolatey if not already installed")

    console.print("  On macOS/Linux:")
    console.print("    - Uses curl to download and run the FVM installation script")
    console.print("    - May require terminal restart after installation")

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]fvm install[/] - Install FVM on your system")

    return "Displayed fvm install help"


def show_fvm_uninstall_help():
    """Display help information for the 'fvm uninstall' command."""
    console.print("[bold cyan]fvm uninstall - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Uninstalls Flutter Version Manager (FVM) from your system, with an option "
        "to remove all cached Flutter SDK versions."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]fvm uninstall[/]")

    console.print("\n[bold green]Details:[/]")
    console.print("  On Windows:")
    console.print("    - Uses Chocolatey package manager to uninstall FVM")
    console.print("    - Requires administrative privileges")

    console.print("  On macOS/Linux:")
    console.print("    - Uses the FVM installer script with --uninstall flag")
    console.print("    - May require terminal restart after uninstallation")

    console.print("\n[bold green]Interactive Options:[/]")
    console.print(
        "  The command will ask if you want to remove all cached Flutter versions."
    )
    console.print("  Recommended: Yes, to perform a complete cleanup.")

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]fvm uninstall[/] - Uninstall FVM from your system")

    return "Displayed fvm uninstall help"


def show_fvm_releases_help():
    """Display help information for the 'fvm releases' command."""
    console.print("[bold cyan]fvm releases - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Lists all available Flutter SDK versions that can be installed through FVM. "
        "The versions can be filtered by channel (stable, beta, dev, or all)."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]fvm releases[/] - List all stable versions (default)")
    console.print(
        "  [cyan]fvm releases [channel][/] - List versions from a specific channel"
    )
    console.print(
        "  [cyan]fvm releases --channel [channel][/] - List versions with explicit channel flag"
    )
    console.print(
        "  [cyan]fvm releases -c [channel][/] - List versions with short channel flag"
    )

    console.print("\n[bold green]Parameters:[/]")
    param_table = Table(show_header=True, box=None)
    param_table.add_column("Parameter", style="cyan")
    param_table.add_column("Description", style="green")
    param_table.add_column("Values", style="yellow")

    param_table.add_row(
        "channel",
        "Filter versions by release channel",
        "stable (default), beta, dev, all",
    )

    console.print(param_table)

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]fvm releases[/] - List all stable channel versions")
    console.print("  [cyan]fvm releases beta[/] - List all beta channel versions")
    console.print(
        "  [cyan]fvm releases --channel=dev[/] - List all dev channel versions"
    )
    console.print(
        "  [cyan]fvm releases --channel beta[/] - List all beta channel versions"
    )
    console.print("  [cyan]fvm releases -c all[/] - List versions from all channels")

    return "Displayed fvm releases help"


def show_fvm_list_help():
    """Display help information for the 'fvm list' command."""
    console.print("[bold cyan]fvm list - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Lists all installed Flutter SDK versions managed by FVM on your system. "
        "This includes global and local (project-specific) versions."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]fvm list[/]")

    console.print("\n[bold green]Output Information:[/]")
    console.print("  The command displays:")
    console.print("    • Cache directory location")
    console.print("    • Total size of all installed Flutter versions")
    console.print("    • Version number and details for each installed SDK")
    console.print("    • Which version is set as global (if any)")
    console.print(
        "    • Which version is set as local for the current project (if any)"
    )

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]fvm list[/] - Show all installed Flutter versions")

    return "Displayed fvm list help"


def show_clear_help():
    """Display help information for the 'clear' command."""
    console.print("[bold cyan]clear - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Clears the terminal screen but preserves the FlutterCraft CLI header and "
        "system information. This helps keep your session clean without losing context."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]clear[/]")

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]clear[/] - Clear the terminal screen")

    return "Displayed clear help"


def handle_help_command(command_parts):
    """
    Handle help requests for various commands.

    Args:
        command_parts (list): The command split into parts

    Returns:
        str: Message indicating which help was displayed
    """
    # Handle empty command parts (just 'help')
    if not command_parts or len(command_parts) == 0:
        return show_global_help()

    # First part is always 'help' in this function
    if len(command_parts) == 1:
        return show_global_help()

    # Check for command-specific help
    if command_parts[0] == "fvm":
        if len(command_parts) == 1:
            # Just "fvm", show global help
            return show_global_help()
        elif len(command_parts) == 2 and command_parts[1] in ["help", "--help", "-h"]:
            # "fvm help"
            return show_fvm_help()
        elif len(command_parts) >= 3 and command_parts[2] in ["help", "--help", "-h"]:
            # "fvm <command> help"
            if command_parts[1] == "install":
                return show_fvm_install_help()
            elif command_parts[1] == "uninstall":
                return show_fvm_uninstall_help()
            elif command_parts[1] == "releases":
                return show_fvm_releases_help()
            elif command_parts[1] == "list":
                return show_fvm_list_help()
    elif (
        command_parts[0] == "clear"
        and len(command_parts) >= 2
        and command_parts[1] in ["help", "--help", "-h"]
    ):
        return show_clear_help()

    # If we reach here, it's not a recognized help command
    return show_global_help()
