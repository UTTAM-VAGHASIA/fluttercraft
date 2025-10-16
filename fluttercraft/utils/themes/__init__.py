"""Theme system for FlutterCraft CLI."""

from .theme import Theme, ThemeType
from .professional_themes import PROFESSIONAL_THEMES, DEFAULT_THEME
from .theme_manager import ThemeManager, get_theme_manager

# Use professional themes
AVAILABLE_THEMES = PROFESSIONAL_THEMES

__all__ = [
    "Theme",
    "ThemeType",
    "AVAILABLE_THEMES",
    "PROFESSIONAL_THEMES",
    "DEFAULT_THEME",
    "ThemeManager",
    "get_theme_manager",
]
