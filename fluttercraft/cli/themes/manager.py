"""
Theme Manager

Advanced theme management system for FlutterCraft with Rich integration,
GEMINI-inspired themes, and dynamic theme switching capabilities.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.theme import Theme
from rich.style import Style

from fluttercraft.cli.themes.gemini import ALL_THEMES, get_theme_names, get_theme_info
from fluttercraft.config.settings import ConfigManager, ConfigurationError
from fluttercraft.utils.validators import ValidationError, validate_theme_name


class ThemeError(Exception):
    """Raised when theme operations fail."""
    
    def __init__(self, message: str, suggestions: List[str] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)


class FlutterCraftTheme:
    """
    FlutterCraft theme wrapper that extends Rich's Theme functionality.
    
    Provides enhanced theming capabilities including component styling,
    syntax highlighting, and interactive element customization.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize FlutterCraft theme.
        
        Args:
            name: Theme name
            config: Theme configuration dictionary
        """
        self.name = name
        self.config = config
        
        # Create Rich theme from config
        self.rich_theme = self._create_rich_theme(config)
        
        # Extract theme metadata
        self.display_name = config.get("name", name)
        self.description = config.get("description", "No description available")
        self.author = config.get("author", "Unknown")
        self.version = config.get("version", "1.0.0")
        
        # Extract component properties
        self.spinner = config.get("spinner", "dots")
        self.prompt_style = config.get("prompt", "bold blue")
        
    def _create_rich_theme(self, config: Dict[str, Any]) -> Theme:
        """
        Create Rich theme from configuration.
        
        Args:
            config: Theme configuration
            
        Returns:
            Rich Theme instance
        """
        # Map theme config to Rich theme styles
        theme_styles = {}
        
        # Basic color mappings
        basic_mappings = {
            "primary": "primary",
            "secondary": "secondary", 
            "accent": "accent",
            "success": "success",
            "warning": "warning",
            "error": "error",
            "info": "info",
            "muted": "muted",
        }
        
        for config_key, theme_key in basic_mappings.items():
            if config_key in config:
                theme_styles[theme_key] = config[config_key]
        
        # Component style mappings
        component_mappings = {
            "panel_border": "panel.border",
            "panel_title": "panel.title",
            "panel_content": "panel.content",
            "table_header": "table.header",
            "table_row": "table.row",
            "table_row_alt": "table.row_alt",
            "button": "button",
            "button_secondary": "button.secondary",
            "input": "input",
            "input_border": "input.border",
            "progress_bar": "progress.bar",
            "progress_background": "progress.background",
            "progress_percentage": "progress.percentage",
            "status_working": "status.working",
            "status_success": "status.success",
            "status_error": "status.error",
            "status_info": "status.info",
            "prompt": "prompt",
            "link": "link",
            "code": "code",
        }
        
        for config_key, theme_key in component_mappings.items():
            if config_key in config:
                theme_styles[theme_key] = config[config_key]
        
        # Syntax highlighting mappings
        syntax_mappings = {
            "syntax_keyword": "syntax.keyword",
            "syntax_string": "syntax.string",
            "syntax_number": "syntax.number",
            "syntax_comment": "syntax.comment",
            "syntax_function": "syntax.function",
            "syntax_variable": "syntax.variable",
        }
        
        for config_key, theme_key in syntax_mappings.items():
            if config_key in config:
                theme_styles[theme_key] = config[config_key]
        
        # Text color mappings
        text_mappings = {
            "text_primary": "text.primary",
            "text_secondary": "text.secondary",
            "text_disabled": "text.disabled",
            "text_on_primary": "text.on_primary",
        }
        
        for config_key, theme_key in text_mappings.items():
            if config_key in config:
                theme_styles[theme_key] = config[config_key]
        
        return Theme(theme_styles)
    
    def get_style(self, style_name: str) -> Optional[str]:
        """
        Get a style from the theme.
        
        Args:
            style_name: Name of the style to retrieve
            
        Returns:
            Style string or None if not found
        """
        return self.rich_theme.styles.get(style_name)
    
    def preview_colors(self) -> Dict[str, str]:
        """
        Get preview colors for the theme.
        
        Returns:
            Dictionary of preview colors
        """
        return {
            "primary": self.config.get("primary", "#000000"),
            "secondary": self.config.get("secondary", "#333333"),
            "accent": self.config.get("accent", "#666666"),
            "success": self.config.get("success", "#00ff00"),
            "warning": self.config.get("warning", "#ffff00"),
            "error": self.config.get("error", "#ff0000")
        }


class ThemeManager:
    """
    Advanced theme management system for FlutterCraft.
    
    Handles theme loading, switching, customization, and integration
    with Rich console instances.
    """
    
    def __init__(self, console: Console, config_manager: ConfigManager):
        """
        Initialize theme manager.
        
        Args:
            console: Rich console instance
            config_manager: Configuration manager
        """
        self.console = console
        self.config_manager = config_manager
        self.logger = logging.getLogger("fluttercraft.themes")
        
        # Internal state
        self._themes: Dict[str, FlutterCraftTheme] = {}
        self._current_theme: Optional[FlutterCraftTheme] = None
        
        # Load themes
        self._load_themes()
        
        # Set initial theme
        self._initialize_theme()
    
    def _load_themes(self) -> None:
        """Load all available themes."""
        try:
            for theme_name, theme_config in ALL_THEMES.items():
                theme = FlutterCraftTheme(theme_name, theme_config)
                self._themes[theme_name] = theme
                
            self.logger.debug(f"Loaded {len(self._themes)} themes")
            
        except Exception as e:
            raise ThemeError(
                f"Failed to load themes: {str(e)}",
                ["Check theme definitions for syntax errors"]
            )
    
    def _initialize_theme(self) -> None:
        """Initialize the current theme."""
        try:
            # Get current theme from config
            current_theme_name = self.config_manager.get_current_theme()
            
            # Validate theme exists
            if current_theme_name and current_theme_name in self._themes:
                self.set_theme(current_theme_name, save=False)
            else:
                # Fall back to default theme
                default_theme = self.config_manager.get("general.default_theme", "gemini-classic")
                if default_theme in self._themes:
                    self.set_theme(default_theme, save=True)
                else:
                    # Final fallback to first available theme
                    first_theme = next(iter(self._themes.keys()))
                    self.set_theme(first_theme, save=True)
                    
        except Exception as e:
            self.logger.warning(f"Error initializing theme: {e}")
            # Use first available theme as last resort
            if self._themes:
                first_theme = next(iter(self._themes.keys()))
                self._current_theme = self._themes[first_theme]
                self.console.theme = self._current_theme.rich_theme
    
    @property
    def current_theme(self) -> FlutterCraftTheme:
        """Get the current theme."""
        if not self._current_theme:
            raise ThemeError("No theme is currently active")
        return self._current_theme
    
    @property
    def available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self._themes.keys())
    
    def get_theme(self, name: str) -> FlutterCraftTheme:
        """
        Get theme by name.
        
        Args:
            name: Theme name
            
        Returns:
            FlutterCraftTheme instance
            
        Raises:
            ThemeError: If theme doesn't exist
        """
        if name not in self._themes:
            available = ", ".join(self.available_themes)
            raise ThemeError(
                f"Theme '{name}' not found",
                [f"Available themes: {available}"]
            )
        
        return self._themes[name]
    
    def set_theme(self, name: str, save: bool = True) -> None:
        """
        Set the current theme.
        
        Args:
            name: Theme name to set
            save: Whether to save theme to configuration
            
        Raises:
            ThemeError: If theme doesn't exist or setting fails
        """
        try:
            # Validate theme name
            validate_theme_name(name)
            
            # Get theme
            theme = self.get_theme(name)
            
            # Set as current theme
            self._current_theme = theme
            
            # Update console theme
            self.console.theme = theme.rich_theme
            
            # Save to configuration if requested
            if save:
                self.config_manager.set_current_theme(name)
            
            self.logger.debug(f"Set current theme to '{name}'")
            
        except (ValidationError, ThemeError) as e:
            raise ThemeError(
                f"Failed to set theme '{name}': {e.message if hasattr(e, 'message') else str(e)}",
                getattr(e, 'suggestions', [])
            )
        except Exception as e:
            raise ThemeError(
                f"Unexpected error setting theme '{name}': {str(e)}",
                ["Check theme configuration and try again"]
            )
    
    def preview_theme(self, name: str) -> Dict[str, Any]:
        """
        Preview a theme without applying it.
        
        Args:
            name: Theme name to preview
            
        Returns:
            Theme preview information
            
        Raises:
            ThemeError: If theme doesn't exist
        """
        theme = self.get_theme(name)
        
        return {
            "name": theme.display_name,
            "description": theme.description,
            "author": theme.author,
            "version": theme.version,
            "colors": theme.preview_colors(),
            "spinner": theme.spinner,
            "is_current": theme.name == self._current_theme.name if self._current_theme else False
        }
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """
        List all available themes with information.
        
        Returns:
            List of theme information dictionaries
        """
        themes_info = []
        
        for theme_name in sorted(self.available_themes):
            theme = self._themes[theme_name]
            themes_info.append({
                "id": theme_name,
                "name": theme.display_name,
                "description": theme.description,
                "author": theme.author,
                "version": theme.version,
                "colors": theme.preview_colors(),
                "is_current": theme_name == (self._current_theme.name if self._current_theme else None),
                "is_gemini": theme_name.startswith("gemini-")
            })
        
        return themes_info
    
    def get_gemini_themes(self) -> List[Dict[str, Any]]:
        """
        Get GEMINI-inspired themes only.
        
        Returns:
            List of GEMINI theme information
        """
        return [theme for theme in self.list_themes() if theme["is_gemini"]]
    
    def search_themes(self, query: str) -> List[Dict[str, Any]]:
        """
        Search themes by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching themes
        """
        query_lower = query.lower()
        matching_themes = []
        
        for theme_info in self.list_themes():
            if (query_lower in theme_info["name"].lower() or 
                query_lower in theme_info["description"].lower() or
                query_lower in theme_info["id"].lower()):
                matching_themes.append(theme_info)
        
        return matching_themes
    
    def reset_theme(self) -> None:
        """Reset to default theme."""
        default_theme = self.config_manager.get("general.default_theme", "gemini-classic")
        self.set_theme(default_theme, save=True)
    
    def get_theme_info(self) -> Dict[str, Any]:
        """
        Get information about the current theme system.
        
        Returns:
            Theme system information
        """
        return {
            "current_theme": self._current_theme.name if self._current_theme else None,
            "current_theme_display": self._current_theme.display_name if self._current_theme else None,
            "total_themes": len(self._themes),
            "gemini_themes": len([t for t in self.available_themes if t.startswith("gemini-")]),
            "available_themes": self.available_themes,
            "console_has_theme": hasattr(self.console, 'theme') and self.console.theme is not None
        }
    
    def export_theme(self, theme_name: str, export_path: Path) -> None:
        """
        Export a theme to a file.
        
        Args:
            theme_name: Name of theme to export
            export_path: Path to export file
            
        Raises:
            ThemeError: If export fails
        """
        try:
            theme = self.get_theme(theme_name)
            
            import json
            
            export_data = {
                "fluttercraft_theme_version": "1.0.0",
                "theme": {
                    "name": theme.name,
                    "config": theme.config
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported theme '{theme_name}' to {export_path}")
            
        except Exception as e:
            raise ThemeError(
                f"Failed to export theme '{theme_name}': {str(e)}",
                ["Check write permissions for export path"]
            )
    
    def validate_theme_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate theme configuration.
        
        Args:
            config: Theme configuration to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If configuration is invalid
        """
        required_fields = ["name", "description", "primary", "secondary", "accent"]
        
        for field in required_fields:
            if field not in config:
                raise ValidationError(
                    f"Missing required field: {field}",
                    [f"Theme configuration must include '{field}' field"]
                )
        
        # Validate color fields are strings
        color_fields = ["primary", "secondary", "accent", "success", "warning", "error"]
        for field in color_fields:
            if field in config and not isinstance(config[field], str):
                raise ValidationError(
                    f"Color field '{field}' must be a string",
                    ["Use hex colors (#000000) or color names (red, blue, etc.)"]
                )
        
        return True
    
    def reload_themes(self) -> None:
        """Reload all themes from definitions."""
        self._themes.clear()
        self._load_themes()
        
        # Restore current theme if it still exists
        if self._current_theme and self._current_theme.name in self._themes:
            self.set_theme(self._current_theme.name, save=False)
        else:
            self._initialize_theme()
        
        self.logger.info("Reloaded all themes")
    
    def cleanup(self) -> None:
        """Clean up theme manager resources."""
        try:
            # Save current theme if needed
            if self._current_theme:
                self.config_manager.set_current_theme(self._current_theme.name)
            
            self.logger.debug("Theme manager cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Error during theme manager cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors during destruction
