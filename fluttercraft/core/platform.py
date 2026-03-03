from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, field

# ── Data types ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class ToolInfo:
    """Detection result for a single CLI tool."""

    name: str
    available: bool
    version: str = ""  # empty string when not available or version unknown
    path: str = ""     # absolute path from shutil.which; empty if not found


@dataclass(slots=True)
class PlatformInfo:
    """Snapshot of the current platform and Flutter toolchain."""

    system: str          # "Linux" | "Darwin" | "Windows"
    machine: str         # "x86_64" | "arm64" | …
    python_version: str
    shell: str           # $SHELL on Unix, %COMSPEC% on Windows
    tools: dict[str, ToolInfo] = field(default_factory=dict)


# ── Platform helpers ──────────────────────────────────────────────────────────


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_linux() -> bool:
    return platform.system() == "Linux"


def get_os() -> str:
    """Return the OS name: ``'Linux'``, ``'Darwin'``, or ``'Windows'``."""
    return platform.system()


# ── Toolchain detection ───────────────────────────────────────────────────────

_VERSION_RE = re.compile(r"\d+\.\d+[\.\d]*")

# (tool_name, version_command)
_TOOLCHAIN_SPECS: list[tuple[str, list[str]]] = [
    ("flutter", ["flutter", "--version"]),
    ("dart", ["dart", "--version"]),
    ("fvm", ["fvm", "--version"]),
    ("git", ["git", "--version"]),
]


def _run_version_cmd(cmd: list[str]) -> str:
    """Run *cmd* and return combined stdout+stderr, or ``''`` on any failure."""
    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or result.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def _extract_version(text: str) -> str:
    """Extract the first ``X.Y[.Z]`` version string from *text*.

    Falls back to the first 40 characters of the first line if no version
    number is found.
    """
    match = _VERSION_RE.search(text)
    if match:
        return match.group(0)
    first_line = text.split("\n")[0]
    return first_line[:40]


def detect_tool(name: str, cmd: list[str]) -> ToolInfo:
    """Detect whether *name* is on PATH and retrieve its version.

    Uses :func:`shutil.which` to avoid spawning a subprocess unnecessarily.
    If the tool is found but the version command fails, ``available`` is still
    ``True`` and ``version`` is an empty string.
    """
    path = shutil.which(name)
    if not path:
        return ToolInfo(name=name, available=False)

    raw = _run_version_cmd(cmd)
    version = _extract_version(raw) if raw else ""
    return ToolInfo(name=name, available=True, version=version, path=path)


def detect_toolchain() -> dict[str, ToolInfo]:
    """Detect all Flutter development tools on PATH.

    Returns a dict keyed by tool name: ``flutter``, ``dart``, ``fvm``,
    ``git``.
    """
    return {name: detect_tool(name, cmd) for name, cmd in _TOOLCHAIN_SPECS}


# ── Full platform snapshot ────────────────────────────────────────────────────


def get_platform_info() -> PlatformInfo:
    """Return a :class:`PlatformInfo` snapshot of the current environment.

    Runs toolchain detection synchronously. Suitable for app startup; for
    background refresh use a Textual ``Worker``.
    """
    system = platform.system()
    shell = os.environ.get("COMSPEC", "") if system == "Windows" else os.environ.get("SHELL", "")

    return PlatformInfo(
        system=system,
        machine=platform.machine(),
        python_version=platform.python_version(),
        shell=shell,
        tools=detect_toolchain(),
    )
