"""Global help functionality."""

from rich.console import Console
from rich.table import Table

console = Console()


def show_global_help():
    """Display global help information."""
    console.print("[bold cyan]FlutterCraft CLI Help[/]", justify="center")

    console.print("\n[bold green]Available Commands:[/]")

    # Current commands table
    current_table = Table(show_header=True, box=None)
    current_table.add_column("Command", style="cyan")
    current_table.add_column("Description", style="green")

    current_table.add_row("help", "Display this help information")
    current_table.add_row("exit, quit, q", "Exit the FlutterCraft CLI")
    current_table.add_row("clear", "Clear the terminal screen")
    current_table.add_row("fvm install", "Install Flutter Version Manager")
    current_table.add_row("fvm uninstall", "Uninstall Flutter Version Manager")
    current_table.add_row("fvm releases", "List all available Flutter versions")
    current_table.add_row("fvm list", "List all installed Flutter versions")

    console.print(current_table)

    # Coming Soon table
    future_table = Table(
        title="\n[bold yellow]Coming Soon[/]", show_header=True, box=None
    )
    future_table.add_column("Command", style="cyan")
    future_table.add_column("Description", style="green")

    future_table.add_row(
        "create", "Create a new Flutter project with configuration wizard"
    )
    future_table.add_row("flutter", "Run Flutter commands with extra features")
    future_table.add_row(
        "fvm setup", "Install and configure a specific Flutter version"
    )
    future_table.add_row("fvm remove", "Remove a specific Flutter version")
    future_table.add_row("firebase", "Firebase integration commands")
    future_table.add_row("supabase", "Supabase integration commands")
    future_table.add_row("icon", "Generate app icons for all platforms")
    future_table.add_row("github", "Create and manage GitHub repositories")

    console.print(future_table)

    # Getting help
    console.print("\n[bold green]Getting Help:[/]")
    console.print(
        "  To get help on a specific command, type: [cyan]<command> help[/] or [cyan]<command> --help[/]"
    )
    console.print("  Examples:")
    console.print("    [cyan]fvm help[/] - Show help for FVM commands")
    console.print(
        "    [cyan]fvm install help[/] - Show help for the fvm install command"
    )

    return "Displayed global help"
