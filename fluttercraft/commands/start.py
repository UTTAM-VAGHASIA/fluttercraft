"""Start command for FlutterCraft CLI with beautiful interface."""

import time

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from prompt_toolkit.history import FileHistory

from fluttercraft.utils.platform_utils import get_platform_info
from fluttercraft.utils.beautiful_display import show_platform_not_supported
from fluttercraft.utils.themed_display import (
    display_themed_welcome_header,
    display_animated_welcome_header,
    create_themed_ascii_art,
    clear_screen,
    get_welcome_header_content,
    get_theme,
)
from fluttercraft.utils.beautiful_prompt import (
    prompt_user_with_border,
    FlutterCraftCompleter,
    update_command_completions,
)
from fluttercraft.commands.flutter_commands import check_flutter_version
from fluttercraft.commands.fvm_commands import check_fvm_version
from fluttercraft.commands.core import CommandContext
from fluttercraft.commands.bootstrap import build_command_system
from fluttercraft.utils.themed_console import create_themed_console
from fluttercraft.utils.screen_layout import FlutterCraftScreen
from fluttercraft.utils.themes.theme_manager import get_theme_manager

# Use themed console factory
console = create_themed_console()


def start_command():
    """
    Start the interactive CLI session with beautiful interface.
    This is the main command that users will use to start creating Flutter apps.
    """
    import platform

    # Check platform first
    current_platform = platform.system()

    # If macOS or Linux, show coming soon message
    # Removed Linux check as we are testing on Linux
    if current_platform in ["Darwin"]:
        show_platform_not_supported(current_platform)
        return

    # Initialize theme manager and screen layout
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    screen = FlutterCraftScreen(theme)

    # Show loading spinner
    spinner = Spinner("dots", text="[cyan]Loading system information...[/]")
    with Live(spinner, console=console, refresh_per_second=10):
        # Get platform information (fast, no external calls)
        platform_info = get_platform_info()
        time.sleep(0.3)  # Small delay to show spinner

        # Check Flutter installation and version (silent mode)
        flutter_info = check_flutter_version(silent=True)
        time.sleep(0.3)  # Small delay to show spinner

        # Check FVM installation (silent mode)
        fvm_info = check_fvm_version(silent=True)
        time.sleep(0.3)  # Small delay to show spinner

    # Prepare header content
    ascii_art = create_themed_ascii_art()
    header_lines = get_welcome_header_content(platform_info, flutter_info, fvm_info)
    
    # Combine header lines into a single Renderable
    from rich.console import Group
    info_renderable = Group(*header_lines)
    
    # Update screen header
    screen.update_header(ascii_art, info_renderable)

    # Create completer and persistent file-based history
    from pathlib import Path

    completer = FlutterCraftCompleter()
    history_file = Path.home() / ".fluttercraft" / "history"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history = FileHistory(str(history_file))

    executor = build_command_system(console)
    update_command_completions(executor.registry.to_metadata())

    context = CommandContext(
        platform_info=platform_info,
        flutter_info=flutter_info,
        fvm_info=fvm_info,
        console=console,
        prompt_history=history,
    )

    from fluttercraft.utils.animations.engine import AnimationEngine
    from rich.text import Text
    engine = AnimationEngine(console=console)

    # Main REPL loop with Full-Screen Live Layout
    # The prompt_user_with_border function ALREADY creates a "full screen feel" via its layout.
    # The goal "Full Window Theming" means the BACKGROUND should be colored.
    # This is now handled by create_themed_console() which sets style="on {bg}".
    
    # Clear screen and display themed static header
    clear_screen()
    
    display_animated_welcome_header(
        platform_info, flutter_info, fvm_info, show_ascii=True
    )

    # Main REPL loop
    while True:
        try:
            # Ensure background color is reset/maintained
            # prompt_user_with_border uses prompt_toolkit styling which we already customized.
            
            # Get user input with beautiful bordered prompt
            command = prompt_user_with_border(completer, history)

            # Execute command
            result = executor.dispatch(command, context)

            if result.message:
                # Convert message string to Rich Text for animation if it's not already
                msg_renderable = result.message
                if isinstance(msg_renderable, str):
                    # Check if it has Rich tags
                    if "[" in msg_renderable and "]" in msg_renderable:
                        from rich.text import Text
                        msg_renderable = Text.from_markup(msg_renderable)
                
                # Animate feedback
                if result.success:
                    # Sleek success: slight slide up from bottom (200ms)
                    engine.slide_in(msg_renderable, direction="bottom", duration=0.2, start_offset=1)
                else:
                    # Subtle error: shake (200ms)
                    engine.shake(msg_renderable, duration=0.2, intensity=1)
                
                # Print the final static version
                console.print(result.message)

            # Display execution timing if available
            if result.execution_time is not None:
                # Format timing with appropriate color
                timing = result.execution_time

                # Color coding: green < 1s, yellow < 3s, red >= 3s
                if timing < 1.0:
                    color = "green"
                    icon = "⚡"
                elif timing < 3.0:
                    color = "yellow"
                    icon = "⏱️"
                else:
                    color = "red"
                    icon = "🐌"

                # Format timing display
                if timing < 0.001:  # Less than 1ms
                    timing_str = f"{timing * 1000:.2f}ms"
                elif timing < 1.0:  # Less than 1s
                    timing_str = f"{timing * 1000:.0f}ms"
                else:  # 1s or more
                    timing_str = f"{timing:.2f}s"

                console.print(
                    f"[dim]{icon} Executed in [{color}]{timing_str}[/{color}][/dim]"
                )

            if not result.should_continue:
                break

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n[yellow]Use '/quit' to exit FlutterCraft[/]")
            continue

        except EOFError:
            # Handle Ctrl+D as quit
            console.print("\n[yellow]Thank you for using FlutterCraft! Goodbye! 👋[/]")
            break

        except Exception as e:
            # Handle unexpected errors
            console.print(f"\n[bold red]An error occurred: {str(e)}[/]")
            console.print("[dim]Please report this issue if it persists.[/]")
            continue
