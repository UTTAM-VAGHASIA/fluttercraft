"""FVM commands for FlutterCraft CLI."""

import os
import subprocess
import re
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
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


def fvm_releases_command(channel=None):
    """
    Run the 'fvm releases' command and display the output in a better format.

    Args:
        channel (str, optional): Filter releases by channel ('stable', 'beta', 'dev', 'all').
                                Defaults to None which will use FVM's default (stable).

    Returns:
        Captured output during the command
    """
    # Capture all output during this command
    with OutputCapture() as output:
        console.print("[bold blue]Fetching Flutter releases from FVM...[/]")

        # Prepare command with optional channel parameter
        command = "fvm releases"
        if channel and channel.lower() in ["stable", "beta", "dev", "all"]:
            command += f" --channel {channel.lower()}"

        # Try with our standard method first
        result = run_with_loading(
            command,
            status_message="[bold yellow]Fetching Flutter release versions...[/]",
            should_display_command=False,
            clear_on_success=True,
            show_output_on_failure=False,
            shell=True,
        )

        if result.returncode != 0:
            # Try with direct subprocess call as fallback
            try:
                # Use subprocess directly to get output
                process = subprocess.run(
                    command, shell=True, text=True, capture_output=True
                )

                if process.returncode == 0:
                    result = process
                else:
                    console.print("[bold red]Error fetching Flutter releases.[/]")
                    if process.stderr:
                        console.print(f"[red]{process.stderr}[/]")
                    else:
                        console.print("[red]Make sure FVM is installed correctly.[/]")
                    return output.get_output()
            except Exception as e:
                console.print(f"[bold red]Error: {str(e)}[/]")
                return output.get_output()

        # Process the output - parse the table data from the command output
        lines = result.stdout.strip().split("\n")

        # Create stable releases table
        stable_releases = []
        current_channel_info = {}

        # Track if we're in the main list or in the Channel section
        in_channel_section = False

        # Simpler parsing approach - look for lines with stable versions
        for line in lines:
            # Check if we've reached the Channel section
            if "Channel:" in line:
                in_channel_section = True
                continue

            if "│" in line:
                # Clean up the line by removing ANSI escape codes
                line = re.sub(r"\x1b\[[0-9;]*[mK]", "", line)

                # Split by the pipe character and clean up
                parts = [p.strip() for p in line.split("│") if p.strip()]

                # Make sure we have enough parts
                if len(parts) >= 3:
                    if in_channel_section:
                        # This is part of the Channel section
                        # Record the current channel version info
                        if parts[0].lower() == "channel":  # This is the header
                            continue
                        elif parts[0].lower() in ["stable", "beta", "dev"]:
                            current_channel_info[parts[0].lower()] = {
                                "channel": parts[0],
                                "version": parts[1],
                                "date": parts[2] if len(parts) > 2 else "",
                            }
                    else:
                        # This is a regular version
                        # Skip rows that contain 'Channel' as these are headers
                        if any("channel" == p.lower() for p in parts):
                            continue

                        # The first part should be the version
                        version = parts[0]
                        # The second part should be the release date
                        date = parts[1]
                        # The third part should be the channel
                        release_channel = parts[2].replace("✓", "").strip()

                        # Check if this is the current version (has checkmark)
                        is_current = "✓" in line

                        # Skip entries that look like they might be channel indicators
                        # or the Channel section
                        if version.lower() == "stable" or version.lower() == "channel":
                            continue

                        stable_releases.append(
                            {
                                "version": version,
                                "date": date,
                                "channel": release_channel,
                                "is_current": is_current,
                            }
                        )

        # Get the current channel name for display in title
        channel_name = channel.lower() if channel else "stable"
        if channel_name == "all":
            title = "[bold cyan]All Flutter Versions Available Through FVM[/]"
        else:
            title = f"[bold cyan]Flutter {channel_name.capitalize()} Versions Available Through FVM[/]"

        # Create a rich table for display
        table = Table(title=title, show_header=True, header_style="bold magenta")

        # Add columns with proper width settings
        table.add_column("Version", style="cyan bold", no_wrap=True)
        table.add_column("Release Date", style="green")
        table.add_column("Channel", style="yellow")

        # Function to extract version number components for proper sorting
        def version_key(release):
            version = release["version"]
            # Remove leading 'v' if present
            if version.startswith("v"):
                version = version[1:]

            # Split by dots and extract components
            components = []
            # First split by special characters
            parts = re.split(r"[\.\+\-]", version)
            for part in parts:
                # Try to convert to number if possible
                if not part:  # Skip empty parts
                    continue
                try:
                    components.append((0, int(part)))  # Numbers come first
                except ValueError:
                    # If not a number, keep as string but ensure consistent comparison types
                    components.append((1, part))  # Strings come after numbers

            return components  # Python can compare tuples element by element

        # Sort releases by version number (ascending order)
        sorted_releases = sorted(stable_releases, key=version_key)

        # Get the latest versions by channel from current_channel_info
        latest_versions = {}
        for ch, info in current_channel_info.items():
            latest_versions[ch] = info.get("version", "").strip()

        # Add rows
        for release in sorted_releases:
            version = release["version"].strip()
            release_channel = release["channel"].lower()

            # Highlight if this is the latest version in its channel
            if (
                release_channel in latest_versions
                and version == latest_versions[release_channel]
            ):
                table.add_row(
                    f"[bold green]{version} ← Latest {release_channel}[/]",
                    release["date"],
                    release["channel"],
                )
            # Or if it has the checkmark in the original output
            elif release.get("is_current", False):
                table.add_row(
                    f"[bold green]{version} ← Latest {release_channel}[/]",
                    release["date"],
                    release["channel"],
                )
            else:
                table.add_row(version, release["date"], release["channel"])

        # Display the table
        console.print(table)

        # Show a count of available versions and usage instructions
        console.print(
            f"\n[bold green]Found {len(sorted_releases)} Flutter versions available through FVM.[/]"
        )

        # Show current channel information
        if current_channel_info:
            console.print(f"\n[bold cyan]Current Channels:[/]")
            for ch, info in current_channel_info.items():
                console.print(
                    f"  [bold green]{info['channel']}:[/] {info['version']} ({info['date']})"
                )

        # Show helpful usage instructions
        console.print("\n[bold blue]To use these versions:[/]")
        console.print(
            "  [yellow]fvm install <version>[/] - Install a specific Flutter version"
        )
        console.print(
            "  [yellow]fvm use <version>[/] - Set a specific Flutter version as active"
        )

        return output.get_output()
