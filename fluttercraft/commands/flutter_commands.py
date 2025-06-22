"""Flutter commands for FlutterCraft CLI."""

import re
from fluttercraft.utils.terminal_utils import run_with_loading


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
            clear_on_success=True,
            show_output_on_failure=False,
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
                clear_on_success=True,
                show_output_on_failure=False,
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
