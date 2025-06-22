import typer
from rich.console import Console

from fluttercraft.commands.start import start_command
from fluttercraft.utils.display_utils import display_welcome_art

app = typer.Typer(help="FlutterCraft: Automate your Flutter app setup like a pro.")
console = Console()


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
