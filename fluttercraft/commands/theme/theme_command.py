"""Theme command implementation for FlutterCraft CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from fluttercraft.utils.themes import get_theme_manager
from fluttercraft.utils.themes.gradient import create_gradient_text
from fluttercraft.utils.themed_display import (
    print_success,
    print_error,
    print_info,
)
from .interactive_selector import run_interactive_theme_selector

theme_app = typer.Typer(help="Manage FlutterCraft themes")
console = Console()


@theme_app.command("set")
def set_theme(
    theme_name: str = typer.Argument(
        ..., help="Theme name (gemini, dark, light, minimal)"
    )
):
    """Set the active theme for FlutterCraft CLI.

    Examples:
        fluttercraft theme set gemini
        fluttercraft theme set dark
    """
    theme_manager = get_theme_manager()

    # Normalize theme name
    theme_name = theme_name.lower()

    if theme_manager.set_theme(theme_name):
        theme = theme_manager.get_current_theme()
        print_success(f"Theme changed to '{theme.name}'")

        # Show a preview of the new theme
        if theme.gradient_colors:
            preview = create_gradient_text(
                "FlutterCraft", theme.gradient_colors, bold=True
            )
            console.print("\nPreview: ", end="")
            console.print(preview)
        else:
            console.print(f"\nPreview: [bold {theme.accent_cyan}]FlutterCraft[/]")

        console.print(
            f"\n[dim]Restart FlutterCraft to see the full theme changes.[/]\n"
        )
    else:
        print_error(f"Theme '{theme_name}' not found")
        print_info("Use 'fluttercraft theme list' to see available themes")


@theme_app.command("list")
def list_themes():
    """List all available themes."""
    theme_manager = get_theme_manager()
    current_theme = theme_manager.get_current_theme()
    themes = theme_manager.list_themes()

    console.print(
        f"\n[bold {current_theme.semantic.text_accent}]Available Themes:[/]\n"
    )

    # Create a table for themes
    table = Table(
        show_header=True,
        header_style=f"bold {current_theme.semantic.text_accent}",
        border_style=current_theme.semantic.border_default,
    )
    table.add_column("Theme", style=current_theme.semantic.text_link, width=15)
    table.add_column("Description", style=current_theme.semantic.text_secondary)
    table.add_column("Status", justify="center", width=10)

    for name, description in themes.items():
        status = (
            f"[{current_theme.semantic.status_success}]✓ Active[/]"
            if name == current_theme.name
            else ""
        )
        table.add_row(name.title(), description, status)

    console.print(table)

    console.print(
        f"\n[{current_theme.semantic.text_secondary}]Use 'fluttercraft theme set <name>' to change theme[/]\n"
    )


@theme_app.command("current")
def show_current_theme():
    """Show the currently active theme."""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()

    console.print(f"\n[bold {theme.semantic.text_accent}]Current Theme:[/]\n")

    # Create info panel
    info_text = Text()
    info_text.append(f"Name: ", style=f"bold {theme.semantic.text_secondary}")
    info_text.append(f"{theme.name.title()}\n", style=f"bold {theme.accent_cyan}")
    info_text.append(f"Type: ", style=f"bold {theme.semantic.text_secondary}")
    info_text.append(f"{theme.type.value.title()}\n", style=theme.semantic.text_primary)
    info_text.append(f"Description: ", style=f"bold {theme.semantic.text_secondary}")
    info_text.append(f"{theme.description}\n\n", style=theme.semantic.text_primary)

    # Show color palette
    info_text.append("Color Palette:\n", style=f"bold {theme.semantic.text_secondary}")
    colors = [
        ("Blue", theme.accent_blue),
        ("Purple", theme.accent_purple),
        ("Cyan", theme.accent_cyan),
        ("Green", theme.accent_green),
        ("Yellow", theme.accent_yellow),
        ("Red", theme.accent_red),
    ]

    for color_name, color_value in colors:
        info_text.append(f"  {color_name}: ", style=theme.semantic.text_secondary)
        info_text.append("████", style=f"bold {color_value}")
        info_text.append(f" {color_value}\n", style="dim")

    panel = Panel(
        info_text,
        border_style=theme.semantic.border_focused,
        title=f"[bold {theme.accent_purple}]Theme Information[/]",
        title_align="left",
    )

    console.print(panel)
    console.print()


@theme_app.command("preview")
def preview_theme(
    theme_name: str = typer.Argument(
        ..., help="Theme name to preview (gemini, dark, light, minimal)"
    )
):
    """Preview a theme without applying it.

    Examples:
        fluttercraft theme preview gemini
        fluttercraft theme preview dark
    """
    theme_manager = get_theme_manager()
    theme_name = theme_name.lower()

    theme = theme_manager.get_theme_by_name(theme_name)
    if not theme:
        print_error(f"Theme '{theme_name}' not found")
        print_info("Use 'fluttercraft theme list' to see available themes")
        return

    console.print(
        f"\n[bold {theme.semantic.text_accent}]Theme Preview: {theme.name.title()}[/]\n"
    )

    # Show ASCII art preview with gradient
    if theme.gradient_colors:
        preview_text = create_gradient_text(
            "FlutterCraft", theme.gradient_colors, bold=True
        )
        console.print(preview_text)
    else:
        console.print(f"[bold {theme.accent_cyan}]FlutterCraft[/]")

    console.print()

    # Show sample output
    console.print(f"[{theme.semantic.status_success}]✓ Success message[/]")
    console.print(f"[{theme.semantic.status_error}]✗ Error message[/]")
    console.print(f"[{theme.semantic.status_warning}]⚠ Warning message[/]")
    console.print(f"[{theme.semantic.status_info}]ℹ Info message[/]")
    console.print(f"[{theme.semantic.text_link}]Link or command[/]")
    console.print(f"[{theme.semantic.text_secondary}]Secondary text[/]")

    console.print(
        f"\n[{theme.semantic.text_secondary}]Use 'fluttercraft theme set {theme_name}' to apply this theme[/]\n"
    )


@theme_app.command("select")
def select_theme_interactive():
    """Launch interactive theme selector with live preview.

    This opens a beautiful interactive interface where you can:
    - Browse all available themes with arrow keys
    - See live preview of each theme
    - Select and apply a theme with Enter
    - Cancel with 'q' or Escape

    Example:
        fluttercraft theme select
    """
    run_interactive_theme_selector()


@theme_app.callback(invoke_without_command=True)
def theme_callback(ctx: typer.Context):
    """Manage FlutterCraft themes.

    Use subcommands to list, set, or preview themes.
    Run without arguments to launch interactive selector.
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand, launch interactive selector
        run_interactive_theme_selector()
