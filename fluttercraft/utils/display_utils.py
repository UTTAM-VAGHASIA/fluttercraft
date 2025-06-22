"""Display utilities for FlutterCraft CLI."""

from rich.console import Console
from rich.panel import Panel
import pyfiglet
from fluttercraft import __version__
import os
import platform

console = Console()

# Store command history for redisplay after refreshing header
command_history = []


def display_welcome_art():
    """Display the FlutterCraft ASCII art and welcome message."""
    art = pyfiglet.figlet_format("Flutter Craft", font="banner3-D")
    console.print(
        Panel.fit(
            f"[bold cyan]{art}[/]\n"
            "[bold green]Automate your Flutter app setup like a pro.[/]\n"
            "[yellow]From folder structure to backend integration, from icons to "
            "GitHub repo setup — FlutterCraft does it all.[/]",
            border_style="blue",
            title="Welcome to FlutterCraft 🛠️🚀",
            subtitle=f"v{__version__}",
        )
    )


def display_full_header(platform_info, flutter_info, fvm_info):
    """Display the complete header including ASCII art and version information.
    Clears the screen first.
    """
    # Clear the screen
    os.system("cls" if platform.system().lower() == "windows" else "clear")

    # Display the welcome art
    display_welcome_art()

    # Print platform information
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


def refresh_display(platform_info, flutter_info, fvm_info, should_clear=False):
    """Clear the screen, redisplay the header with updated version info,
    and restore command history.
    """
    # Redisplay full header with current version info
    display_full_header(platform_info, flutter_info, fvm_info)

    # Redisplay previous command outputs
    if should_clear:
        command_history.clear()
    else:
        for cmd, output in command_history:
            console.print(f"[bold cyan]fluttercraft>[/] {cmd}")
            console.print(output)


def add_to_history(command, output):
    """Add a command and its output to the history."""
    command_history.append((command, output))

    # Keep history to a reasonable size (last 20 commands)
    if len(command_history) > 20:
        command_history.pop(0)


def clear_command(platform_info, flutter_info, fvm_info):
    """Clear the screen and redisplay the header and history."""
    command_history.clear()
    refresh_display(platform_info, flutter_info, fvm_info, should_clear=True)
