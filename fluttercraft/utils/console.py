"""
Console Utilities

Rich console setup and management utilities for FlutterCraft.
Provides themed console instances and output formatting.
"""

import os
import sys
from typing import Optional, TextIO

from rich.console import Console
from rich.theme import Theme
from rich.highlighter import RegexHighlighter

from fluttercraft.utils.platform import get_terminal_size, is_windows


class FlutterHighlighter(RegexHighlighter):
    """Custom highlighter for Flutter-related content."""
    
    base_style = "flutter."
    highlights = [
        # Flutter commands
        r"(?P<command>flutter\s+(?:create|build|run|test|doctor|channel|upgrade|downgrade))",
        # Dart files
        r"(?P<dart_file>\w+\.dart)",
        # YAML files
        r"(?P<yaml_file>\w+\.ya?ml)",
        # Package names
        r"(?P<package>package:\s*\w+)",
        # Version numbers
        r"(?P<version>\d+\.\d+\.\d+(?:\+\d+)?)",
        # File paths
        r"(?P<path>(?:[a-zA-Z]:)?[/\\](?:[^/\\:\s]+[/\\])*[^/\\:\s]*)",
        # URLs
        r"(?P<url>https?://[^\s]+)",
        # Email addresses
        r"(?P<email>[\w\.-]+@[\w\.-]+\.\w+)",
    ]


def get_default_theme() -> Theme:
    """
    Get the default Rich theme for FlutterCraft.
    
    Returns:
        Default theme instance
    """
    return Theme({
        # Basic colors
        "primary": "blue",
        "secondary": "cyan", 
        "accent": "magenta",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "blue",
        "muted": "dim white",
        
        # Component styles
        "panel.border": "blue",
        "panel.title": "bold blue",
        "table.header": "bold magenta",
        "progress.bar": "blue",
        "progress.percentage": "cyan",
        "status.spinner": "cyan",
        
        # Flutter highlighter styles
        "flutter.command": "bold green",
        "flutter.dart_file": "cyan",
        "flutter.yaml_file": "yellow",
        "flutter.package": "blue",
        "flutter.version": "magenta",
        "flutter.path": "dim cyan",
        "flutter.url": "blue underline",
        "flutter.email": "blue",
        
        # Special styles
        "prompt": "bold blue",
        "help": "dim cyan",
        "code": "dim white on grey23",
    })


def setup_console(
    verbose: bool = False,
    force_terminal: Optional[bool] = None,
    width: Optional[int] = None,
    file: Optional[TextIO] = None,
    theme: Optional[Theme] = None
) -> Console:
    """
    Setup and configure a Rich console instance.
    
    Args:
        verbose: Enable verbose output
        force_terminal: Force terminal detection
        width: Console width (auto-detected if None)
        file: Output file (stdout if None)
        theme: Console theme (default if None)
        
    Returns:
        Configured console instance
    """
    # Auto-detect terminal size if width not provided
    if width is None:
        terminal_width, _ = get_terminal_size()
        width = terminal_width
    
    # Use default theme if none provided
    if theme is None:
        theme = get_default_theme()
    
    # Use stdout if no file provided
    if file is None:
        file = sys.stdout
    
    # Create console with configuration
    console = Console(
        file=file,
        width=width,
        force_terminal=force_terminal,
        theme=theme,
        highlighter=FlutterHighlighter(),
        markup=True,
        emoji=True,
        highlight=True,
        log_time=verbose,
        log_path=verbose,
        record=True,  # Enable recording for export features
    )
    
    return console


def create_error_console(theme: Optional[Theme] = None) -> Console:
    """
    Create a console instance for error output.
    
    Args:
        theme: Console theme (default if None)
        
    Returns:
        Console instance configured for stderr
    """
    if theme is None:
        theme = get_default_theme()
    
    return Console(
        file=sys.stderr,
        theme=theme,
        highlighter=FlutterHighlighter(),
        markup=True,
        emoji=True,
        force_terminal=True,
        record=True,
    )


def get_console_width(console: Console) -> int:
    """
    Get the effective width of a console.
    
    Args:
        console: Console instance
        
    Returns:
        Console width in characters
    """
    return console.width if console.width else 80


def is_terminal_capable() -> bool:
    """
    Check if the terminal supports Rich features.
    
    Returns:
        True if terminal supports colors and formatting
    """
    # Check if we're in a real terminal
    if not sys.stdout.isatty():
        return False
    
    # Check for Windows terminal capabilities
    if is_windows():
        # Windows Terminal, PowerShell, and modern Command Prompt support colors
        term = os.environ.get("TERM", "")
        wt_session = os.environ.get("WT_SESSION")
        
        if wt_session or "xterm" in term:
            return True
            
        # Try to enable ANSI colors on Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except (ImportError, AttributeError, OSError):
            return False
    
    # Unix-like systems generally support colors
    return True


def format_command_output(output: str, console: Console) -> str:
    """
    Format command output for display.
    
    Args:
        output: Raw command output
        console: Console instance for formatting
        
    Returns:
        Formatted output string
    """
    # Basic formatting for command output
    lines = output.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        # Highlight error patterns
        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
            formatted_lines.append(f"[red]{line}[/red]")
        elif any(keyword in line.lower() for keyword in ['warning', 'warn']):
            formatted_lines.append(f"[yellow]{line}[/yellow]")
        elif any(keyword in line.lower() for keyword in ['success', 'completed', 'done']):
            formatted_lines.append(f"[green]{line}[/green]")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def print_banner(console: Console, title: str, subtitle: str = "") -> None:
    """
    Print a formatted banner.
    
    Args:
        console: Console instance
        title: Main title text
        subtitle: Optional subtitle text
    """
    from rich.panel import Panel
    from rich.align import Align
    
    content = f"[bold]{title}[/bold]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    
    banner = Panel(
        Align.center(content),
        style="blue",
        padding=(1, 2)
    )
    
    console.print(banner)


def print_section_header(console: Console, title: str) -> None:
    """
    Print a section header.
    
    Args:
        console: Console instance
        title: Section title
    """
    console.rule(f"[bold blue]{title}[/bold blue]")


def print_success(console: Console, message: str) -> None:
    """
    Print a success message.
    
    Args:
        console: Console instance
        message: Success message
    """
    console.print(f"[green]✅ {message}[/green]")


def print_warning(console: Console, message: str) -> None:
    """
    Print a warning message.
    
    Args:
        console: Console instance
        message: Warning message
    """
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_error(console: Console, message: str) -> None:
    """
    Print an error message.
    
    Args:
        console: Console instance
        message: Error message
    """
    console.print(f"[red]❌ {message}[/red]")


def print_info(console: Console, message: str) -> None:
    """
    Print an info message.
    
    Args:
        console: Console instance
        message: Info message
    """
    console.print(f"[blue]ℹ️  {message}[/blue]")
