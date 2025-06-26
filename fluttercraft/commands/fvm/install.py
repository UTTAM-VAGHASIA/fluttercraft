"""FVM installation functionality."""

import os
from rich.console import Console
from rich.prompt import Prompt
from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture
from fluttercraft.utils.system_utils import check_chocolatey_installed
from fluttercraft.commands.fvm.version import check_fvm_version

console = Console()


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
                admin_cmd = f"powershell -Command \"Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command {choco_install_cmd}' -Verb RunAs -Wait\""

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
            admin_cmd = "powershell -Command \"Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command choco install fvm -y' -Verb RunAs -Wait\""

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