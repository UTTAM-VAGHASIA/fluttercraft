"""Flutter version checking functionality."""

import re
from fluttercraft.utils.terminal_utils import run_with_loading


def check_flutter_version(silent=False):
    """Check if Flutter is installed and get version information.
    
    Uses only 'flutter upgrade --verify-only' to check both installation and updates.
    
    Args:
        silent: If True, suppress all loading indicators and output
    
    Returns:
        dict: {
            "installed": bool,
            "current_version": str or None,
            "latest_version": str or None,
            "update_available": bool
        }
    """
    flutter_installed = False
    current_version = None
    latest_version = None
    update_available = False

    try:
        # Use only 'flutter upgrade --verify-only' to check everything at once
        if silent:
            # Silent mode - no loading indicators
            import subprocess
            import platform as plat
            upgrade_result = subprocess.run(
                ["flutter", "upgrade", "--verify-only"],
                capture_output=True,
                text=True,
                timeout=30,  # Increased timeout for slower systems
                shell=(plat.system() == "Windows")  # Use shell on Windows to find flutter in PATH
            )
            # Create a simple object to match run_with_loading return
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            upgrade_process = Result(
                upgrade_result.returncode,
                upgrade_result.stdout,
                upgrade_result.stderr
            )
        else:
            upgrade_process = run_with_loading(
                ["flutter", "upgrade", "--verify-only"],
                status_message="[bold yellow]Checking Flutter version and updates...[/]",
                should_display_command=False,
                clear_on_success=True,
                show_output_on_failure=False,
            )

        if upgrade_process.returncode == 0:
            flutter_installed = True
            output = upgrade_process.stdout

            # Case 1: When there's an update available
            if "A new version of Flutter is available" in output:
                update_available = True
                
                # Latest version check
                latest_match = re.search(
                    r"The latest version: (\d+\.\d+\.\d+)", output
                )
                if latest_match:
                    latest_version = latest_match.group(1)

                # Current version check
                current_match = re.search(
                    r"Your current version: (\d+\.\d+\.\d+)", output
                )
                if current_match:
                    current_version = current_match.group(1)

            # Case 2: When Flutter is already up to date
            elif "Flutter is already up to date" in output or "already on" in output:
                update_available = False
                
                # Try to extract version from output
                version_match = re.search(r"Flutter (\d+\.\d+\.\d+)", output)
                if version_match:
                    current_version = version_match.group(1)
                    latest_version = current_version  # Same version
                    
    except FileNotFoundError:
        # Flutter command not found
        flutter_installed = False
    except Exception as e:
        # Catch any other exceptions (timeout, etc.)
        if not silent:
            from rich.console import Console
            console = Console()
            console.print(f"[dim]Note: Could not check Flutter version: {str(e)}[/]")

    return {
        "installed": flutter_installed,
        "current_version": current_version,
        "latest_version": latest_version,
        "update_available": update_available,
    }