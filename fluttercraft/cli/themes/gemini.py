"""
GEMINI-Inspired Themes

Theme definitions inspired by Google's GEMINI CLI, featuring professional
color schemes and modern design patterns.
"""

from typing import Dict, Any

# GEMINI-inspired theme collection based on Google's design language
GEMINI_THEMES: Dict[str, Dict[str, Any]] = {
    "gemini-classic": {
        "name": "Gemini Classic",
        "description": "Professional blue theme inspired by Google's design",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Core color palette (using Google Blue palette)
        "primary": "#1a73e8",
        "secondary": "#34a853", 
        "accent": "#fbbc04",
        "success": "#34a853",
        "warning": "#ff9800",
        "error": "#ea4335",
        "info": "#1a73e8",
        "muted": "dim #9aa0a6",
        
        # Background and surface colors
        "background": "#ffffff",
        "surface": "#f8f9fa",
        "surface_variant": "#e8eaed",
        
        # Text colors
        "text_primary": "#202124",
        "text_secondary": "#5f6368",
        "text_disabled": "#9aa0a6",
        "text_on_primary": "#ffffff",
        
        # Component styles
        "panel_border": "#1a73e8",
        "panel_title": "bold #1a73e8",
        "panel_content": "#202124",
        
        "table_header": "bold #1a73e8",
        "table_row": "#202124",
        "table_row_alt": "#f8f9fa",
        
        "button": "bold white on #1a73e8",
        "button_secondary": "bold #1a73e8 on #e8f0fe",
        "input": "#1a73e8",
        "input_border": "#dadce0",
        
        # Status and progress
        "progress_bar": "#1a73e8",
        "progress_background": "#e8f0fe",
        "progress_percentage": "#1a73e8",
        
        "status_working": "#ff9800",
        "status_success": "#34a853",
        "status_error": "#ea4335",
        "status_info": "#1a73e8",
        
        # Interactive elements
        "spinner": "dots",
        "prompt": "bold #1a73e8",
        "link": "#1a73e8 underline",
        "code": "#5f6368 on #f8f9fa",
        
        # Syntax highlighting
        "syntax_keyword": "bold #1565c0",
        "syntax_string": "#2e7d32",
        "syntax_number": "#ef6c00",
        "syntax_comment": "italic #9e9e9e",
        "syntax_function": "#6a1b9a",
        "syntax_variable": "#1976d2",
    },
    
    "gemini-dark": {
        "name": "Gemini Dark",
        "description": "Dark theme with bright accents",
        "author": "FlutterCraft Team", 
        "version": "1.0.0",
        
        # Core color palette (dark variant)
        "primary": "#4285f4",
        "secondary": "#0f9d58",
        "accent": "#f4b400",
        "success": "#0f9d58",
        "warning": "#ff6d01",
        "error": "#d93025",
        "info": "#4285f4",
        "muted": "dim #9aa0a6",
        
        # Background and surface colors
        "background": "#121212",
        "surface": "#1e1e1e",
        "surface_variant": "#2d2d2d",
        
        # Text colors
        "text_primary": "#e8eaed",
        "text_secondary": "#9aa0a6",
        "text_disabled": "#5f6368",
        "text_on_primary": "#ffffff",
        
        # Component styles
        "panel_border": "#4285f4",
        "panel_title": "bold #4285f4",
        "panel_content": "#e8eaed",
        
        "table_header": "bold #4285f4",
        "table_row": "#e8eaed",
        "table_row_alt": "#2d2d2d",
        
        "button": "bold white on #4285f4",
        "button_secondary": "bold #4285f4 on #1e3a8a",
        "input": "#4285f4",
        "input_border": "#5f6368",
        
        # Status and progress
        "progress_bar": "#4285f4",
        "progress_background": "#1e3a8a",
        "progress_percentage": "#4285f4",
        
        "status_working": "#ff6d01",
        "status_success": "#0f9d58",
        "status_error": "#d93025",
        "status_info": "#4285f4",
        
        # Interactive elements
        "spinner": "arc",
        "prompt": "bold #4285f4",
        "link": "#4285f4 underline",
        "code": "#9aa0a6 on #2d2d2d",
        
        # Syntax highlighting
        "syntax_keyword": "bold #5dade2",
        "syntax_string": "#52c41a",
        "syntax_number": "#fa8c16",
        "syntax_comment": "italic #8c8c8c",
        "syntax_function": "#b37feb",
        "syntax_variable": "#40a9ff",
    },
    
    "gemini-light": {
        "name": "Gemini Light",
        "description": "Clean light theme with subtle accents",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Core color palette (light variant)
        "primary": "#1976d2",
        "secondary": "#388e3c",
        "accent": "#f57c00",
        "success": "#388e3c",
        "warning": "#f9a825",
        "error": "#d32f2f",
        "info": "#1976d2",
        "muted": "dim #757575",
        
        # Background and surface colors
        "background": "#fafafa",
        "surface": "#ffffff",
        "surface_variant": "#f5f5f5",
        
        # Text colors
        "text_primary": "#212121",
        "text_secondary": "#757575",
        "text_disabled": "#bdbdbd",
        "text_on_primary": "#ffffff",
        
        # Component styles
        "panel_border": "#1976d2",
        "panel_title": "bold #1976d2",
        "panel_content": "#212121",
        
        "table_header": "bold #1976d2",
        "table_row": "#212121",
        "table_row_alt": "#f5f5f5",
        
        "button": "bold white on #1976d2",
        "button_secondary": "bold #1976d2 on #e3f2fd",
        "input": "#1976d2",
        "input_border": "#e0e0e0",
        
        # Status and progress
        "progress_bar": "#1976d2",
        "progress_background": "#e3f2fd",
        "progress_percentage": "#1976d2",
        
        "status_working": "#f9a825",
        "status_success": "#388e3c",
        "status_error": "#d32f2f",
        "status_info": "#1976d2",
        
        # Interactive elements
        "spinner": "dots",
        "prompt": "bold #1976d2",
        "link": "#1976d2 underline",
        "code": "#757575 on #f5f5f5",
        
        # Syntax highlighting
        "syntax_keyword": "bold #1565c0",
        "syntax_string": "#2e7d32",
        "syntax_number": "#ef6c00",
        "syntax_comment": "italic #9e9e9e",
        "syntax_function": "#7b1fa2",
        "syntax_variable": "#1976d2",
    },
    
    "gemini-neon": {
        "name": "Gemini Neon",
        "description": "Cyberpunk-inspired vibrant theme",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Core color palette (neon/cyberpunk)
        "primary": "#00ffff",
        "secondary": "#ff00ff",
        "accent": "#ffff00",
        "success": "#00ff00",
        "warning": "#ff8c00",
        "error": "#ff0040",
        "info": "#00bfff",
        "muted": "dim #808080",
        
        # Background and surface colors
        "background": "#0a0a0a",
        "surface": "#1a1a2e",
        "surface_variant": "#16213e",
        
        # Text colors
        "text_primary": "#ffffff",
        "text_secondary": "#cccccc",
        "text_disabled": "#808080",
        "text_on_primary": "#000000",
        
        # Component styles
        "panel_border": "#00ffff",
        "panel_title": "bold #00ffff",
        "panel_content": "#ffffff",
        
        "table_header": "bold #ff00ff",
        "table_row": "#ffffff",
        "table_row_alt": "#1a1a2e",
        
        "button": "bold black on #00ffff",
        "button_secondary": "bold #00ffff on #1a1a2e",
        "input": "#00ffff",
        "input_border": "#00ffff",
        
        # Status and progress
        "progress_bar": "#00ffff",
        "progress_background": "#1a1a2e",
        "progress_percentage": "#00ffff",
        
        "status_working": "#ff8c00",
        "status_success": "#00ff00",
        "status_error": "#ff0040",
        "status_info": "#00bfff",
        
        # Interactive elements
        "spinner": "aesthetic",
        "prompt": "bold #00ffff",
        "link": "#00ffff underline",
        "code": "#cccccc on #1a1a2e",
        
        # Syntax highlighting
        "syntax_keyword": "bold #ff00ff",
        "syntax_string": "#00ff00",
        "syntax_number": "#ffff00",
        "syntax_comment": "italic #808080",
        "syntax_function": "#ff8c00",
        "syntax_variable": "#00bfff",
    },
    
    "gemini-ocean": {
        "name": "Gemini Ocean",
        "description": "Blue-green gradient theme inspired by ocean depths",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Core color palette (ocean-inspired)
        "primary": "#006064",
        "secondary": "#00695c",
        "accent": "#00acc1",
        "success": "#00c853",
        "warning": "#ffc107",
        "error": "#d50000",
        "info": "#0277bd",
        "muted": "dim #607d8b",
        
        # Background and surface colors
        "background": "#e0f2f1",
        "surface": "#ffffff",
        "surface_variant": "#b2dfdb",
        
        # Text colors
        "text_primary": "#263238",
        "text_secondary": "#455a64",
        "text_disabled": "#90a4ae",
        "text_on_primary": "#ffffff",
        
        # Component styles
        "panel_border": "#006064",
        "panel_title": "bold #006064",
        "panel_content": "#263238",
        
        "table_header": "bold #00695c",
        "table_row": "#263238",
        "table_row_alt": "#b2dfdb",
        
        "button": "bold white on #006064",
        "button_secondary": "bold #006064 on #b2dfdb",
        "input": "#00695c",
        "input_border": "#4db6ac",
        
        # Status and progress
        "progress_bar": "#00acc1",
        "progress_background": "#b2dfdb",
        "progress_percentage": "#006064",
        
        "status_working": "#ffc107",
        "status_success": "#00c853",
        "status_error": "#d50000",
        "status_info": "#0277bd",
        
        # Interactive elements
        "spinner": "dots",
        "prompt": "bold #006064",
        "link": "#0277bd underline",
        "code": "#455a64 on #b2dfdb",
        
        # Syntax highlighting
        "syntax_keyword": "bold #00695c",
        "syntax_string": "#00c853",
        "syntax_number": "#ffc107",
        "syntax_comment": "italic #90a4ae",
        "syntax_function": "#7c4dff",
        "syntax_variable": "#0277bd",
    },
}

