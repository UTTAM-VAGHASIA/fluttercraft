"""Live theme selector with code preview and dynamic UI updates."""

import sys
from typing import Optional
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.layout import Layout
from rich.live import Live
import msvcrt  # For Windows key detection

from fluttercraft.utils.themes import get_theme_manager
from fluttercraft.utils.themes.professional_themes import PROFESSIONAL_THEMES

console = Console()


class LiveThemeSelector:
    """Interactive theme selector with live UI updates."""

    def __init__(self):
        """Initialize the theme selector."""
        self.theme_manager = get_theme_manager()
        self.current_theme = self.theme_manager.get_current_theme()
        self.themes = list(PROFESSIONAL_THEMES.keys())
        self.selected_index = (
            self.themes.index(self.current_theme.name)
            if self.current_theme.name in self.themes
            else 0
        )

    def _get_code_sample(self) -> str:
        """Get sample code for preview."""
        return """# function
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

- print("Hello, " + name)
+ print(f"Hello, {name}!")"""

    def _create_theme_list_panel(self, theme) -> Panel:
        """Create the theme list panel with current theme colors."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Indicator", width=3)
        table.add_column("Number", width=4)
        table.add_column("Name", width=30)

        for i, theme_name in enumerate(self.themes):
            t = PROFESSIONAL_THEMES[theme_name]
            indicator = "●" if i == self.selected_index else " "
            number = f"{i + 1}."

            # Format name with type
            display_name = f"{t.name.replace('_', ' ').title()}"
            if t.type.value == "dark":
                display_name += " [dim](Dark)[/]"
            else:
                display_name += " [dim](Light)[/]"

            # Highlight selected row with theme colors
            if i == self.selected_index:
                table.add_row(
                    f"[bold {theme.accent_cyan}]{indicator}[/]",
                    f"[bold {theme.accent_cyan}]{number}[/]",
                    f"[bold {theme.accent_cyan}]{display_name}[/]",
                )
            else:
                table.add_row(
                    f"[{theme.foreground}]{indicator}[/]",
                    f"[{theme.foreground}]{number}[/]",
                    f"[{theme.foreground}]{display_name}[/]",
                )

        return Panel(
            table,
            title=f"[bold {theme.accent_purple}]> Select Theme[/]",
            border_style=theme.accent_cyan,
            padding=(1, 2),
            style=f"on {theme.background}",
        )

    def _create_preview_panel(self, theme) -> Panel:
        """Create the preview panel with syntax-highlighted code."""
        preview_theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]

        # Create syntax highlighted code
        code = self._get_code_sample()

        # Create custom syntax with theme colors
        syntax = Syntax(
            code,
            "python",
            theme="monokai",  # Base theme
            line_numbers=True,
            background_color=preview_theme.background,
        )

        # Create preview text with theme info
        preview_text = Text()
        preview_text.append(f"Theme: ", style=f"bold {theme.foreground}")
        preview_text.append(
            f"{preview_theme.name.replace('_', ' ').title()}\n",
            style=f"bold {preview_theme.accent_cyan}",
        )
        preview_text.append(f"Type: ", style=f"{theme.foreground}")
        preview_text.append(
            f"{preview_theme.type.value.title()}\n\n", style=f"dim {theme.foreground}"
        )

        # Group the text and syntax together
        preview_content = Group(preview_text, syntax)

        return Panel(
            preview_content,
            title=f"[bold {theme.accent_purple}]Preview[/]",
            border_style=theme.accent_cyan,
            padding=(1, 2),
            style=f"on {theme.background}",
        )

    def _create_help_panel(self, theme) -> Panel:
        """Create the help panel with theme colors."""
        help_text = Text()
        help_text.append("▲/▼", style=f"bold {theme.accent_cyan}")
        help_text.append(" Navigate  ", style=theme.foreground)
        help_text.append("Enter", style=f"bold {theme.accent_green}")
        help_text.append(" Select  ", style=theme.foreground)
        help_text.append("Q/Esc", style=f"bold {theme.accent_red}")
        help_text.append(" Cancel", style=theme.foreground)

        return Panel(
            help_text,
            border_style=f"dim {theme.gray}",
            padding=(0, 2),
            style=f"on {theme.background}",
        )

    def _create_layout(self) -> Layout:
        """Create the main layout with current theme colors."""
        # Get current theme for UI colors
        preview_theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]

        layout = Layout()

        layout.split_column(
            Layout(name="main", ratio=10),
            Layout(name="help", size=3),
        )

        layout["main"].split_row(
            Layout(name="themes", ratio=1),
            Layout(name="preview", ratio=2),
        )

        layout["themes"].update(self._create_theme_list_panel(preview_theme))
        layout["preview"].update(self._create_preview_panel(preview_theme))
        layout["help"].update(self._create_help_panel(preview_theme))

        return layout

    def run(self) -> Optional[str]:
        """Run the interactive theme selector.

        Returns:
            Selected theme name or None if cancelled
        """
        console.print(f"\n[bold cyan]Interactive Theme Selector[/]\n")

        try:
            with Live(
                self._create_layout(),
                console=console,
                refresh_per_second=10,
                screen=False,
            ) as live:
                while True:
                    # Read key input (Windows-specific)
                    if msvcrt.kbhit():
                        key = msvcrt.getch()

                        # Arrow keys are two-byte sequences
                        if key == b"\xe0":  # Special key prefix
                            key = msvcrt.getch()
                            if key == b"H":  # Up arrow
                                self.selected_index = (self.selected_index - 1) % len(
                                    self.themes
                                )
                                # Update entire layout with new theme colors
                                live.update(self._create_layout())
                            elif key == b"P":  # Down arrow
                                self.selected_index = (self.selected_index + 1) % len(
                                    self.themes
                                )
                                # Update entire layout with new theme colors
                                live.update(self._create_layout())
                        elif key == b"\r":  # Enter
                            return self.themes[self.selected_index]
                        elif key in (b"q", b"Q", b"\x1b"):  # q, Q, or Escape
                            return None

        except KeyboardInterrupt:
            return None


def run_live_theme_selector() -> bool:
    """Run the live theme selector.

    Returns:
        True if theme was changed, False otherwise
    """
    selector = LiveThemeSelector()
    selected = selector.run()

    if selected:
        theme_manager = get_theme_manager()
        if theme_manager.set_theme(selected):
            theme = theme_manager.get_current_theme()
            console.print(
                f"\n[green]✓ Theme changed to '{theme.name.replace('_', ' ').title()}'[/]"
            )
            console.print(
                "\n[dim]Restart FlutterCraft to see the full theme changes.[/]\n"
            )
            return True

    console.print("\n[yellow]Theme selection cancelled[/]\n")
    return False
