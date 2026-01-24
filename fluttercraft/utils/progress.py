"""
Progress indicators for FlutterCraft CLI.
Uses Rich Progress for beautiful, theme-aware progress bars.
"""
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    DownloadColumn,
    TransferSpeedColumn,
)
from rich.console import Console
from typing import Optional

from fluttercraft.utils.themed_display import get_theme

def create_progress(console: Optional[Console] = None, transient: bool = True) -> Progress:
    """
    Create a standard themed progress bar.
    """
    theme = get_theme()
    accent = theme.accent_cyan
    
    return Progress(
        SpinnerColumn(spinner_name="dots", style=f"bold {accent}"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, complete_style=accent, finished_style=theme.semantic.status_success),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=transient,
    )

def create_download_progress(console: Optional[Console] = None, transient: bool = True) -> Progress:
    """
    Create a themed progress bar optimized for downloads.
    """
    theme = get_theme()
    accent = theme.accent_cyan
    
    return Progress(
        SpinnerColumn(spinner_name="dots", style=f"bold {accent}"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, complete_style=accent),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=transient,
    )
