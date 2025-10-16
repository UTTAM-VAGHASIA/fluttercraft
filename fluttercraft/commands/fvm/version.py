"""FVM version checking functionality."""

import subprocess
from rich.console import Console
from fluttercraft.utils.terminal_utils import run_with_loading

console = Console()


def check_fvm_version(silent=False):
    """Check if FVM is installed and get version information.

    Args:
        silent: If True, suppress all loading indicators and output
    """
    fvm_installed = False
    fvm_version = None

    try:
        # Check if FVM is installed and get version
        if silent:
            # Silent mode - no loading indicators
            fvm_result = subprocess.run(
                ["fvm", "--version"], capture_output=True, text=True, timeout=5
            )

            # Create a simple object to match run_with_loading return
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            fvm_version_process = Result(
                fvm_result.returncode, fvm_result.stdout, fvm_result.stderr
            )
        else:
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
