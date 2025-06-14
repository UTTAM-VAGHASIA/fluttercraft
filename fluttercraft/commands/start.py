"""Start command for FlutterCraft CLI."""
from rich.console import Console
from rich.prompt import Prompt

console = Console()


def start_command():
    """
    Start the interactive CLI session.
    This is the main command that users will use to start creating Flutter apps.
    """
    console.print("[bold green]FlutterCraft CLI started![/]")
    console.print(
        "[bold]Enter commands or type 'exit' or 'quit' or 'q' to quit[/]"
    )

    # Simple REPL for demonstration
    while True:
        command = Prompt.ask("[bold cyan]fluttercraft>[/]")

        if command.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Thank you for using FlutterCraft! Goodbye![/]")
            break
        elif command.lower() in ["help", "h"]:
            console.print("[green]Available commands:[/]")
            console.print("  [bold]create[/] - Create a new Flutter project")
            console.print("  [bold]flutter install[/] - Install Flutter")
            console.print("  [bold]fvm setup[/] - Setup Flutter Version Manager")
            console.print("  [bold]help[/] - Show this help message")
            console.print("  [bold]exit or quit or q[/] - Exit the CLI")
        elif command.lower() == "create":
            console.print(
                "[yellow]In a future update, this would start the Flutter app "
                "creation wizard![/]"
            )
        elif command.lower().startswith("flutter"):
            console.print(
                "[yellow]In a future update, this would handle Flutter commands![/]"
            )
        elif command.lower().startswith("fvm"):
            console.print(
                "[yellow]In a future update, this would handle FVM commands![/]"
            )
        else:
            console.print(f"[red]Unknown command: {command}[/]")
            console.print("Type 'help' to see available commands") 
            