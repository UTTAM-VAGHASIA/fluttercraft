"""Core theme classes and types for FlutterCraft CLI."""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class ThemeType(str, Enum):
    """Theme type enumeration."""

    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


@dataclass
class SemanticColors:
    """Semantic color definitions for UI elements."""

    # Text colors
    text_primary: str
    text_secondary: str
    text_link: str
    text_accent: str

    # Background colors
    background_primary: str
    background_diff_added: str
    background_diff_removed: str

    # Border colors
    border_default: str
    border_focused: str

    # UI element colors
    ui_comment: str
    ui_symbol: str

    # Status colors
    status_error: str
    status_success: str
    status_warning: str
    status_info: str


@dataclass
class Theme:
    """Theme configuration for FlutterCraft CLI.

    Inspired by Gemini CLI's theming system with support for
    gradient colors, semantic tokens, and rich formatting.
    """

    name: str
    type: ThemeType
    description: str

    # Core colors
    background: str
    foreground: str

    # Accent colors
    accent_blue: str
    accent_purple: str
    accent_cyan: str
    accent_green: str
    accent_yellow: str
    accent_red: str

    # Utility colors
    gray: str
    comment: str

    # Diff colors
    diff_added: str
    diff_removed: str

    # Optional accent colors
    accent_pink: Optional[str] = None
    accent_orange: Optional[str] = None

    # Gradient colors for special effects
    gradient_colors: Optional[List[str]] = None

    # Semantic colors
    semantic: Optional[SemanticColors] = None

    def __post_init__(self):
        """Initialize semantic colors if not provided."""
        if self.semantic is None:
            self.semantic = SemanticColors(
                text_primary=self.foreground,
                text_secondary=self.gray,
                text_link=self.accent_blue,
                text_accent=self.accent_purple,
                background_primary=self.background,
                background_diff_added=self.diff_added,
                background_diff_removed=self.diff_removed,
                border_default=self.gray,
                border_focused=self.accent_blue,
                ui_comment=self.comment,
                ui_symbol=self.accent_cyan,
                status_error=self.accent_red,
                status_success=self.accent_green,
                status_warning=self.accent_yellow,
                status_info=self.accent_blue,
            )

    def get_rich_style(self, element: str) -> str:
        """Get Rich library style string for a given element.

        Args:
            element: Element type (e.g., 'error', 'success', 'info', 'warning',
                    'primary', 'secondary', 'accent', 'link', 'comment')

        Returns:
            Rich-compatible color string
        """
        mapping = {
            "error": self.semantic.status_error,
            "success": self.semantic.status_success,
            "warning": self.semantic.status_warning,
            "info": self.semantic.status_info,
            "primary": self.semantic.text_primary,
            "secondary": self.semantic.text_secondary,
            "accent": self.semantic.text_accent,
            "link": self.semantic.text_link,
            "comment": self.semantic.ui_comment,
            "symbol": self.semantic.ui_symbol,
            "border": self.semantic.border_default,
            "border_focused": self.semantic.border_focused,
        }
        return mapping.get(element, self.foreground)

    def to_dict(self) -> dict:
        """Convert theme to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "background": self.background,
            "foreground": self.foreground,
            "accent_blue": self.accent_blue,
            "accent_purple": self.accent_purple,
            "accent_cyan": self.accent_cyan,
            "accent_green": self.accent_green,
            "accent_yellow": self.accent_yellow,
            "accent_red": self.accent_red,
            "accent_pink": self.accent_pink,
            "accent_orange": self.accent_orange,
            "gray": self.gray,
            "comment": self.comment,
            "diff_added": self.diff_added,
            "diff_removed": self.diff_removed,
            "gradient_colors": self.gradient_colors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create theme from dictionary."""
        return cls(
            name=data["name"],
            type=ThemeType(data["type"]),
            description=data.get("description", ""),
            background=data["background"],
            foreground=data["foreground"],
            accent_blue=data["accent_blue"],
            accent_purple=data["accent_purple"],
            accent_cyan=data["accent_cyan"],
            accent_green=data["accent_green"],
            accent_yellow=data["accent_yellow"],
            accent_red=data["accent_red"],
            accent_pink=data.get("accent_pink"),
            accent_orange=data.get("accent_orange"),
            gray=data["gray"],
            comment=data["comment"],
            diff_added=data["diff_added"],
            diff_removed=data["diff_removed"],
            gradient_colors=data.get("gradient_colors"),
        )
