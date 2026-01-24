"""Full-screen themed layout manager for FlutterCraft."""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

class FlutterCraftScreen:
    """Manages full-screen themed layout."""
    
    def __init__(self, theme):
        self.theme = theme
        self.layout = Layout()
        self._setup_layout()
        
        # Initial empty state
        self.update_header(Text(""), Text(""))
        self.update_output(Text("Welcome to FlutterCraft! Type /help for commands.", style="dim"))
        self.update_input(Text("> ", style="bold cyan"), Text("Ready", style="dim"))
    
    def _setup_layout(self):
        # Split into Header, Main Output, and Input/Status
        self.layout.split_column(
            Layout(name="header", size=14),  # Adjust size for ASCII art + info
            Layout(name="output", ratio=1),
            Layout(name="input", size=3),
        )
    
    def update_header(self, ascii_art, info_text):
        """Update the header section with logo and system info."""
        # Combine ASCII art and info text
        # If they are Text objects, we can join them or put them in a table/columns
        # For now, let's stack them
        from rich.console import Group
        
        content = Group(
            Align.center(ascii_art),
            Align.center(info_text)
        )
        
        self.layout["header"].update(
            Panel(
                content, 
                border_style=self.theme.accent_cyan,
                title="FlutterCraft CLI",
                title_align="center",
                padding=(0, 1)
            )
        )
    
    def update_output(self, content):
        """Update the main output area."""
        # Content should be a Renderable
        self.layout["output"].update(
            Panel(
                content, 
                border_style=self.theme.accent_cyan, 
                title="Output",
                padding=(1, 2)
            )
        )
    
    def update_input(self, prompt_text, toolbar_text=""):
        """Update the input/status area."""
        # Use columns for prompt and toolbar?
        # Or just a simple panel
        from rich.table import Table
        
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row(prompt_text, toolbar_text)
        
        self.layout["input"].update(
            Panel(
                grid, 
                border_style=self.theme.accent_cyan,
                height=3
            )
        )
