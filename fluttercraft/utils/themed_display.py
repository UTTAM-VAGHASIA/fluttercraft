"""Themed display utilities for FlutterCraft CLI."""

from rich.console import Console
from rich.text import Text

from .themes.service import ThemeDisplayService

console = Console()
_display_service: ThemeDisplayService | None = None


def _get_service() -> ThemeDisplayService:
    global _display_service
    if _display_service is None:
        _display_service = ThemeDisplayService(console=console)
    return _display_service


def create_themed_ascii_art(prefer_block: bool = False) -> Text:
    return _get_service().render_ascii_art(prefer_block=prefer_block)


def display_themed_welcome_header(
    platform_info, flutter_info, fvm_info, show_ascii: bool = True
) -> None:
    _get_service().show_welcome_header(
        platform_info=platform_info,
        flutter_info=flutter_info,
        fvm_info=fvm_info,
        show_ascii=show_ascii,
    )


def display_themed_about() -> None:
    _get_service().show_about()


def display_themed_help() -> None:
    _get_service().show_help()


def clear_screen() -> None:
    _get_service().clear_screen()


def print_success(message: str) -> None:
    _get_service().print_success(message)


def print_error(message: str) -> None:
    _get_service().print_error(message)


def print_warning(message: str) -> None:
    _get_service().print_warning(message)


def print_info(message: str) -> None:
    _get_service().print_info(message)


def get_console() -> Console:
    return _get_service().get_console()


def get_theme():
    return _get_service().get_theme()


def format_text(
    kind: str, text: str, *, bold: bool = False, italic: bool = False
) -> str:
    return _get_service().format_text(kind, text, bold=bold, italic=italic)


def format_style(kind: str, *, bold: bool = False, italic: bool = False) -> str:
    return _get_service().format_style(kind, bold=bold, italic=italic)
