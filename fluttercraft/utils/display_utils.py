from rich.console import Console
from rich.panel import Panel
import pyfiglet
from fluttercraft import __version__

console = Console()


def display_welcome_art():
    """Display the FlutterCraft ASCII art and welcome message."""
    art = pyfiglet.figlet_format("Flutter Craft", font="banner3-D")
    console.print(
        Panel.fit(
            f"[bold cyan]{art}[/]\n"
            "[bold green]Automate your Flutter app setup like a pro.[/]\n"
            "[yellow]From folder structure to backend integration, from icons to "
            "GitHub repo setup — FlutterCraft does it all.[/]",
            border_style="blue",
            title="Welcome to FlutterCraft 🛠️🚀",
            subtitle=f"v{__version__}"
        )
    ) 