"""Theme-based Rich Console factory."""

from rich.console import Console
from rich.theme import Theme as RichTheme
from fluttercraft.utils.themes.theme_manager import get_theme_manager

def create_themed_console() -> Console:
    """Create a Rich Console with full theme styling."""
    theme = get_theme_manager().get_current_theme()
    
    # Create Rich theme from our theme
    # Rich themes map style names (e.g. "primary") to Rich style definitions (e.g. "bold white")
    rich_theme = RichTheme({
        "primary": f"{theme.semantic.text_primary}",
        "secondary": f"{theme.semantic.text_secondary}",
        "accent": f"{theme.accent_cyan}",
        "success": f"{theme.semantic.status_success}",
        "error": f"{theme.semantic.status_error}",
        "warning": f"{theme.semantic.status_warning}",
        "border": f"{theme.accent_cyan}",
    })
    
    return Console(
        theme=rich_theme,
        style=f"on {theme.background}",  # KEY: Background color for everything
        force_terminal=True,
        color_system="truecolor",  # 24-bit color support
    )