# Additional non-GEMINI themes for variety
ADDITIONAL_THEMES: Dict[str, Dict[str, Any]] = {
    "flutter-blue": {
        "name": "Flutter Blue",
        "description": "Official Flutter brand colors",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Flutter brand colors
        "primary": "#0175c2",
        "secondary": "#13b9fd",
        "accent": "#ffc108",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#0175c2",
        "muted": "dim #666666",
        
        "background": "#ffffff",
        "surface": "#f5f5f5",
        "surface_variant": "#eeeeee",
        
        "text_primary": "#212121",
        "text_secondary": "#666666",
        "text_disabled": "#bdbdbd",
        "text_on_primary": "#ffffff",
        
        "panel_border": "#0175c2",
        "panel_title": "bold #0175c2",
        "panel_content": "#212121",
        
        "table_header": "bold #0175c2",
        "table_row": "#212121",
        "table_row_alt": "#f5f5f5",
        
        "button": "bold white on #0175c2",
        "button_secondary": "bold #0175c2 on #e3f2fd",
        "input": "#0175c2",
        "input_border": "#cccccc",
        
        "progress_bar": "#13b9fd",
        "progress_background": "#e3f2fd",
        "progress_percentage": "#0175c2",
        
        "status_working": "#ff9800",
        "status_success": "#4caf50",
        "status_error": "#f44336",
        "status_info": "#0175c2",
        
        "spinner": "dots",
        "prompt": "bold #0175c2",
        "link": "#0175c2 underline",
        "code": "#666666 on #f5f5f5",
        
        "syntax_keyword": "bold #0175c2",
        "syntax_string": "#4caf50",
        "syntax_number": "#ff9800",
        "syntax_comment": "italic #bdbdbd",
        "syntax_function": "#9c27b0",
        "syntax_variable": "#13b9fd",
    },
    
    "terminal-green": {
        "name": "Terminal Green",
        "description": "Classic hacker green terminal theme",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Classic terminal colors
        "primary": "#00ff00",
        "secondary": "#00cc00",
        "accent": "#ffff00",
        "success": "#00ff00",
        "warning": "#ffff00",
        "error": "#ff0000",
        "info": "#00ffff",
        "muted": "dim #008000",
        
        "background": "#000000",
        "surface": "#001100",
        "surface_variant": "#002200",
        
        "text_primary": "#00ff00",
        "text_secondary": "#00cc00",
        "text_disabled": "#008000",
        "text_on_primary": "#000000",
        
        "panel_border": "#00ff00",
        "panel_title": "bold #00ff00",
        "panel_content": "#00ff00",
        
        "table_header": "bold #00ff00",
        "table_row": "#00ff00",
        "table_row_alt": "#001100",
        
        "button": "bold black on #00ff00",
        "button_secondary": "bold #00ff00 on #001100",
        "input": "#00ff00",
        "input_border": "#00ff00",
        
        "progress_bar": "#00ff00",
        "progress_background": "#001100",
        "progress_percentage": "#00ff00",
        
        "status_working": "#ffff00",
        "status_success": "#00ff00",
        "status_error": "#ff0000",
        "status_info": "#00ffff",
        
        "spinner": "dots",
        "prompt": "bold #00ff00",
        "link": "#00ffff underline",
        "code": "#00cc00 on #001100",
        
        "syntax_keyword": "bold #00ff00",
        "syntax_string": "#ffff00",
        "syntax_number": "#00ffff",
        "syntax_comment": "italic #008000",
        "syntax_function": "#ff00ff",
        "syntax_variable": "#00cc00",
    },
    
    "sunset-orange": {
        "name": "Sunset Orange",
        "description": "Warm orange gradient theme",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Sunset-inspired colors
        "primary": "#e65100",
        "secondary": "#ff9800",
        "accent": "#ffc107",
        "success": "#8bc34a",
        "warning": "#ff5722",
        "error": "#d32f2f",
        "info": "#2196f3",
        "muted": "dim #795548",
        
        "background": "#fff3e0",
        "surface": "#ffffff",
        "surface_variant": "#ffe0b2",
        
        "text_primary": "#3e2723",
        "text_secondary": "#5d4037",
        "text_disabled": "#8d6e63",
        "text_on_primary": "#ffffff",
        
        "panel_border": "#e65100",
        "panel_title": "bold #e65100",
        "panel_content": "#3e2723",
        
        "table_header": "bold #e65100",
        "table_row": "#3e2723",
        "table_row_alt": "#ffe0b2",
        
        "button": "bold white on #e65100",
        "button_secondary": "bold #e65100 on #ffe0b2",
        "input": "#e65100",
        "input_border": "#ffcc02",
        
        "progress_bar": "#ff9800",
        "progress_background": "#ffe0b2",
        "progress_percentage": "#e65100",
        
        "status_working": "#ff5722",
        "status_success": "#8bc34a",
        "status_error": "#d32f2f",
        "status_info": "#2196f3",
        
        "spinner": "dots",
        "prompt": "bold #e65100",
        "link": "#2196f3 underline",
        "code": "#5d4037 on #ffe0b2",
        
        "syntax_keyword": "bold #e65100",
        "syntax_string": "#8bc34a",
        "syntax_number": "#ffc107",
        "syntax_comment": "italic #8d6e63",
        "syntax_function": "#9c27b0",
        "syntax_variable": "#ff9800",
    },
    
    "purple-rain": {
        "name": "Purple Rain",
        "description": "Purple-based theme with elegant gradients",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Purple-based palette
        "primary": "#7b1fa2",
        "secondary": "#9c27b0",
        "accent": "#e91e63",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#2196f3",
        "muted": "dim #9e9e9e",
        
        "background": "#f3e5f5",
        "surface": "#ffffff",
        "surface_variant": "#e1bee7",
        
        "text_primary": "#4a148c",
        "text_secondary": "#6a1b9a",
        "text_disabled": "#9e9e9e",
        "text_on_primary": "#ffffff",
        
        "panel_border": "#7b1fa2",
        "panel_title": "bold #7b1fa2",
        "panel_content": "#4a148c",
        
        "table_header": "bold #7b1fa2",
        "table_row": "#4a148c",
        "table_row_alt": "#e1bee7",
        
        "button": "bold white on #7b1fa2",
        "button_secondary": "bold #7b1fa2 on #e1bee7",
        "input": "#7b1fa2",
        "input_border": "#ce93d8",
        
        "progress_bar": "#9c27b0",
        "progress_background": "#e1bee7",
        "progress_percentage": "#7b1fa2",
        
        "status_working": "#ff9800",
        "status_success": "#4caf50",
        "status_error": "#f44336",
        "status_info": "#2196f3",
        
        "spinner": "dots",
        "prompt": "bold #7b1fa2",
        "link": "#2196f3 underline",
        "code": "#6a1b9a on #e1bee7",
        
        "syntax_keyword": "bold #7b1fa2",
        "syntax_string": "#4caf50",
        "syntax_number": "#ff9800",
        "syntax_comment": "italic #9e9e9e",
        "syntax_function": "#e91e63",
        "syntax_variable": "#9c27b0",
    },
    
    "monochrome": {
        "name": "Monochrome",
        "description": "Black and white theme for accessibility",
        "author": "FlutterCraft Team",
        "version": "1.0.0",
        
        # Monochrome palette
        "primary": "#000000",
        "secondary": "#333333",
        "accent": "#666666",
        "success": "#000000",
        "warning": "#333333",
        "error": "#000000",
        "info": "#000000",
        "muted": "dim #999999",
        
        "background": "#ffffff",
        "surface": "#f5f5f5",
        "surface_variant": "#eeeeee",
        
        "text_primary": "#000000",
        "text_secondary": "#333333",
        "text_disabled": "#999999",
        "text_on_primary": "#ffffff",
        
        "panel_border": "#000000",
        "panel_title": "bold #000000",
        "panel_content": "#000000",
        
        "table_header": "bold #000000",
        "table_row": "#000000",
        "table_row_alt": "#f5f5f5",
        
        "button": "bold white on #000000",
        "button_secondary": "bold #000000 on #eeeeee",
        "input": "#000000",
        "input_border": "#cccccc",
        
        "progress_bar": "#000000",
        "progress_background": "#eeeeee",
        "progress_percentage": "#000000",
        
        "status_working": "#333333",
        "status_success": "#000000",
        "status_error": "#000000",
        "status_info": "#000000",
        
        "spinner": "dots",
        "prompt": "bold #000000",
        "link": "#000000 underline",
        "code": "#333333 on #f5f5f5",
        
        "syntax_keyword": "bold #000000",
        "syntax_string": "#333333",
        "syntax_number": "#666666",
        "syntax_comment": "italic #999999",
        "syntax_function": "#000000",
        "syntax_variable": "#333333",
    }
}

# Combine all themes
ALL_THEMES = {**GEMINI_THEMES, **ADDITIONAL_THEMES}

def get_theme_names() -> list[str]:
    """Get list of all available theme names."""
    return list(ALL_THEMES.keys())

def get_gemini_theme_names() -> list[str]:
    """Get list of GEMINI-inspired theme names."""
    return list(GEMINI_THEMES.keys())

def get_theme_info(theme_name: str) -> Dict[str, Any]:
    """
    Get theme information.
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        Theme information dictionary
        
    Raises:
        KeyError: If theme doesn't exist
    """
    if theme_name not in ALL_THEMES:
        raise KeyError(f"Theme '{theme_name}' not found")
    
    theme = ALL_THEMES[theme_name]
    return {
        "name": theme["name"],
        "description": theme["description"],
        "author": theme["author"],
        "version": theme["version"],
        "is_gemini": theme_name in GEMINI_THEMES,
        "preview_colors": {
            "primary": theme["primary"],
            "secondary": theme["secondary"],
            "accent": theme["accent"],
            "success": theme["success"],
            "warning": theme["warning"],
            "error": theme["error"]
        }
    }
