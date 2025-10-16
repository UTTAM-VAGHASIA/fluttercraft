"""Theme manager for FlutterCraft CLI.

Handles theme selection, persistence, and application.
"""

import json
from pathlib import Path
from typing import Optional
from .theme import Theme
from .professional_themes import PROFESSIONAL_THEMES, DEFAULT_THEME

# Use professional themes
AVAILABLE_THEMES = PROFESSIONAL_THEMES


class ThemeManager:
    """Manages theme configuration and persistence."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize theme manager.

        Args:
            config_dir: Directory to store theme configuration.
                       Defaults to ~/.fluttercraft/
        """
        if config_dir is None:
            config_dir = Path.home() / ".fluttercraft"

        self.config_dir = config_dir
        self.config_file = self.config_dir / "theme.json"
        self._current_theme: Optional[Theme] = None

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_current_theme(self) -> Theme:
        """Get the currently active theme.

        Returns:
            Current theme, defaults to Gemini theme if not set
        """
        if self._current_theme is None:
            self._current_theme = self._load_theme()
        return self._current_theme

    def set_theme(self, theme_name: str) -> bool:
        """Set the active theme.

        Args:
            theme_name: Name of the theme to activate

        Returns:
            True if theme was set successfully, False otherwise
        """
        if theme_name not in AVAILABLE_THEMES:
            return False

        self._current_theme = AVAILABLE_THEMES[theme_name]
        self._save_theme(theme_name)
        return True

    def list_themes(self) -> dict[str, str]:
        """List all available themes.

        Returns:
            Dictionary mapping theme names to descriptions
        """
        return {name: theme.description for name, theme in AVAILABLE_THEMES.items()}

    def get_theme_by_name(self, name: str) -> Optional[Theme]:
        """Get a theme by name.

        Args:
            name: Theme name

        Returns:
            Theme object or None if not found
        """
        return AVAILABLE_THEMES.get(name)

    def _load_theme(self) -> Theme:
        """Load theme from configuration file.

        Returns:
            Loaded theme or default theme
        """
        if not self.config_file.exists():
            return DEFAULT_THEME

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                theme_name = config.get("theme", "default_dark")
                return AVAILABLE_THEMES.get(theme_name, DEFAULT_THEME)
        except (json.JSONDecodeError, OSError):
            return DEFAULT_THEME

    def _save_theme(self, theme_name: str) -> None:
        """Save theme preference to configuration file.

        Args:
            theme_name: Name of the theme to save
        """
        try:
            config = {"theme": theme_name}
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except OSError:
            # Silently fail if we can't save the theme
            pass


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance.

    Returns:
        Global ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
