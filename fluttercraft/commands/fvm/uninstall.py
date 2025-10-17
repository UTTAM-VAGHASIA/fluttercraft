"""FVM uninstall functionality."""

import os
from rich.prompt import Prompt

from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture
from fluttercraft.utils.system_utils import check_chocolatey_installed
from fluttercraft.utils.themed_display import (
    get_console,
    format_text,
    print_success,
    print_error,
    print_warning,
)
from fluttercraft.commands.fvm.version import check_fvm_version

console = get_console()


def fvm_uninstall_command(platform_info, flutter_info, fvm_info):
    """
    Uninstall Flutter Version Manager (FVM) based on the platform.
    For Windows: Uses Chocolatey
    For macOS/Linux: Uses install.sh --uninstall

    Returns:
        Updated FVM info, output captured during the command
    """
    # Capture all output during this command
    with OutputCapture() as output:
        # First check if FVM is installed
        if not fvm_info["installed"]:
            print_warning("FVM is not installed. Nothing to uninstall.")
            return fvm_info, output.get_output()

        console.print(
            format_text(
                "info",
                f"Flutter Version Manager (FVM) version {fvm_info['version']} is installed.",
                bold=True,
            )
        )

        # Ask if user wants to remove cached Flutter versions
        remove_cache = Prompt.ask(
            format_text(
                "warning",
                "Do you want to remove all cached Flutter versions before uninstalling? (recommended)",
                bold=True,
            ),
            choices=["y", "n"],
            default="y",
        )

        if remove_cache.lower() == "y":
            print_warning("Removing cached Flutter versions...")

            # For 'fvm destroy', we can't use run_with_loading directly because it requires interactive input
            # Instead we'll handle the process differently to automatically provide "y" to the prompt
            try:
                # Use subprocess directly to handle interactive input
                console.print(
                    format_text(
                        "warning",
                        "Running 'fvm destroy' and automatically confirming...",
                        bold=True,
                    )
                )

                # Check platform for appropriate command
                if platform_info["system"].lower().startswith("windows"):
                    # On Windows, use echo y | fvm destroy
                    destroy_cmd = "echo y | fvm destroy"
                    shell = True
                else:
                    # On Unix-like systems, use echo y | fvm destroy or printf "y\n" | fvm destroy
                    destroy_cmd = "printf 'y\\n' | fvm destroy"
                    shell = True

                # Execute the command with output displayed
                destroy_result = run_with_loading(
                    destroy_cmd,
                    status_message=format_text(
                        "warning", "Running 'fvm destroy'...", bold=True
                    ),
                    shell=shell,
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                if destroy_result.returncode == 0:
                    print_success("Successfully removed all cached Flutter versions.")
                else:
                    print_error("Failed to remove cached Flutter versions.")
                    console.print(destroy_result.stderr)

                    # Ask if the user wants to continue with uninstallation
                    continue_uninstall = Prompt.ask(
                        format_text(
                            "warning",
                            "Do you want to continue with FVM uninstallation?",
                            bold=True,
                        ),
                        choices=["y", "n"],
                        default="y",
                    )

                    if continue_uninstall.lower() != "y":
                        print_warning("FVM uninstallation aborted.")
                        return fvm_info, output.get_output()
            except Exception as e:
                print_error(f"Error when removing cached Flutter versions: {str(e)}")

                # Ask if the user wants to continue with uninstallation despite the error
                continue_uninstall = Prompt.ask(
                    format_text(
                        "warning",
                        "Do you want to continue with FVM uninstallation?",
                        bold=True,
                    ),
                    choices=["y", "n"],
                    default="y",
                )

                if continue_uninstall.lower() != "y":
                    print_warning("FVM uninstallation aborted.")
                    return fvm_info, output.get_output()

        # Windows uninstallation (using Chocolatey)
        if platform_info["system"].lower().startswith("windows"):
            # Check if Chocolatey is installed
            choco_info = check_chocolatey_installed()

            if not choco_info["installed"]:
                print_warning(
                    "Chocolatey is not installed. Cannot use choco to uninstall FVM."
                )
                print_warning("Please uninstall FVM manually.")
                return fvm_info, output.get_output()

            console.print(
                format_text(
                    "warning", "Uninstalling FVM using Chocolatey...", bold=True
                )
            )
            console.print(
                format_text(
                    "warning",
                    "This requires administrative privileges. Please allow the UAC prompt if it appears...",
                    bold=True,
                )
            )

            # Use PowerShell's Start-Process with -Verb RunAs to request elevation
            admin_cmd = "powershell -Command \"Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command choco uninstall fvm -y' -Verb RunAs -Wait\""

            result = run_with_loading(
                admin_cmd,
                status_message=format_text(
                    "warning", "Uninstalling FVM via Chocolatey...", bold=True
                ),
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify uninstallation
            updated_fvm_info = check_fvm_version(silent=True)
            if not updated_fvm_info["installed"]:
                print_success("FVM uninstalled successfully!")
                return updated_fvm_info, output.get_output()
            else:
                print_error(
                    "Failed to uninstall FVM. Please try uninstalling it manually."
                )
                print_warning("You can try: choco uninstall fvm -y")
                return fvm_info, output.get_output()

        # macOS and Linux uninstallation
        else:
            console.print(format_text("warning", "Uninstalling FVM...", bold=True))

            # Try to locate the install.sh script (usually in ~/.fvm/bin)
            install_script_path = os.path.expanduser("~/.fvm/bin/install.sh")

            if not os.path.exists(install_script_path):
                print_warning("Cannot find the FVM install script.")
                print_warning("Attempting to download the uninstaller...")

                download_cmd = "curl -fsSL https://fvm.app/install.sh -o /tmp/fvm_uninstall.sh && chmod +x /tmp/fvm_uninstall.sh"
                download_result = run_with_loading(
                    download_cmd,
                    status_message=format_text(
                        "warning",
                        "Downloading FVM installer/uninstaller...",
                        bold=True,
                    ),
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                if download_result.returncode == 0:
                    install_script_path = "/tmp/fvm_uninstall.sh"
                else:
                    print_error("Failed to download FVM uninstaller.")
                    console.print(
                        format_text(
                            "warning",
                            "Please try uninstalling manually with: curl -fsSL https://fvm.app/install.sh | bash -- --uninstall",
                        )
                    )
                    return fvm_info, output.get_output()

            # Run the uninstall command
            uninstall_cmd = f"{install_script_path} --uninstall"

            result = run_with_loading(
                uninstall_cmd,
                status_message=format_text("warning", "Uninstalling FVM...", bold=True),
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify uninstallation
            updated_fvm_info = check_fvm_version(silent=True)
            if not updated_fvm_info["installed"]:
                print_success("FVM uninstalled successfully!")
                return updated_fvm_info, output.get_output()
            else:
                print_warning(
                    "FVM may still be installed or needs a terminal restart to reflect changes."
                )
                print_warning(
                    "Please restart your terminal and check with 'fvm --version'."
                )
                return fvm_info, output.get_output()
