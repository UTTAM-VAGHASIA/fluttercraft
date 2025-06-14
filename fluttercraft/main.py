import typer
from rich.console import Console
from rich.panel import Panel
import pyfiglet
from typing import Optional

from fluttercraft.commands.start import start_command

app = typer.Typer(help="FlutterCraft: Automate your Flutter app setup like a pro.")
console = Console()

def display_welcome_art():
    """Display the FlutterCraft ASCII art and welcome message."""
    art = pyfiglet.figlet_format("FlutterCraft", font="slant")
    console.print(Panel.fit(
        f"[bold cyan]{art}[/]\n"
        "[bold green]Automate your Flutter app setup like a pro.[/]\n"
        "[yellow]From folder structure to backend integration, from icons to GitHub repo setup — FlutterCraft does it all.[/]",
        border_style="blue",
        title="Welcome to FlutterCraft 🛠️🚀",
        subtitle="v0.1.0"
    ))

@app.command()
def start():
    """Start the FlutterCraft interactive CLI."""
    display_welcome_art()
    start_command()
    
@app.callback()
def main():
    """FlutterCraft CLI - Flutter app automation tool."""
    pass

if __name__ == "__main__":
    app() 