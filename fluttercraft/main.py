"""
FlutterCraft Main Entry Point

This module provides the main entry point for the FlutterCraft CLI application.
It initializes the Typer app and handles global configuration.
"""

import asyncio
from pickle import NONE
import sys
from pathlib import Path
from typing import Optional

from click import Command, command
import typer
from rich.console import Console
from rich.traceback import install

from fluttercraft import __version__
from fluttercraft.cli.core import FlutterCraftApp
from fluttercraft.config.settings import ConfigManager
from fluttercraft.utils.console import setup_console
from fluttercraft.utils.platform import ensure_platform_compatibility

# Install rich traceback handler for better error display
install(show_locals=True)

# Global console instance
console = Console()

def version_callback(value: bool):
    """Display version information."""
    if value:
        console.print(f"[bold blue]FlutterCraft[/bold blue] version [green]{__version__}[/green]")
        console.print("[dim]Automate your Flutter app setup like a pro 🛠️🚀[/dim]")
        raise typer.Exit()


def start_interactive(
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        help="Custom configuration directory path"
    )
):
    """
    Start the interactive FlutterCraft CLI.
    
    This launches the main interactive shell with theming, onboarding,
    and chat-like command experience.
    """
    try:
        # Ensure platform compatibility
        ensure_platform_compatibility()
        
        # Setup console with appropriate settings
        global console
        console = setup_console(verbose=verbose)
        
        # Initialize configuration
        config_manager = ConfigManager(config_dir=config_dir)
        
        # Create and run the main application
        app = FlutterCraftApp(console=console, config_manager=config_manager)
        
        # Start interactive mode
        asyncio.run(app.start_interactive())
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


# Create the main Typer app
app = typer.Typer(
    name="fluttercraft",
    help="Automate your Flutter app setup like a pro 🛠️🚀",
    rich_markup_mode="rich",
    no_args_is_help=False,  # Don't show help by default - launch interactive instead
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True,
)

# Add commands to the app
app.command("start")(start_interactive)

# Main callback that launches interactive mode by default
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        callback=version_callback,
        is_eager=True,
        help="Show version information and exit"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        help="Custom configuration directory path"
    )
):
    """
    FlutterCraft - Automate your Flutter app setup like a pro 🛠️🚀
    
    An interactive CLI tool for Flutter development that provides:
    
    • Flutter SDK and FVM management
    • Beautiful theming and customization  
    • Interactive chat-like experience
    • Cross-platform support (Windows, Linux, macOS)
    
    By default, launches the interactive shell. Use 'fluttercraft start' for explicit launch.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand provided - launch interactive shell
        try:
            # Ensure platform compatibility
            ensure_platform_compatibility()
            
            # Setup console with appropriate settings
            global console
            console = setup_console(verbose=verbose)
            
            # Initialize configuration
            config_manager = ConfigManager(config_dir=config_dir)
            
            # Create and run the main application
            app_instance = FlutterCraftApp(console=console, config_manager=config_manager)
            
            # Start interactive mode
            asyncio.run(app_instance.start_interactive())
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise typer.Exit(1)
        except Exception as e:
            import traceback
            error_msg = f"[red]Unexpected error: {str(e)}[/red]"
            console.print(error_msg)
            console.print(f"[yellow]Error location: {traceback.format_exc().splitlines()[-3]}[/yellow]")
            if verbose:
                console.print_exception()
            raise typer.Exit(1)

if __name__ == "__main__":
    app()
