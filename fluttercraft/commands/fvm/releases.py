"""FVM releases command functionality."""

import re
import subprocess
from rich.console import Console
from rich.table import Table
from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture

console = Console()


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