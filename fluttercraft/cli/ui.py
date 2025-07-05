"""
CLI UI Components

This module provides UI components for the FlutterCraft CLI interface,
inspired by the GEMINI CLI design with prompt boxes, status bars,
and other interactive elements.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.box import Box, ROUNDED
from rich.align import Align
from rich.text import Text
from rich.style import Style
from rich.prompt import Prompt
from rich.live import Live
from rich.layout import Layout

from fluttercraft import __version__
from fluttercraft.cli.themes.ascii_art import get_appropriate_logo
from fluttercraft.utils.platform import get_terminal_size, format_path_for_display


# Custom box for prompt - using ROUNDED box with modifications
PROMPT_BOX = ROUNDED


def display_welcome_screen(console: Console) -> None:
    """
    Display the welcome screen with ASCII logo.
    
    Args:
        console: Rich console instance
    """
    # Get appropriate logo based on terminal width
    width, _ = get_terminal_size()
    logo = get_appropriate_logo(width)
    
    # Add color styling to logo
    primary_color = console._theme_stack.get("primary", Style(color="blue"))
    styled_logo = Text(logo, style=primary_color)
    
    # Create welcome message
    version_text = f"FlutterCraft v{__version__}"
    welcome_text = "\nTips for getting started:\n1. Ask questions, edit files, or run commands.\n2. Be specific for the best results.\n3. Type 'help' for more information."
    
    # Print styled logo and welcome message
    console.print(styled_logo)
    console.print(f"\n{version_text}")
    console.print(welcome_text)
    console.print()


def display_status_bar(
    console: Console,
    current_dir: Path,
    branch: Optional[str] = None,
    status_message: Optional[str] = None
) -> None:
    """
    Display a status bar at the bottom of the console.
    
    Args:
        console: Rich console instance
        current_dir: Current working directory
        branch: Git branch name if available
        status_message: Status message to display
    """
    width, _ = get_terminal_size()
    
    # Format paths for display
    dir_display = format_path_for_display(current_dir)
    
    # Truncate if too long
    max_dir_length = min(40, width // 2)
    if len(dir_display) > max_dir_length:
        dir_display = f"...{dir_display[-(max_dir_length-3):]}"
    
    # Create left part (directory)
    left_part = f"[dim]{dir_display}[/dim]"
    
    # Create middle part (branch)
    middle_part = ""
    if branch:
        middle_part = f"[dim]({branch})[/dim]"
    
    # Create right part (status)
    right_part = ""
    if status_message:
        right_part = f"[dim]{status_message}[/dim]"
    
    # Calculate padding to justify items
    total_visible_length = len(dir_display) + len(branch or "") + len(status_message or "")
    padding = max(0, width - total_visible_length - 4)  # 4 for safety margin
    
    # Create status bar with justified content
    status_bar = Text()
    status_bar.append(left_part)
    
    # Add appropriate spacing
    if middle_part:
        spaces_before_middle = padding // 2
        status_bar.append(" " * spaces_before_middle)
        status_bar.append(middle_part)
    
    if right_part:
        spaces_before_right = padding - (padding // 2)
        status_bar.append(" " * spaces_before_right)
        status_bar.append(right_part)
    
    # Print status bar
    console.print(status_bar)


def create_prompt_box(console: Console, prompt_message: str = ">") -> str:
    """
    Create a dynamic prompt box for user input similar to GEMINI CLI.
    The box expands automatically as the user types multi-line input.
    
    Args:
        console: Rich console instance
        prompt_message: Message to display in the prompt
        
    Returns:
        User input
    """
    from rich.panel import Panel
    from rich.text import Text
    import textwrap
    import sys
    
    # Import platform-specific modules
    if sys.platform == 'win32':
        import msvcrt
    else:
        import tty
    
    width, _ = get_terminal_size()
    primary_color = console._theme_stack.get("primary", Style(color="blue"))
    
    # Show instructions
    console.print("[dim]Type your message. Press Enter to submit.[/dim]")
    console.print("[dim]Type [bold].ml[/bold] to enter multi-line mode.[/dim]")
    console.print("[dim]Type [bold]exit[/bold] to quit.[/dim]")
    
    # Create a panel for the prompt
    panel = Panel(
        "",
        title=f" {prompt_message} ",
        title_align="left",
        border_style=primary_color,
        padding=(1, 1),
        width=width - 4  # Leave some margin
    )
    
    # Display the panel
    console.print(panel)
    
    # Move cursor up to inside the panel
    sys.stdout.write("\033[F\033[F")  # Move up two lines
    sys.stdout.write("\033[2C")  # Move right 2 spaces for padding
    sys.stdout.flush()
    
    # Get user input
    try:
        user_input = input()
        
        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            return "/exit"
        
        # Check if user wants multi-line mode
        if user_input.strip() == ".ml":
            console.print("\n[bold blue]Multi-line mode:[/bold blue]")
            console.print("[dim]Enter your text. Type [bold].end[/bold] on a new line to finish.[/dim]")
            
            lines = []
            while True:
                line = input()
                if line.strip() == ".end":
                    break
                lines.append(line)
            
            # Join all lines into a single string
            user_input = '\n'.join(lines)
            
            # Display the multi-line input in a panel
            console.print(Panel(
                user_input,
                title="Your input",
                border_style=primary_color,
                padding=(1, 1),
                width=width - 4
            ))
        
        return user_input
        
    except KeyboardInterrupt:
        # Let the core.py handle the KeyboardInterrupt
        raise KeyboardInterrupt


def display_full_interface(console: Console, current_dir: Path) -> str:
    """
    Display the full interface with logo, prompt, and status bar.
    
    Args:
        console: Rich console instance
        current_dir: Current working directory
        
    Returns:
        User input
    """
    # Clear screen
    console.clear()
    
    # Display welcome screen
    display_welcome_screen(console)
    
    # Display prompt box
    user_input = create_prompt_box(console)
    
    # Display status bar
    display_status_bar(console, current_dir)
    
    return user_input


def create_interactive_interface(console: Console, current_dir: Path) -> Layout:
    """
    Create an interactive interface with live updates.
    
    Args:
        console: Rich console instance
        current_dir: Current working directory
        
    Returns:
        Rich layout for the interface
    """
    layout = Layout()
    
    # Create header section with logo
    layout.split(
        Layout(name="header", size=10),
        Layout(name="body", ratio=5),
        Layout(name="footer", size=1),
    )
    
    # Get appropriate logo based on terminal width
    width, _ = get_terminal_size()
    logo = get_appropriate_logo(width)
    
    # Add color styling to logo
    primary_color = console._theme_stack.get("primary", Style(color="blue"))
    styled_logo = Text(logo, style=primary_color)
    
    # Set header content
    version_text = f"FlutterCraft v{__version__}"
    welcome_text = "\nTips for getting started:\n1. Ask questions, edit files, or run commands.\n2. Be specific for the best results.\n3. Type 'help' for more information."
    
    header_content = styled_logo + Text(f"\n{version_text}\n{welcome_text}")
    layout["header"].update(header_content)
    
    # Create prompt panel
    prompt_panel = Panel(
        "",
        box=PROMPT_BOX,

        padding=(1, 1),
        border_style=console._theme_stack.get("primary", Style(color="blue"))
    )
    layout["body"].update(prompt_panel)
    
    # Create status bar
    dir_display = format_path_for_display(current_dir)
    status_text = Text(f"{dir_display}", style="dim")
    layout["footer"].update(status_text)
    
    return layout


def get_user_input_gemini_style(console: Console) -> str:
    """
    Get user input in GEMINI CLI style with custom prompt box.
    
    Args:
        console: Rich console instance
        
    Returns:
        User input
    """
    # Show the prompt box
    user_input = create_prompt_box(console)
    
    # Add empty line after input
    console.print()
    
    return user_input 