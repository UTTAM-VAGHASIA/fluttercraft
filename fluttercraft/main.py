import typer
from rich.console import Console

from fluttercraft.commands.start import start_command
from fluttercraft.commands.theme import theme_app

app = typer.Typer(help="FlutterCraft: Automate your Flutter app setup like a pro.")
console = Console()

# Add theme command
app.add_typer(theme_app, name="theme")


@app.command()
def start():
    """Start the FlutterCraft interactive CLI."""
    start_command()


@app.callback()
def main():
    """FlutterCraft CLI - Flutter app automation tool."""
    pass


if __name__ == "__main__":
    app()
