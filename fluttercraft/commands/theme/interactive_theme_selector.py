"""Interactive theme selector with live preview for FlutterCraft CLI."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout as PTLayout
from prompt_toolkit.formatted_text import HTML

from fluttercraft.utils.themes import get_theme_manager, AVAILABLE_THEMES
from fluttercraft.utils.themes.gradient import create_gradient_text

console = Console()


class InteractiveThemeSelector:
    """Interactive theme selector with live preview."""

    def __init__(self):
        """Initialize the theme selector."""
        self.theme_manager = get_theme_manager()
        self.current_theme = self.theme_manager.get_current_theme()
        self.themes = list(AVAILABLE_THEMES.keys())
        self.selected_index = self.themes.index(self.current_theme.name)
        self.preview_lines = self._generate_preview_lines()

    def _generate_preview_lines(self) -> list[str]:
        """Generate sample code lines for preview."""
        return [
            "# Sample Python Code",
            "def fibonacci(n):",
            "    a, b = 0, 1",
            "    for _ in range(n):",
            "        a, b = b, a + b",
            "    return a",
            "",
            "# Sample output",
            "✓ Success: Installation complete",
            "✗ Error: Command not found",
            "⚠ Warning: Update available",
            "ℹ Info: Use /help for commands",
        ]

    def _render_theme_list(self) -> str:
        """Render the theme list with selection indicator."""
        lines = []
        lines.append("╭─ Select Theme ─────────────────────╮")
        lines.append("│                                    │")

        for i, theme_name in enumerate(self.themes):
            theme = AVAILABLE_THEMES[theme_name]
            indicator = "●" if i == self.selected_index else " "
            current_marker = (
                " (current)" if theme_name == self.current_theme.name else ""
            )

            # Format: " ● 1. Gemini (current)"
            line = f"│ {indicator}  {i + 1}. {theme.name.title():<20}{current_marker:<10} │"
            lines.append(line)

        lines.append("│                                    │")
        lines.append("╰────────────────────────────────────╯")
        return "\n".join(lines)

    def _render_preview(self) -> str:
        """Render the preview panel with selected theme."""
        theme = AVAILABLE_THEMES[self.themes[self.selected_index]]
        lines = []

        lines.append("╭─ Preview ──────────────────────────────────────╮")
        lines.append(f"│ Theme: {theme.name.title():<38} │")
        lines.append(f"│ {theme.description[:44]:<44} │")
        lines.append("├────────────────────────────────────────────────┤")

        # Show sample code with theme colors
        for line in self.preview_lines:
            if line.startswith("#"):
                # Comment
                display = f"│ {line:<46} │"
            elif "✓" in line:
                # Success
                display = f"│ {line:<46} │"
            elif "✗" in line:
                # Error
                display = f"│ {line:<46} │"
            elif "⚠" in line:
                # Warning
                display = f"│ {line:<46} │"
            elif "ℹ" in line:
                # Info
                display = f"│ {line:<46} │"
            else:
                display = f"│ {line:<46} │"
            lines.append(display)

        lines.append("╰────────────────────────────────────────────────╯")
        return "\n".join(lines)

    def _render_help(self) -> str:
        """Render help text."""
        return "Use ↑/↓ arrows to navigate, Enter to select, q to quit"

    def run(self) -> Optional[str]:
        """Run the interactive theme selector.

        Returns:
            Selected theme name or None if cancelled
        """
        kb = KeyBindings()
        selected_theme = [None]  # Use list to allow modification in nested function

        @kb.add(Keys.Up)
        def _(event):
            """Move selection up."""
            self.selected_index = (self.selected_index - 1) % len(self.themes)
            event.app.invalidate()

        @kb.add(Keys.Down)
        def _(event):
            """Move selection down."""
            self.selected_index = (self.selected_index + 1) % len(self.themes)
            event.app.invalidate()

        @kb.add(Keys.Enter)
        def _(event):
            """Select current theme."""
            selected_theme[0] = self.themes[self.selected_index]
            event.app.exit()

        @kb.add("q")
        @kb.add("Q")
        @kb.add(Keys.Escape)
        def _(event):
            """Quit without selecting."""
            event.app.exit()

        def get_content():
            """Get the current display content."""
            theme_list = self._render_theme_list()
            preview = self._render_preview()
            help_text = self._render_help()

            # Combine side by side
            theme_lines = theme_list.split("\n")
            preview_lines = preview.split("\n")

            combined = []
            max_lines = max(len(theme_lines), len(preview_lines))

            for i in range(max_lines):
                left = theme_lines[i] if i < len(theme_lines) else " " * 40
                right = preview_lines[i] if i < len(preview_lines) else " " * 52
                combined.append(f"{left}  {right}")

            combined.append("")
            combined.append(help_text)

            return "\n".join(combined)

        # Create the application
        text_control = FormattedTextControl(
            text=get_content,
            focusable=True,
        )

        window = Window(content=text_control)
        layout = PTLayout(window)

        app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
        )

        app.run()
        return selected_theme[0]


def run_interactive_theme_selector() -> bool:
    """Run the interactive theme selector and apply selection.

    Returns:
        True if theme was changed, False otherwise
    """
    console.print("\n[bold cyan]Interactive Theme Selector[/]\n")

    selector = InteractiveThemeSelector()
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
