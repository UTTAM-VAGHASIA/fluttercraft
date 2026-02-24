from __future__ import annotations

import typer

from fluttercraft.app import FlutterCraftApp

app = typer.Typer(help="FlutterCraft: Automate your Flutter app setup like a pro.")


@app.command()
def start():
    """Start the FlutterCraft interactive TUI."""
    FlutterCraftApp().run()


@app.callback()
def main():
    """FlutterCraft CLI - Flutter app automation tool."""
    pass


if __name__ == "__main__":
    app()
