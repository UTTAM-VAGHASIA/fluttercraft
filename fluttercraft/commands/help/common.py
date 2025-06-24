"""Common help command functionality."""

from rich.console import Console

console = Console()


def show_clear_help():
    """Display help information for the 'clear' command."""
    console.print("[bold cyan]clear - Command Help[/]", justify="center")

    console.print("\n[bold green]Description:[/]")
    console.print(
        "Clears the terminal screen but preserves the FlutterCraft CLI header and "
        "system information. This helps keep your session clean without losing context."
    )

    console.print("\n[bold green]Usage:[/]")
    console.print("  [cyan]clear[/]")

    console.print("\n[bold green]Examples:[/]")
    console.print("  [cyan]clear[/] - Clear the terminal screen")

    return "Displayed clear help" 