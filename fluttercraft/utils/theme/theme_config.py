"""Theme configuration for FlutterCraft CLI."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Theme:
    name: str
    background: str
    foreground: str
    primary: str
    secondary: str
    accent: str
    success: str
    warning: str
    error: str
    border: str
    
    # Textual TUI specific colors
    surface: str = "#1e1e1e"
    panel_bg: str = "#252526"

# Default Dark Theme (Codex-inspired)
DEFAULT_THEME = Theme(
    name="default",
    background="#1e1e1e",
    foreground="#d4d4d4",
    primary="#569cd6",
    secondary="#9cdcfe",
    accent="#4ec9b0",
    success="#6a9955",
    warning="#dcdcaa",
    error="#f44747",
    border="#3c3c3c",
    surface="#252526",
    panel_bg="#1e1e1e"
)

def get_current_theme() -> Theme:
    """Get the current active theme."""
    # In a real app, this would load from config
    return DEFAULT_THEME
