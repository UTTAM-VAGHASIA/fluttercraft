"""
Settings UI for FlutterCraft.
Renders an interactive settings panel using Rich.
"""
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm

from fluttercraft.infrastructure.storage.config_manager import get_config_manager
from fluttercraft.utils.themed_display import get_theme, clear_screen

class SettingsUI:
    """Handles the interactive settings interface."""
    
    def __init__(self, console: Console):
        self.console = console
        self.config = get_config_manager()
        self.theme = get_theme()

    def show(self) -> None:
        """Display the settings menu loop."""
        while True:
            clear_screen()
            self._render_menu()
            
            choice = Prompt.ask(
                "\n[bold cyan]Select a category[/] (or 'q' to quit)", 
                choices=["1", "2", "3", "4", "q"], 
                default="q"
            )
            
            if choice == "q":
                break
            elif choice == "1":
                self._edit_general()
            elif choice == "2":
                self._edit_appearance()
            elif choice == "3":
                self._edit_completion()
            elif choice == "4":
                self._edit_ui()

    def _render_menu(self) -> None:
        """Render the main settings menu."""
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        
        # Header
        self.console.print(Panel(
            "[bold white]FlutterCraft Settings[/]", 
            style=f"{self.theme.accent_cyan}",
            subtitle="[dim]v0.1.3[/]"
        ))
        
        # Categories
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan")
        table.add_column("Category")
        table.add_column("Description", style="dim")
        
        table.add_row("1", "General", "History, System")
        table.add_row("2", "Appearance", "Themes, Animations")
        table.add_row("3", "Completion", "Fuzzy matching, Auto-show")
        table.add_row("4", "UI", "Tips, Timing, Compact mode")
        
        self.console.print(table)

    def _edit_general(self) -> None:
        """Edit general settings."""
        while True:
            clear_screen()
            self.console.print("[bold cyan]General Settings[/]\n")
            
            max_entries = self.config.get("history.max_entries")
            save_dupes = self.config.get("history.save_duplicates")
            
            self.console.print(f"1. History Max Entries: [green]{max_entries}[/]")
            self.console.print(f"2. Save Duplicates: [green]{save_dupes}[/]")
            self.console.print("\n[dim]b. Back[/]")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "b"], default="b")
            
            if choice == "b":
                break
            elif choice == "1":
                val = Prompt.ask("Enter max entries", default=str(max_entries))
                if val.isdigit():
                    self.config.set("history.max_entries", int(val))
            elif choice == "2":
                val = Confirm.ask("Save duplicate commands?", default=save_dupes)
                self.config.set("history.save_duplicates", val)

    def _edit_appearance(self) -> None:
        """Edit appearance settings."""
        while True:
            clear_screen()
            self.console.print("[bold cyan]Appearance Settings[/]\n")
            
            animations = self.config.get("animations.enabled")
            reduced_motion = self.config.get("animations.reduced_motion")
            
            self.console.print(f"1. Enable Animations: [green]{animations}[/]")
            self.console.print(f"2. Reduced Motion: [green]{reduced_motion}[/]")
            self.console.print("\n[dim]b. Back[/]")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "b"], default="b")
            
            if choice == "b":
                break
            elif choice == "1":
                val = Confirm.ask("Enable animations?", default=animations)
                self.config.set("animations.enabled", val)
            elif choice == "2":
                val = Confirm.ask("Reduce motion?", default=reduced_motion)
                self.config.set("animations.reduced_motion", val)

    def _edit_completion(self) -> None:
        """Edit completion settings."""
        while True:
            clear_screen()
            self.console.print("[bold cyan]Completion Settings[/]\n")
            
            fuzzy = self.config.get("completion.fuzzy_enabled")
            auto_show = self.config.get("completion.auto_show_slash")
            
            self.console.print(f"1. Fuzzy Matching: [green]{fuzzy}[/]")
            self.console.print(f"2. Auto-show Slash Commands: [green]{auto_show}[/]")
            self.console.print("\n[dim]b. Back[/]")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "b"], default="b")
            
            if choice == "b":
                break
            elif choice == "1":
                val = Confirm.ask("Enable fuzzy matching?", default=fuzzy)
                self.config.set("completion.fuzzy_enabled", val)
            elif choice == "2":
                val = Confirm.ask("Auto-show menu for '/'?", default=auto_show)
                self.config.set("completion.auto_show_slash", val)

    def _edit_ui(self) -> None:
        """Edit UI settings."""
        while True:
            clear_screen()
            self.console.print("[bold cyan]UI Settings[/]\n")
            
            tips = self.config.get("ui.show_tips")
            timing = self.config.get("ui.show_timing")
            compact = self.config.get("ui.compact_mode")
            
            self.console.print(f"1. Show Tips: [green]{tips}[/]")
            self.console.print(f"2. Show Execution Time: [green]{timing}[/]")
            self.console.print(f"3. Compact Mode: [green]{compact}[/]")
            self.console.print("\n[dim]b. Back[/]")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "b"], default="b")
            
            if choice == "b":
                break
            elif choice == "1":
                val = Confirm.ask("Show startup tips?", default=tips)
                self.config.set("ui.show_tips", val)
            elif choice == "2":
                val = Confirm.ask("Show command timing?", default=timing)
                self.config.set("ui.show_timing", val)
            elif choice == "3":
                val = Confirm.ask("Enable compact mode?", default=compact)
                self.config.set("ui.compact_mode", val)
