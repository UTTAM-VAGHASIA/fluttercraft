"""Rich-based interactive theme selector with live preview."""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
import msvcrt  # For Windows key detection

from fluttercraft.utils.themes import get_theme_manager, PROFESSIONAL_THEMES
from fluttercraft.utils.themes.gradient import create_gradient_text

console = Console()


class RichThemeSelector:
    """Interactive theme selector using Rich library."""

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

    def _create_theme_list_panel(self) -> Panel:
        """Create the theme list panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Indicator", width=3)
        table.add_column("Number", width=3)
        table.add_column("Name", width=20)
        table.add_column("Status", width=10)

        for i, theme_name in enumerate(self.themes):
            theme = PROFESSIONAL_THEMES[theme_name]
            indicator = "●" if i == self.selected_index else " "
            number = f"{i + 1}."
            name = theme.name.title()
            status = (
                "[dim](current)[/]" if theme_name == self.current_theme.name else ""
            )

            # Highlight selected row
            if i == self.selected_index:
                table.add_row(
                    f"[bold cyan]{indicator}[/]",
                    f"[bold cyan]{number}[/]",
                    f"[bold cyan]{name}[/]",
                    f"[cyan]{status}[/]",
                )
            else:
                table.add_row(indicator, number, name, status)

        return Panel(
            table,
            title="[bold]Select Theme[/]",
            border_style="cyan",
            padding=(1, 2),
        )

    def _create_preview_panel(self) -> Panel:
        """Create the preview panel for selected theme."""
        theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]

        # Create preview content
        preview = Text()

        # Theme info
        preview.append(f"Theme: ", style="bold")
        preview.append(f"{theme.name.title()}\n", style=f"bold {theme.accent_cyan}")
        preview.append(f"Type: ", style="bold")
        preview.append(f"{theme.type.value.title()}\n\n", style="dim")
        preview.append(f"{theme.description}\n\n", style="dim")

        # Color palette
        preview.append("Color Palette:\n", style="bold")
        colors = [
            ("Blue", theme.accent_blue),
            ("Purple", theme.accent_purple),
            ("Cyan", theme.accent_cyan),
            ("Green", theme.accent_green),
            ("Yellow", theme.accent_yellow),
            ("Red", theme.accent_red),
        ]

        for color_name, color_value in colors:
            preview.append(f"  {color_name}: ", style="dim")
            preview.append("████", style=f"bold {color_value}")
            preview.append("\n")

        preview.append("\nSample Messages:\n", style="bold")
        preview.append("  ✓ Success message\n", style=theme.semantic.status_success)
        preview.append("  ✗ Error message\n", style=theme.semantic.status_error)
        preview.append("  ⚠ Warning message\n", style=theme.semantic.status_warning)
        preview.append("  ℹ Info message\n", style=theme.semantic.status_info)

        # Gradient preview
        if theme.gradient_colors:
            preview.append("\nGradient Preview:\n", style="bold")
            gradient_text = create_gradient_text(
                "FlutterCraft", theme.gradient_colors, bold=True
            )
            preview.append(gradient_text)

        return Panel(
            preview,
            title="[bold]Preview[/]",
            border_style="cyan",
            padding=(1, 2),
        )

    def _create_help_panel(self) -> Panel:
        """Create the help panel."""
        help_text = Text()
        help_text.append("↑/↓", style="bold cyan")
        help_text.append(" Navigate  ")
        help_text.append("Enter", style="bold green")
        help_text.append(" Select  ")
        help_text.append("Q/Esc", style="bold red")
        help_text.append(" Cancel")

        return Panel(help_text, border_style="dim", padding=(0, 2))

    def _create_layout(self) -> Layout:
        """Create the main layout."""
        layout = Layout()

        layout.split_column(
            Layout(name="main", ratio=10),
            Layout(name="help", size=3),
        )

        layout["main"].split_row(
            Layout(name="themes", ratio=1),
            Layout(name="preview", ratio=2),
        )

        layout["themes"].update(self._create_theme_list_panel())
        layout["preview"].update(self._create_preview_panel())
        layout["help"].update(self._create_help_panel())

        return layout

    def run(self) -> Optional[str]:
        """Run the interactive theme selector.

        Returns:
            Selected theme name or None if cancelled
        """
        console.print("\n[bold cyan]Interactive Theme Selector[/]\n")

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
                                live.update(self._create_layout())
                            elif key == b"P":  # Down arrow
                                self.selected_index = (self.selected_index + 1) % len(
                                    self.themes
                                )
                                live.update(self._create_layout())
                        elif key == b"\r":  # Enter
                            return self.themes[self.selected_index]
                        elif key in (b"q", b"Q", b"\x1b"):  # q, Q, or Escape
                            return None

        except KeyboardInterrupt:
            return None


def run_rich_theme_selector() -> bool:
    """Run the Rich-based interactive theme selector.

    Returns:
        True if theme was changed, False otherwise
    """
    selector = RichThemeSelector()
    selected = selector.run()

    if selected:
        theme_manager = get_theme_manager()
        if theme_manager.set_theme(selected):
            theme = theme_manager.get_current_theme()
            console.print(f"\n[green]✓ Theme changed to '{theme.name}'[/]")

            # Show preview
            if theme.gradient_colors:
                preview = create_gradient_text(
                    "FlutterCraft", theme.gradient_colors, bold=True
                )
                console.print("\nPreview: ", end="")
                console.print(preview)

            console.print(
                "\n[dim]Restart FlutterCraft to see the full theme changes.[/]\n"
            )
            return True

    console.print("\n[yellow]Theme selection cancelled[/]\n")
    return False
