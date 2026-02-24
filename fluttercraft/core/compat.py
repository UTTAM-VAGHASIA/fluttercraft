from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


# ── Config directory ──────────────────────────────────────────────────────────


def get_config_dir() -> Path:
    """Return the platform-appropriate directory for FlutterCraft data files.

    - **Linux / macOS:** ``~/.fluttercraft/``
    - **Windows:** ``%APPDATA%\\FlutterCraft\\``  (falls back to
      ``~/AppData/Roaming/FlutterCraft/`` when ``APPDATA`` is unset)
    """
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "FlutterCraft"
        return Path.home() / "AppData" / "Roaming" / "FlutterCraft"
    return Path.home() / ".fluttercraft"


# ── Terminal capability detection ─────────────────────────────────────────────


def supports_unicode() -> bool:
    """Return ``True`` when the terminal is likely capable of rendering Unicode.

    Checks (in order):

    1. ``sys.stdout.encoding`` — UTF-8 means Unicode is available.
    2. ``LANG`` / ``LC_ALL`` environment variables (Unix).
    3. ``WT_SESSION`` environment variable — Windows Terminal always supports
       Unicode.
    4. ``TERM`` / ``TERM_PROGRAM`` for known-good terminals.
    """
    encoding: str = getattr(sys.stdout, "encoding", "") or ""
    if encoding.lower().replace("-", "") in ("utf8", "utf-8"):
        return True

    for env_var in ("LANG", "LC_ALL", "LC_CTYPE"):
        value = os.environ.get(env_var, "")
        if "utf" in value.lower():
            return True

    if sys.platform == "win32":
        # Windows Terminal sets WT_SESSION
        if os.environ.get("WT_SESSION"):
            return True
        # ConEmu / cmder
        if os.environ.get("ConEmuANSI"):
            return True

    term_program = os.environ.get("TERM_PROGRAM", "")
    if term_program in ("iTerm.app", "vscode", "WezTerm", "Hyper"):
        return True

    return False


def supports_truecolor() -> bool:
    """Return ``True`` when the terminal advertises 24-bit true-color support.

    Checks the ``COLORTERM`` environment variable for ``truecolor`` or
    ``24bit``, and common ``TERM`` values.
    """
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return True
    term = os.environ.get("TERM", "")
    return term in ("xterm-direct", "xterm-256color")


def supports_mouse() -> bool:
    """Return ``True`` when the terminal is expected to support mouse events.

    Textual enables mouse support automatically, but some headless / dumb
    terminals reject the escape sequences.
    """
    term = os.environ.get("TERM", "")
    if term in ("dumb", ""):
        return False
    if os.environ.get("TERM_PROGRAM") == "Apple_Terminal":
        # Apple's built-in Terminal has limited mouse support
        return False
    return True


# ── Glyph sets ────────────────────────────────────────────────────────────────

#: Full Unicode glyphs used in the TUI.
GLYPHS_UNICODE: dict[str, str] = {
    "bullet":    "◈",
    "selected":  "◀",
    "bolt":      "⚡",
    "success":   "▶",
    "error":     "✖",
    "warning":   "⚠",
    "info":      "·",
    "handle":    "┃",
    "separator": "──",
    "check":     "✓",
    "cross":     "✗",
    "ellipsis":  "…",
}

#: Plain ASCII fallbacks for terminals that cannot render Unicode.
GLYPHS_ASCII: dict[str, str] = {
    "bullet":    "*",
    "selected":  "<",
    "bolt":      "!",
    "success":   ">",
    "error":     "x",
    "warning":   "!",
    "info":      ".",
    "handle":    "|",
    "separator": "--",
    "check":     "Y",
    "cross":     "N",
    "ellipsis":  "...",
}


def get_glyph(name: str, *, force_ascii: bool = False) -> str:
    """Return the glyph string for *name*.

    Uses the Unicode set when :func:`supports_unicode` returns ``True``
    (or *force_ascii* is ``False``), otherwise falls back to ASCII.
    Returns *name* unchanged if it is not a known glyph key.
    """
    use_ascii = force_ascii or not supports_unicode()
    glyphs = GLYPHS_ASCII if use_ascii else GLYPHS_UNICODE
    return glyphs.get(name, name)


# ── Dependency check ──────────────────────────────────────────────────────────

#: Required CLI tools checked at startup.
REQUIRED_TOOLS: list[str] = ["git"]

#: Optional but highly recommended tools.
RECOMMENDED_TOOLS: list[str] = ["flutter", "fvm"]


def check_dependencies(
    required: list[str] | None = None,
) -> dict[str, bool]:
    """Check whether CLI tools are available on PATH.

    Returns a dict ``{tool_name: is_available}``.  Pass *required* to
    override :data:`REQUIRED_TOOLS`; defaults to checking both required and
    recommended tools.
    """
    tools = required if required is not None else REQUIRED_TOOLS + RECOMMENDED_TOOLS
    return {tool: shutil.which(tool) is not None for tool in tools}


def missing_required() -> list[str]:
    """Return the names of required tools that are NOT on PATH."""
    return [
        tool
        for tool, found in check_dependencies(REQUIRED_TOOLS).items()
        if not found
    ]


# ── Terminal geometry ─────────────────────────────────────────────────────────


def get_terminal_size(fallback: tuple[int, int] = (80, 24)) -> tuple[int, int]:
    """Return ``(columns, rows)`` of the terminal.

    Uses :func:`shutil.get_terminal_size` which works cross-platform (reads
    ``$COLUMNS`` / ``$LINES`` on Unix, ``GetConsoleScreenBufferInfo`` on
    Windows).  Falls back to *fallback* when the size cannot be determined.
    """
    size = shutil.get_terminal_size(fallback=fallback)
    return (size.columns, size.lines)


# ── Newline normalisation ─────────────────────────────────────────────────────


def normalise_newlines(text: str) -> str:
    """Convert ``\\r\\n`` and bare ``\\r`` to ``\\n``.

    Useful when consuming subprocess output on Windows where ``\\r\\n`` is the
    default line ending.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")
