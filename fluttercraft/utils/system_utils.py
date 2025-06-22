"""System utilities for FlutterCraft CLI."""

from fluttercraft.utils.terminal_utils import run_with_loading


def check_chocolatey_installed():
    """Check if Chocolatey is installed on Windows."""
    choco_installed = False

    try:
        # Check if Chocolatey is installed by running choco --version
        choco_version_process = run_with_loading(
            ["choco", "--version"],
            status_message="[bold yellow]Checking Chocolatey installation...[/]",
            should_display_command=False,
            clear_on_success=True,
            show_output_on_failure=False,
        )

        if choco_version_process.returncode == 0:
            choco_installed = True
            version = choco_version_process.stdout.strip()
            return {"installed": True, "version": version}
    except FileNotFoundError:
        pass

    return {"installed": False, "version": None}
