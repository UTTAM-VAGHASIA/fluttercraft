"""FVM installation functionality."""

import os
from rich.console import Console
from rich.prompt import Prompt

from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture
from fluttercraft.utils.system_utils import check_chocolatey_installed
from fluttercraft.utils.themes.service import ThemeDisplayService
from fluttercraft.commands.fvm.version import check_fvm_version

console = Console()
display = ThemeDisplayService(console)


def fvm_install_command(platform_info, flutter_info, fvm_info):
    """
    Install Flutter Version Manager (FVM) based on the platform.
    For Windows: Uses Chocolatey
    For macOS/Linux: Uses curl installation script

    Returns:
        Updated FVM info, output captured during the command
    """
    # Capture all output during this command
    with OutputCapture() as output:
        # First check if FVM is already installed
        if fvm_info["installed"]:
            display.print_success(
                f"FVM is already installed (version: {fvm_info['version']})"
            )
            return fvm_info, output.get_output()

        console.print(
            display.format_text(
                "info", "Installing Flutter Version Manager (FVM)...", bold=True
            )
        )

        # Windows installation (using Chocolatey)
        if platform_info["system"].lower().startswith("windows"):
            # Check if Chocolatey is installed
            choco_info = check_chocolatey_installed()

            if not choco_info["installed"]:
                console.print(
                    display.format_text(
                        "warning",
                        "Chocolatey package manager is required but not installed.",
                        bold=True,
                    )
                )
                install_choco = Prompt.ask(
                    display.format_text(
                        "warning",
                        "Would you like to install Chocolatey? (requires admin privileges)",
                        bold=True,
                    ),
                    choices=["y", "n"],
                    default="y",
                )

                if install_choco.lower() != "y":
                    console.print(
                        display.format_text(
                            "error",
                            "FVM installation aborted. Chocolatey is required to install FVM on Windows.",
                        )
                    )
                    return fvm_info, output.get_output()

                console.print(
                    display.format_text(
                        "warning",
                        "Installing Chocolatey. This requires administrative privileges...",
                        bold=True,
                    )
                )
                console.print(
                    display.format_text(
                        "warning",
                        "Please allow the UAC prompt if it appears...",
                        bold=True,
                    )
                )

                # Command to install Chocolatey
                choco_install_cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex"

                # Need to run as admin
                # Use PowerShell's Start-Process with -Verb RunAs to request elevation
                admin_cmd = f"powershell -Command \"Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command {choco_install_cmd}' -Verb RunAs -Wait\""

                result = run_with_loading(
                    admin_cmd,
                    status_message=display.format_text(
                        "warning", "Installing Chocolatey package manager...", bold=True
                    ),
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                # Check if installation was successful
                choco_info = check_chocolatey_installed()
                if not choco_info["installed"]:
                    console.print(
                        display.format_text(
                            "error",
                            "Failed to install Chocolatey. Please install it manually.",
                            bold=True,
                        )
                    )
                    return fvm_info, output.get_output()
                else:
                    display.print_success(
                        f"Chocolatey installed successfully (version: {choco_info['version']})!"
                    )

            # Install FVM using Chocolatey
            console.print(
                display.format_text(
                    "warning", "Installing FVM using Chocolatey...", bold=True
                )
            )
            console.print(
                display.format_text(
                    "warning",
                    "This requires administrative privileges. Please allow the UAC prompt if it appears...",
                    bold=True,
                )
            )

            # Use PowerShell's Start-Process with -Verb RunAs to request elevation
            admin_cmd = "powershell -Command \"Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command choco install fvm -y' -Verb RunAs -Wait\""

            result = run_with_loading(
                admin_cmd,
                status_message=display.format_text(
                    "warning", "Installing FVM via Chocolatey...", bold=True
                ),
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify installation
            updated_fvm_info = check_fvm_version()
            if updated_fvm_info["installed"]:
                display.print_success(
                    f"FVM installed successfully (version: {updated_fvm_info['version']})!"
                )
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    display.format_text(
                        "error",
                        "Failed to install FVM. Please try installing it manually.",
                        bold=True,
                    )
                )
                console.print(
                    display.format_text("warning", "You can try: choco install fvm -y")
                )
                return fvm_info, output.get_output()

        # macOS and Linux installation (using curl)
        else:
            console.print(
                display.format_text(
                    "warning", "Installing FVM using curl...", bold=True
                )
            )

            curl_cmd = "curl -fsSL https://fvm.app/install.sh | bash"

            result = run_with_loading(
                curl_cmd,
                status_message=display.format_text(
                    "warning", "Installing FVM via curl...", bold=True
                ),
                clear_on_success=True,
                show_output_on_failure=True,
            )

            if result.returncode != 0:
                console.print(
                    display.format_text(
                        "error", "Failed to install FVM. Error:", bold=True
                    )
                )
                console.print(result.stderr)
                console.print(
                    display.format_text(
                        "warning",
                        "You can try installing manually: curl -fsSL https://fvm.app/install.sh | bash",
                    )
                )
                return fvm_info, output.get_output()

            # Verify installation
            updated_fvm_info = check_fvm_version()
            if updated_fvm_info["installed"]:
                display.print_success(
                    f"FVM installed successfully (version: {updated_fvm_info['version']})!"
                )
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    display.format_text(
                        "warning",
                        "FVM may have been installed but needs a terminal restart to be detected.",
                        bold=True,
                    )
                )
                console.print(
                    display.format_text(
                        "warning",
                        "Please restart your terminal and run 'fvm --version' to verify installation.",
                    )
                )
                return fvm_info, output.get_output()
