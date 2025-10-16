from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.text import Text

from .ascii_art import select_ascii_art
from .gradient import apply_gradient_to_ascii
from .theme import Theme
from .theme_manager import ThemeManager, get_theme_manager

FLUTTERCRAFT_ASCII_GRADIENT = [
    "#F97316",  # vibrant sunset orange
    "#F43F5E",  # rosy magenta
    "#7C3AED",  # deep electric violet
]


@dataclass(slots=True)
class ThemeDisplayService:
    """Centralized service for rendering themed FlutterCraft output."""

    console: Console
    theme_manager: Optional[ThemeManager] = None

    def __post_init__(self) -> None:
        if self.theme_manager is None:
            self.theme_manager = get_theme_manager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_ascii_art(self, prefer_block: bool = False) -> Text:
        ascii_art = select_ascii_art(self._get_terminal_width(), prefer_block)
        theme = self.theme_manager.get_current_theme()

        if FLUTTERCRAFT_ASCII_GRADIENT:
            return apply_gradient_to_ascii(ascii_art, FLUTTERCRAFT_ASCII_GRADIENT)

        if theme.gradient_colors:
            return apply_gradient_to_ascii(ascii_art, theme.gradient_colors)

        return Text(ascii_art, style=f"bold {theme.accent_cyan}")

    def show_welcome_header(
        self,
        platform_info: dict,
        flutter_info: dict,
        fvm_info: dict,
        show_ascii: bool = True,
    ) -> None:
        theme = self.theme_manager.get_current_theme()

        if show_ascii:
            self.clear_screen()
            ascii_art = self.render_ascii_art()
            self.console.print(ascii_art)
            self.console.print()

        # Tips section
        self.console.print(
            f"[bold {theme.semantic.text_accent}]Tips for getting started:[/]"
        )
        self.console.print(
            f"[{theme.semantic.text_secondary}]1. Use slash commands like /help, /clear, /quit[/]"
        )
        self.console.print(
            f"[{theme.semantic.text_secondary}]2. Manage Flutter versions with FVM commands[/]"
        )
        self.console.print(
            f"[{theme.semantic.text_secondary}]3. Run 'flutter upgrade' to update Flutter[/]"
        )
        self.console.print(
            f"[{theme.semantic.text_secondary}]4. Type / to see available commands[/]\n"
        )

        platform_name = platform_info.get("system", "Unknown")
        python_version = platform_info.get("python_version", "Unknown")
        fvm_version = fvm_info.get("version") or "Not installed"

        flutter_version = flutter_info.get("current_version")
        if flutter_version:
            if flutter_info.get("update_available"):
                latest = flutter_info.get("latest_version", "unknown")
                flutter_display = (
                    f"{flutter_version} [{theme.semantic.status_warning}]"
                    "(→ {latest} available)[/]"
                )
            else:
                flutter_display = (
                    f"{flutter_version} [{theme.semantic.status_success}]✓[/]"
                )
        else:
            flutter_display = "None"

        self.console.print(
            f"[{theme.semantic.text_secondary}]Platform: {platform_name} | "
            f"Python: {python_version} | "
            f"Flutter: {flutter_display} | "
            f"FVM: {fvm_version}[/]\n"
        )

    def show_about(self) -> None:
        import sys
        from importlib.metadata import PackageNotFoundError, version as get_version

        theme = self.theme_manager.get_current_theme()

        border_color = theme.semantic.text_accent
        title_color = theme.semantic.text_primary

        self.console.print(
            f"\n[bold {border_color}]╔════════════════════════════════════════════════════════════════╗[/]"
        )
        self.console.print(
            f"[bold {border_color}]║[/]                        [bold {title_color}]FlutterCraft CLI[/]                        [bold {border_color}]║[/]"
        )
        self.console.print(
            f"[bold {border_color}]╚════════════════════════════════════════════════════════════════╝[/]\n"
        )

        self.console.print(f"[bold {theme.semantic.status_warning}]Description:[/]")
        self.console.print(
            "  A powerful command-line interface for managing Flutter and FVM"
        )
        self.console.print(
            "  (Flutter Version Manager) with an intuitive and beautiful interface.\n"
        )

        self.console.print(
            f"[bold {theme.semantic.status_warning}]Version Information:[/]"
        )

        try:
            version = get_version("fluttercraft")
        except PackageNotFoundError:
            version = "0.1.3-dev"

        self.console.print(f"  [{theme.semantic.text_link}]FlutterCraft:[/] {version}")
        self.console.print(
            f"  [{theme.semantic.text_link}]Python:[/] {sys.version.split()[0]}"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]Platform:[/] {platform.system()} {platform.release()}"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]Theme:[/] {theme.name.title()}\n"
        )

        success_icon = f"[{theme.semantic.status_success}]✓[/]"
        self.console.print(f"[bold {theme.semantic.status_warning}]Features:[/]")
        self.console.print(
            f"  {success_icon} Flutter Version Manager (FVM) integration"
        )
        self.console.print(f"  {success_icon} Install and manage FVM")
        self.console.print(f"  {success_icon} List available Flutter SDK versions")
        self.console.print(f"  {success_icon} Flutter upgrade with progress tracking")
        self.console.print(f"  {success_icon} Real-time command output with theming")
        self.console.print(
            f"  {success_icon} Beautiful command-line interface with theming"
        )
        self.console.print(f"  {success_icon} Auto-completion and command history\n")

        self.console.print(
            f"[bold {theme.semantic.status_warning}]Working Commands:[/]"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]Slash Commands:[/] /quit, /clear, /help, /about"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]FVM Commands:[/] fvm install, fvm uninstall, fvm releases, fvm list"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]Flutter Commands:[/] flutter upgrade (with --force, --verify-only)"
        )
        self.console.print(
            f"  [{theme.semantic.text_link}]Theme Commands:[/] fluttercraft theme <name>\n"
        )

        self.console.print(f"[bold {theme.semantic.status_warning}]Author:[/]")
        self.console.print(
            "  Created with 💝 by UTTAM VAGHASIA for Flutter developers\n"
        )

        self.console.print(f"[bold {theme.semantic.status_warning}]Repository:[/]")
        self.console.print(
            f"  [{theme.semantic.text_link}]https://github.com/UTTAM-VAGHASIA/fluttercraft[/]"
        )
        self.console.print(
            f"  [{theme.semantic.text_secondary}]⭐ Star the repo if you find it useful![/]\n"
        )

        self.console.print(f"[bold {theme.semantic.status_warning}]Quick Start:[/]")
        self.console.print(
            f"  1. Type [{theme.semantic.text_link}]/help[/] to see all available commands"
        )
        self.console.print(
            f"  2. Use [{theme.semantic.text_link}]fvm install[/] to install Flutter Version Manager"
        )
        self.console.print(
            f"  3. Run [{theme.semantic.text_link}]fvm releases[/] to see available Flutter versions"
        )
        self.console.print(
            f"  4. Use [{theme.semantic.text_link}]flutter upgrade[/] to update Flutter"
        )
        self.console.print(
            f"  5. Change theme with [{theme.semantic.text_link}]fluttercraft theme <name>[/]\n"
        )

        self.console.print(
            f"[{theme.semantic.text_secondary}]Type '/help' for detailed command information[/]\n"
        )

    def show_help(self) -> None:
        from fluttercraft.utils.beautiful_prompt import (
            FVM_COMMANDS,
            FLUTTER_COMMANDS,
            SLASH_COMMANDS,
        )

        theme = self.theme_manager.get_current_theme()

        self.console.print(
            f"\n[bold {theme.semantic.text_accent}]Available Commands:[/]\n"
        )

        self.console.print(f"[bold {theme.semantic.status_warning}]Slash Commands:[/]")
        for cmd, desc in SLASH_COMMANDS.items():
            cmd_padded = f"{cmd:<25}"
            self.console.print(
                f" [{theme.semantic.text_link}]{cmd_padded}[/] [{theme.semantic.text_secondary}]{desc}[/]"
            )

        self.console.print()

        self.console.print(
            f"[bold {theme.semantic.status_warning}]FVM Commands:[/] [{theme.semantic.status_success}]✓ Working[/]"
        )
        for cmd, desc in FVM_COMMANDS.items():
            cmd_padded = f"{cmd:<25}"
            self.console.print(
                f" [{theme.semantic.text_link}]{cmd_padded}[/] [{theme.semantic.text_secondary}]{desc}[/]"
            )

        self.console.print()

        self.console.print(
            f"[bold {theme.semantic.status_warning}]Flutter Commands:[/] [{theme.semantic.status_warning}]⚠ Partial Support[/]"
        )
        for cmd, desc in FLUTTER_COMMANDS.items():
            cmd_padded = f"{cmd:<25}"
            status = (
                f" [{theme.semantic.status_success}]✓[/]"
                if cmd.startswith("flutter upgrade")
                else ""
            )
            self.console.print(
                f" [{theme.semantic.text_link}]{cmd_padded}[/] [{theme.semantic.text_secondary}]{desc}[/]{status}"
            )

        self.console.print()
        self.console.print(
            f"[{theme.semantic.text_secondary}]Tip: Type / to see slash commands | Use arrow keys for history[/]\n"
        )

    def print_success(self, message: str) -> None:
        theme = self.theme_manager.get_current_theme()
        self.console.print(f"[{theme.semantic.status_success}]✓ {message}[/]")

    def print_error(self, message: str) -> None:
        theme = self.theme_manager.get_current_theme()
        self.console.print(f"[{theme.semantic.status_error}]✗ {message}[/]")

    def print_warning(self, message: str) -> None:
        theme = self.theme_manager.get_current_theme()
        self.console.print(f"[{theme.semantic.status_warning}]⚠ {message}[/]")

    def print_info(self, message: str) -> None:
        theme = self.theme_manager.get_current_theme()
        self.console.print(f"[{theme.semantic.status_info}]ℹ {message}[/]")

    def clear_screen(self) -> None:
        os.system("cls" if platform.system().lower() == "windows" else "clear")

    def get_console(self) -> Console:
        return self.console

    def get_theme(self) -> Theme:
        return self.theme_manager.get_current_theme()

    def format_text(
        self, kind: str, text: str, *, bold: bool = False, italic: bool = False
    ) -> str:
        theme = self.get_theme()
        color = theme.get_rich_style(kind)

        styles: list[str] = []
        if bold:
            styles.append("bold")
        if italic:
            styles.append("italic")
        if color:
            styles.append(color)

        if not styles:
            return text

        style_definition = " ".join(styles)
        return f"[{style_definition}]{text}[/]"

    def format_style(
        self, kind: str, *, bold: bool = False, italic: bool = False
    ) -> str:
        theme = self.get_theme()
        color = theme.get_rich_style(kind)

        styles: list[str] = []
        if bold:
            styles.append("bold")
        if italic:
            styles.append("italic")
        if color:
            styles.append(color)

        return " ".join(styles)

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _get_terminal_width() -> int:
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80


__all__ = ["ThemeDisplayService", "FLUTTERCRAFT_ASCII_GRADIENT"]
