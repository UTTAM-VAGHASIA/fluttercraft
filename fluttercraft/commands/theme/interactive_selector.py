"""Interactive theme selector using prompt_toolkit for smooth rendering."""

from typing import Optional
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML, FormattedText
from prompt_toolkit.widgets import Frame
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
import io

from fluttercraft.utils.themes import get_theme_manager
from fluttercraft.utils.themes.professional_themes import PROFESSIONAL_THEMES

console = Console()


class InteractiveThemeSelector:
    """Interactive theme selector with smooth rendering."""

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
        self.result = None

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

    def _get_theme_list_text(self) -> FormattedText:
        """Get formatted text for theme list."""
        theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]
        lines = []

        lines.append(("", "\n"))

        for i, theme_name in enumerate(self.themes):
            t = PROFESSIONAL_THEMES[theme_name]
            indicator = "●" if i == self.selected_index else " "
            number = f"{i + 1:2}."
            display_name = f"{t.name.replace('_', ' ').title()}"
            type_label = f"({t.type.value.title()})"

            if i == self.selected_index:
                # Highlighted row
                lines.append(
                    (
                        "class:selected",
                        f"  {indicator} {number} {display_name:<25} {type_label}\n",
                    )
                )
            else:
                # Normal row
                lines.append(
                    ("", f"  {indicator} {number} {display_name:<25} {type_label}\n")
                )

        lines.append(("", "\n"))
        return FormattedText(lines)

    def _get_preview_text(self) -> FormattedText:
        """Get formatted text for preview panel."""
        preview_theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]
        lines = []

        lines.append(("", "\n"))
        lines.append(("class:preview-title", f"  Theme: "))
        lines.append(
            ("class:preview-value", f"{preview_theme.name.replace('_', ' ').title()}\n")
        )
        lines.append(("class:preview-title", f"  Type: "))
        lines.append(("", f"{preview_theme.type.value.title()}\n\n"))

        # Add code preview
        code_lines = self._get_code_sample().split("\n")
        for i, line in enumerate(code_lines, 1):
            if line.startswith("#"):
                lines.append(("class:comment", f"  {i:2} {line}\n"))
            elif line.startswith("-"):
                lines.append(("class:removed", f"  {i:2} {line}\n"))
            elif line.startswith("+"):
                lines.append(("class:added", f"  {i:2} {line}\n"))
            elif "def " in line or "for " in line or "return " in line:
                lines.append(("class:keyword", f"  {i:2} {line}\n"))
            else:
                lines.append(("", f"  {i:2} {line}\n"))

        lines.append(("", "\n"))
        return FormattedText(lines)

    def _get_help_text(self) -> FormattedText:
        """Get formatted text for help panel."""
        return FormattedText(
            [
                ("", "  "),
                ("class:help-key", "↑/↓"),
                ("", " Navigate  "),
                ("class:help-key", "Enter"),
                ("", " Select  "),
                ("class:help-key", "Q/Esc"),
                ("", " Cancel  "),
            ]
        )

    def _create_layout(self) -> Layout:
        """Create the application layout."""
        theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]

        # Theme list window
        theme_list_window = Window(
            content=FormattedTextControl(
                text=self._get_theme_list_text,
                focusable=False,
            ),
            width=42,
        )

        # Preview window
        preview_window = Window(
            content=FormattedTextControl(
                text=self._get_preview_text,
                focusable=False,
            ),
        )

        # Help window
        help_window = Window(
            content=FormattedTextControl(
                text=self._get_help_text,
                focusable=False,
            ),
            height=1,
        )

        # Main layout
        body = HSplit(
            [
                VSplit(
                    [
                        Frame(theme_list_window, title="> Select Theme"),
                        Frame(preview_window, title="Preview"),
                    ]
                ),
                Frame(help_window),
            ]
        )

        return Layout(body)

    def _get_style(self):
        """Get style for the application."""
        theme = PROFESSIONAL_THEMES[self.themes[self.selected_index]]

        from prompt_toolkit.styles import Style

        return Style.from_dict(
            {
                # Selected row with theme's accent color
                "selected": f"bg:{theme.accent_cyan} {theme.background}",
                # Default text with theme background
                "": f"{theme.foreground} bg:{theme.background}",
                # Frame borders
                "frame.border": f"{theme.accent_cyan}",
                "frame.label": f"bold {theme.accent_purple}",
                # Preview styles
                "preview-title": f"bold {theme.foreground} bg:{theme.background}",
                "preview-value": f"{theme.accent_cyan} bg:{theme.background}",
                "comment": f"{theme.comment} bg:{theme.background}",
                "keyword": f"{theme.accent_purple} bg:{theme.background}",
                "added": f"{theme.accent_green} bg:{theme.background}",
                "removed": f"{theme.accent_red} bg:{theme.background}",
                "help-key": f"bold {theme.accent_cyan} bg:{theme.background}",
            }
        )

    def run(self) -> Optional[str]:
        """Run the interactive selector.

        Returns:
            Selected theme name or None if cancelled
        """
        # Create key bindings that recreate layout on navigation
        kb = KeyBindings()

        @kb.add("up")
        def _(event):
            """Move selection up."""
            self.selected_index = (self.selected_index - 1) % len(self.themes)
            # Recreate layout and style with new theme colors
            event.app.layout = self._create_layout()
            event.app.style = self._get_style()
            event.app.invalidate()

        @kb.add("down")
        def _(event):
            """Move selection down."""
            self.selected_index = (self.selected_index + 1) % len(self.themes)
            # Recreate layout and style with new theme colors
            event.app.layout = self._create_layout()
            event.app.style = self._get_style()
            event.app.invalidate()

        @kb.add("enter")
        def _(event):
            """Select current theme."""
            self.result = self.themes[self.selected_index]
            event.app.exit()

        @kb.add("q")
        @kb.add("Q")
        @kb.add("escape")
        def _(event):
            """Cancel selection."""
            self.result = None
            event.app.exit()

        @kb.add("c-c")
        def _(event):
            """Handle Ctrl+C."""
            self.result = None
            event.app.exit()

        app = Application(
            layout=self._create_layout(),
            key_bindings=kb,
            style=self._get_style(),
            full_screen=False,
            mouse_support=False,
        )

        app.run()
        return self.result


def run_interactive_theme_selector() -> bool:
    """Run the interactive theme selector.

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
            console.print(
                f"\n[green]✓ Theme changed to '{theme.name.replace('_', ' ').title()}'[/]"
            )
            console.print(
                "\n[dim]Restart FlutterCraft to see the full theme changes.[/]\n"
            )
            return True

    console.print("\n[yellow]Theme selection cancelled[/]\n")
    return False
