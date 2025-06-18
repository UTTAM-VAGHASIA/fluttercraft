"""Start command for FlutterCraft CLI."""

from rich.console import Console
from rich.prompt import Prompt
import platform
import os
import sys
import subprocess
import re

from fluttercraft.utils.platform_utils import get_platform_info

console = Console()


def run_with_loading(cmd, status_message=None, shell=True, should_display_command=True):
    """Run a command with a loading indicator.

    Args:
        cmd: Command to run (list or string)
        status_message: Custom status message (defaults to "Running command...")
        shell: Whether to run command in shell

    Returns:
        CompletedProcess instance with stdout and stderr
    """
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd

    if should_display_command:
        console.print(f"[bold cyan]Running command:[/] {cmd_str}")

    if not status_message:
        status_message = f"[bold yellow]Running {cmd_str}, please wait...[/]"

    with console.status(status_message):
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell,)

    return result


def check_flutter_version():
    """Check if Flutter is installed and get version information."""
    flutter_installed = False
    current_version = None
    latest_version = None

    try:
        # Check if Flutter is installed and get version
        flutter_version_process = run_with_loading(
            ["flutter", "--version"],
            status_message="[bold yellow]Checking Flutter installation...[/]",
            should_display_command=False,
        )

        if flutter_version_process.returncode == 0:
            flutter_installed = True
            # Parse version from output (e.g., "Flutter 3.32.0 • channel stable")
            version_match = re.search(
                r"Flutter (\d+\.\d+\.\d+)", flutter_version_process.stdout
            )
            if version_match:
                current_version = version_match.group(1)

            # Check for the latest version
            upgrade_process = run_with_loading(
                ["flutter", "upgrade", "--verify-only"],
                status_message="[bold yellow]Checking for Flutter updates...[/]",
                should_display_command=False,
            )

            if upgrade_process.returncode == 0:
                output = upgrade_process.stdout

                # Case 1: When there's an update available
                if "A new version of Flutter is available" in output:
                    # Latest version check
                    latest_match = re.search(
                        r"The latest version: (\d+\.\d+\.\d+)", output
                    )
                    if latest_match:
                        latest_version = latest_match.group(1)

                    # Current version check (from the upgrade output)
                    # This is more accurate than the version from flutter --version
                    current_match = re.search(
                        r"Your current version: (\d+\.\d+\.\d+)", output
                    )
                    if current_match:
                        current_version = current_match.group(1)

                # Case 2: When Flutter is already up to date
                elif "Flutter is already up to date" in output:
                    # In this case, the current version is also the latest version
                    version_match = re.search(r"Flutter (\d+\.\d+\.\d+) •", output)
                    if version_match:
                        current_version = version_match.group(1)
                        latest_version = current_version  # Same version
    except FileNotFoundError:
        flutter_installed = False

    return {
        "installed": flutter_installed,
        "current_version": current_version,
        "latest_version": latest_version,
    }


def check_fvm_version():
    """Check if FVM is installed and get version information."""
    fvm_installed = False
    fvm_version = None

    try:
        # Check if FVM is installed and get version
        fvm_version_process = run_with_loading(
            ["fvm", "--version"],
            status_message="[bold yellow]Checking FVM installation...[/]",
            should_display_command=False,
        )

        if fvm_version_process.returncode == 0:
            fvm_installed = True
            # Clean up version string (remove whitespace)
            fvm_version = fvm_version_process.stdout.strip()
    except FileNotFoundError:
        fvm_installed = False

    return {"installed": fvm_installed, "version": fvm_version}


def start_command():
    """
    Start the interactive CLI session.
    This is the main command that users will use to start creating Flutter apps.
    """
    # Get platform information using the utility function
    platform_info = get_platform_info()

    console.print("[bold green]FlutterCraft CLI started![/]")
    console.print(f"[bold blue]Platform: {platform_info['system']}[/]")
    console.print(f"[bold blue]Shell: {platform_info['shell']}[/]")
    console.print(f"[bold blue]Python version: {platform_info['python_version']}[/]")

    # Check Flutter installation and version
    flutter_info = check_flutter_version()

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

    # Check FVM installation
    fvm_info = check_fvm_version()

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
            console.print("[green]Available commands:[/]")
            console.print("  [bold]create[/] - Create a new Flutter project")
            console.print("  [bold]flutter install[/] - Install Flutter")
            console.print("  [bold]fvm setup[/] - Setup Flutter Version Manager")
            console.print("  [bold]help[/] - Show this help message")
            console.print("  [bold]exit or quit or q[/] - Exit the CLI")
        elif command.lower() == "create":
            # For future implementation of actual command execution
            # run_with_loading(command, "[bold yellow]Creating Flutter project, please wait...[/]")
            console.print(
                "[yellow]In a future update, this would start the Flutter app "
                "creation wizard![/]"
            )
        elif command.lower().startswith("flutter"):
            # For future implementation of actual command execution
            # run_with_loading(command, f"[bold yellow]Running {command}, please wait...[/]")
            console.print(
                "[yellow]In a future update, this would handle Flutter commands![/]"
            )
        elif command.lower().startswith("fvm"):
            # For future implementation of actual command execution
            # run_with_loading(command, f"[bold yellow]Running {command}, please wait...[/]")
            console.print(
                "[yellow]In a future update, this would handle FVM commands![/]"
            )
        else:
            console.print(f"[red]Unknown command: {command}[/]")
            console.print("Type 'help' to see available commands")
