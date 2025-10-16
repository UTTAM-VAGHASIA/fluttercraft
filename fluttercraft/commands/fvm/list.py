"""FVM list command functionality."""

import re
import subprocess
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from fluttercraft.utils.terminal_utils import run_with_loading, OutputCapture

console = Console()


def fvm_list_command():
    """
    Run the 'fvm list' command and display the output in a better format.
    Shows all installed Flutter SDK versions on the system through FVM.

    Returns:
        Captured output during the command
    """
    # Capture all output during this command
    with OutputCapture() as output:
        console.print("[bold blue]Listing installed Flutter versions from FVM...[/]")

        # Prepare command to list installed versions
        command = "fvm list"

        # Try with our standard method first
        result = run_with_loading(
            command,
            status_message="[bold yellow]Fetching installed Flutter versions...[/]",
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
                    console.print(
                        "[bold red]Error fetching installed Flutter versions.[/]"
                    )
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

        # Extract cache directory and size information
        cache_dir = None
        cache_size = None

        for line in lines:
            if "Cache directory:" in line:
                cache_dir = line.replace("Cache directory:", "").strip()
            elif "Directory Size:" in line:
                cache_size = line.replace("Directory Size:", "").strip()

        # Display cache information in a better format
        console.print()
        if cache_dir:
            console.print(f"[bold cyan]Cache Directory:[/] [green]{cache_dir}[/]")
        if cache_size:
            console.print(f"[bold cyan]Cache Size:[/] [green]{cache_size}[/]")
        console.print()

        # Create a list to store the installed versions
        installed_versions = []

        # Track if we're in the table section
        in_table = False
        headers = []

        # Parse the installed versions from the table
        for line in lines:
            # Skip until we find the table header divider
            if "├─────────┼" in line or "┌─────────┬" in line:
                in_table = True
                continue

            # Skip divider lines
            if "┼─────────┼" in line:
                continue

            # End of table
            if "└─────────┴" in line:
                in_table = False
                continue

            # If we're in the table section, parse the row
            if in_table and "│" in line:
                # Clean up the line by removing ANSI escape codes
                line = re.sub(r"\x1b\[[0-9;]*[mK]", "", line)

                # Split by the pipe character and clean up
                parts = [p.strip() for p in line.split("│") if p.strip()]

                # Store headers if this is the first row
                if not headers and any("Version" in p for p in parts):
                    headers = parts
                    continue

                # Skip if we don't have enough parts or this is the header row
                if len(parts) < 4 or any("Version" in p for p in parts):
                    continue

                # Create a dictionary for this version
                version_info = {}
                for i, header in enumerate(headers):
                    if i < len(parts):
                        key = header.lower().strip()
                        value = parts[i].strip()
                        # Check for global/local indicators (● symbol)
                        if key == "global" or key == "local":
                            version_info[key] = "●" in value or "✓" in value
                        else:
                            version_info[key] = value

                # Add to our list if it's a valid entry
                if "version" in version_info:
                    installed_versions.append(version_info)

        # Sort installed versions by date (newest first)
        installed_versions.sort(key=lambda v: v.get("release date", ""), reverse=True)

        # Create a rich table for display with improved styling
        table = Table(
            title="[bold cyan]Installed Flutter Versions[/]",
            show_header=True,
            header_style="bold bright_magenta",
            box=ROUNDED,
            border_style="bright_blue",
            padding=(0, 1),
            collapse_padding=False,
            min_width=80,
        )

        # Add columns with improved styles
        table.add_column("Version", style="cyan bold", no_wrap=True)
        table.add_column("Channel", style="yellow")
        table.add_column("Flutter Ver", style="green")
        table.add_column("Dart Ver", style="blue")
        table.add_column("Release Date", style="magenta")
        table.add_column("Global", style="red", justify="center")
        table.add_column("Local", style="red", justify="center")

        # Check if we have any installed versions
        if not installed_versions:
            # Add a centered message if no versions are installed
            table.add_row(
                "[yellow]No Flutter versions installed yet[/]", "", "", "", "", "", ""
            )
        else:
            # Add rows with improved styling
            for version in installed_versions:
                # Highlight the global version
                if version.get("global", False):
                    name = f"[bold bright_green]{version.get('version')} ← Global[/]"
                    global_mark = "[bright_green]✓[/]"
                    local_mark = ""
                elif version.get("local", False):
                    name = f"[bold bright_yellow]{version.get('version')} ← Local[/]"
                    global_mark = ""
                    local_mark = "[bright_yellow]✓[/]"
                else:
                    name = f"[white]{version.get('version')}[/]"
                    global_mark = ""
                    local_mark = ""

                table.add_row(
                    name,
                    f"[yellow]{version.get('channel', '')}[/]",
                    f"[green]{version.get('flutter version', '')}[/]",
                    f"[blue]{version.get('dart version', '')}[/]",
                    f"[magenta]{version.get('release date', '')}[/]",
                    global_mark if version.get("global", False) else "",
                    local_mark if version.get("local", False) else "",
                )

        # Display the table
        console.print(table)

        # Show a count of installed versions and usage instructions with improved styling
        version_count = len(installed_versions)
        if version_count == 0:
            console.print(
                "\n[bold yellow]No Flutter versions are installed through FVM yet.[/]"
            )
            console.print("\n[bold bright_blue]To install Flutter versions:[/]")
            console.print(
                "  [bright_yellow]fvm install <version>[/] - Install a specific Flutter version"
            )
        else:
            console.print(
                f"\n[bold bright_green]Found {version_count} installed Flutter {'version' if version_count == 1 else 'versions'}.[/]"
            )

            # Show helpful usage instructions with improved formatting
            console.print("\n[bold bright_blue]Helpful commands:[/]")
            console.print(
                "  [bright_yellow]fvm use <version>[/] - Set a specific Flutter version as active"
            )
            console.print(
                "  [bright_yellow]fvm remove <version>[/] - Remove a specific Flutter version"
            )

            if version_count > 0:
                console.print(
                    "\n[dim italic]💡 To learn more about a command, type: [cyan]command --help[/][/]"
                )

        return output.get_output()
