"""FVM version checking functionality."""

import subprocess
from rich.console import Console
from fluttercraft.utils.terminal_utils import run_with_loading

console = Console()


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
            clear_on_success=True,
            show_output_on_failure=False,
        )

        if fvm_version_process.returncode == 0:
            fvm_installed = True
            # Clean up version string (remove whitespace)
            fvm_version = fvm_version_process.stdout.strip()
    except FileNotFoundError:
        fvm_installed = False

    return {"installed": fvm_installed, "version": fvm_version} 