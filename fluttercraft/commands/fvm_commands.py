"""FVM commands for FlutterCraft CLI."""

import os
from rich.console import Console
from rich.prompt import Prompt
from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture
from fluttercraft.utils.system_utils import check_chocolatey_installed

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
            console.print(
                f"[bold green]FVM is already installed (version: {fvm_info['version']})[/]"
            )
            return fvm_info, output.get_output()

        console.print("[bold blue]Installing Flutter Version Manager (FVM)...[/]")

        # Windows installation (using Chocolatey)
        if platform_info["system"].lower().startswith("windows"):
            # Check if Chocolatey is installed
            choco_info = check_chocolatey_installed()

            if not choco_info["installed"]:
                console.print(
                    "[bold yellow]Chocolatey package manager is required but not installed.[/]"
                )
                install_choco = Prompt.ask(
                    "[bold yellow]Would you like to install Chocolatey? (requires admin privileges)[/]",
                    choices=["y", "n"],
                    default="y",
                )

                if install_choco.lower() != "y":
                    console.print(
                        "[red]FVM installation aborted. Chocolatey is required to install FVM on Windows.[/]"
                    )
                    return fvm_info, output.get_output()

                console.print(
                    "[bold yellow]Installing Chocolatey. This requires administrative privileges...[/]"
                )
                console.print(
                    "[bold yellow]Please allow the UAC prompt if it appears...[/]"
                )

                # Command to install Chocolatey
                choco_install_cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex"

                # Need to run as admin
                # Use PowerShell's Start-Process with -Verb RunAs to request elevation
                admin_cmd = f"powershell -Command \"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command {choco_install_cmd}' -Verb RunAs -Wait\""

                result = run_with_loading(
                    admin_cmd,
                    status_message="[bold yellow]Installing Chocolatey package manager...[/]",
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                # Check if installation was successful
                choco_info = check_chocolatey_installed()
                if not choco_info["installed"]:
                    console.print(
                        "[bold red]Failed to install Chocolatey. Please install it manually.[/]"
                    )
                    return fvm_info, output.get_output()
                else:
                    console.print(
                        f"[bold green]Chocolatey installed successfully (version: {choco_info['version']})![/]"
                    )

            # Install FVM using Chocolatey
            console.print("[bold yellow]Installing FVM using Chocolatey...[/]")
            console.print(
                "[bold yellow]This requires administrative privileges. Please allow the UAC prompt if it appears...[/]"
            )

            # Use PowerShell's Start-Process with -Verb RunAs to request elevation
            admin_cmd = "powershell -Command \"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command choco install fvm -y' -Verb RunAs -Wait\""

            result = run_with_loading(
                admin_cmd,
                status_message="[bold yellow]Installing FVM via Chocolatey...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify installation
            updated_fvm_info = check_fvm_version()
            if updated_fvm_info["installed"]:
                console.print(
                    f"[bold green]FVM installed successfully (version: {updated_fvm_info['version']})![/]"
                )
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    "[bold red]Failed to install FVM. Please try installing it manually.[/]"
                )
                console.print("[yellow]You can try: choco install fvm -y[/]")
                return fvm_info, output.get_output()

        # macOS and Linux installation (using curl)
        else:
            console.print("[bold yellow]Installing FVM using curl...[/]")

            curl_cmd = "curl -fsSL https://fvm.app/install.sh | bash"

            result = run_with_loading(
                curl_cmd,
                status_message="[bold yellow]Installing FVM via curl...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )

            if result.returncode != 0:
                console.print("[bold red]Failed to install FVM. Error:[/]")
                console.print(result.stderr)
                console.print(
                    "[yellow]You can try installing manually: curl -fsSL https://fvm.app/install.sh | bash[/]"
                )
                return fvm_info, output.get_output()

            # Verify installation
            updated_fvm_info = check_fvm_version()
            if updated_fvm_info["installed"]:
                console.print(
                    f"[bold green]FVM installed successfully (version: {updated_fvm_info['version']})![/]"
                )
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    "[bold yellow]FVM may have been installed but needs a terminal restart to be detected.[/]"
                )
                console.print(
                    "[yellow]Please restart your terminal and run 'fvm --version' to verify installation.[/]"
                )
                return fvm_info, output.get_output()


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
            console.print("[bold yellow]FVM is not installed. Nothing to uninstall.[/]")
            return fvm_info, output.get_output()

        console.print(
            f"[bold blue]Flutter Version Manager (FVM) version {fvm_info['version']} is installed.[/]"
        )

        # Ask if user wants to remove cached Flutter versions
        remove_cache = Prompt.ask(
            "[bold yellow]Do you want to remove all cached Flutter versions before uninstalling? (recommended)[/]",
            choices=["y", "n"],
            default="y",
        )

        if remove_cache.lower() == "y":
            console.print("[bold yellow]Removing cached Flutter versions...[/]")

            # For 'fvm destroy', we can't use run_with_loading directly because it requires interactive input
            # Instead we'll handle the process differently to automatically provide "y" to the prompt
            try:
                # Use subprocess directly to handle interactive input
                console.print(
                    "[bold yellow]Running 'fvm destroy' and automatically confirming...[/]"
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
                    status_message="[bold yellow]Running 'fvm destroy'...[/]",
                    shell=shell,
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                if destroy_result.returncode == 0:
                    console.print(
                        "[bold green]Successfully removed all cached Flutter versions.[/]"
                    )
                else:
                    console.print(
                        "[bold red]Failed to remove cached Flutter versions.[/]"
                    )
                    console.print(destroy_result.stderr)

                    # Ask if the user wants to continue with uninstallation
                    continue_uninstall = Prompt.ask(
                        "[bold yellow]Do you want to continue with FVM uninstallation?[/]",
                        choices=["y", "n"],
                        default="y",
                    )

                    if continue_uninstall.lower() != "y":
                        console.print("[yellow]FVM uninstallation aborted.[/]")
                        return fvm_info, output.get_output()
            except Exception as e:
                console.print(
                    f"[bold red]Error when removing cached Flutter versions: {str(e)}[/]"
                )

                # Ask if the user wants to continue with uninstallation despite the error
                continue_uninstall = Prompt.ask(
                    "[bold yellow]Do you want to continue with FVM uninstallation?[/]",
                    choices=["y", "n"],
                    default="y",
                )

                if continue_uninstall.lower() != "y":
                    console.print("[yellow]FVM uninstallation aborted.[/]")
                    return fvm_info, output.get_output()

        # Windows uninstallation (using Chocolatey)
        if platform_info["system"].lower().startswith("windows"):
            # Check if Chocolatey is installed
            choco_info = check_chocolatey_installed()

            if not choco_info["installed"]:
                console.print(
                    "[bold yellow]Chocolatey is not installed. Cannot use choco to uninstall FVM.[/]"
                )
                console.print("[yellow]Please uninstall FVM manually.[/]")
                return fvm_info, output.get_output()

            console.print("[bold yellow]Uninstalling FVM using Chocolatey...[/]")
            console.print(
                "[bold yellow]This requires administrative privileges. Please allow the UAC prompt if it appears...[/]"
            )

            # Use PowerShell's Start-Process with -Verb RunAs to request elevation
            admin_cmd = "powershell -Command \"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command choco uninstall fvm -y' -Verb RunAs -Wait\""

            result = run_with_loading(
                admin_cmd,
                status_message="[bold yellow]Uninstalling FVM via Chocolatey...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify uninstallation
            updated_fvm_info = check_fvm_version()
            if not updated_fvm_info["installed"]:
                console.print("[bold green]FVM uninstalled successfully![/]")
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    "[bold red]Failed to uninstall FVM. Please try uninstalling it manually.[/]"
                )
                console.print("[yellow]You can try: choco uninstall fvm -y[/]")
                return fvm_info, output.get_output()

        # macOS and Linux uninstallation
        else:
            console.print("[bold yellow]Uninstalling FVM...[/]")

            # Try to locate the install.sh script (usually in ~/.fvm/bin)
            install_script_path = os.path.expanduser("~/.fvm/bin/install.sh")

            if not os.path.exists(install_script_path):
                console.print("[bold yellow]Cannot find the FVM install script.[/]")
                console.print("[yellow]Attempting to download the uninstaller...[/]")

                download_cmd = "curl -fsSL https://fvm.app/install.sh -o /tmp/fvm_uninstall.sh && chmod +x /tmp/fvm_uninstall.sh"
                download_result = run_with_loading(
                    download_cmd,
                    status_message="[bold yellow]Downloading FVM installer/uninstaller...[/]",
                    clear_on_success=True,
                    show_output_on_failure=True,
                )

                if download_result.returncode == 0:
                    install_script_path = "/tmp/fvm_uninstall.sh"
                else:
                    console.print("[bold red]Failed to download FVM uninstaller.[/]")
                    console.print(
                        "[yellow]Please try uninstalling manually with: curl -fsSL https://fvm.app/install.sh | bash -- --uninstall[/]"
                    )
                    return fvm_info, output.get_output()

            # Run the uninstall command
            uninstall_cmd = f"{install_script_path} --uninstall"

            result = run_with_loading(
                uninstall_cmd,
                status_message="[bold yellow]Uninstalling FVM...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )

            # Verify uninstallation
            updated_fvm_info = check_fvm_version()
            if not updated_fvm_info["installed"]:
                console.print("[bold green]FVM uninstalled successfully![/]")
                return updated_fvm_info, output.get_output()
            else:
                console.print(
                    "[bold yellow]FVM may still be installed or needs a terminal restart to reflect changes.[/]"
                )
                console.print(
                    "[yellow]Please restart your terminal and check with 'fvm --version'.[/]"
                )
                return fvm_info, output.get_output()
