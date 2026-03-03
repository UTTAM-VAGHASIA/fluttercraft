from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class FvmVersion:
    """A single cached Flutter SDK version reported by ``fvm list``."""

    name: str
    is_active: bool = False
    channel: str = ""


# ── FVM availability ──────────────────────────────────────────────────────────


def is_fvm_installed() -> bool:
    """Return True if the ``fvm`` binary is on PATH."""
    return shutil.which("fvm") is not None


# ── Internal runner ───────────────────────────────────────────────────────────


def _run_fvm(
    args: list[str],
    cwd: str | None = None,
    timeout: int = 30,
) -> tuple[bool, str]:
    """Run ``fvm <args>`` and return ``(success, combined_output)``.

    Never raises — errors become ``(False, error_message)``.
    Always sets ``stdin=subprocess.DEVNULL`` to prevent stealing
    keyboard input from the TUI.
    """
    try:
        result = subprocess.run(
            ["fvm"] + args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except (FileNotFoundError, OSError) as exc:
        return False, str(exc)


# ── Version list ──────────────────────────────────────────────────────────────

# Matches version strings like 3.29.3 or 3.29.3-hotfix.2
_VERSION_RE = re.compile(r"\d+\.\d+[\.\d]*(?:-[\w\.]+)?")


def list_installed() -> list[FvmVersion]:
    """Return all locally cached Flutter SDK versions via ``fvm list``.

    Parses both table-style (newer FVM) and plain-line (older FVM) output.
    """
    ok, output = _run_fvm(["list"])
    if not output:
        return []

    # Try to determine active version from a trailing "Active: x.y.z" line
    active_name: str | None = None
    for line in output.splitlines():
        m = re.search(r"active[:\s]+(\S+)", line, re.IGNORECASE)
        if m:
            active_name = m.group(1).strip("()")
            break

    versions: list[FvmVersion] = []
    seen: set[str] = set()

    for line in output.splitlines():
        # Skip table borders/headers
        if re.match(r"^[┌├└─╔╠╚═]", line):
            continue
        if "Version" in line and ("Channel" in line or "SDK" in line):
            continue

        is_active_line = (
            "global" in line.lower()
            or "active" in line.lower()
            or "✓" in line
            or "●" in line
        )

        m = _VERSION_RE.search(line)
        if m:
            name = m.group(0)
            if name not in seen:
                seen.add(name)
                effective_active = is_active_line or name == active_name
                versions.append(FvmVersion(name=name, is_active=effective_active))

    return versions


def get_active_version(project_root: str | None = None) -> str | None:
    """Return the currently active FVM version for the given directory or globally."""
    ok, output = _run_fvm(["current"], cwd=project_root)
    if ok and output:
        m = _VERSION_RE.search(output)
        if m:
            return m.group(0)
    return None


# ── Releases browser ──────────────────────────────────────────────────────────


def list_releases(channel: str = "stable") -> list[str]:
    """Fetch available Flutter SDK releases for *channel* via ``fvm releases``.

    Tries ``--channel <channel>`` first; falls back to plain ``releases``
    for older FVM versions.  Returns version strings in the order FVM emits.
    """
    ok, output = _run_fvm(
        ["releases", "--channel", channel], timeout=60
    )
    if not ok or not output:
        ok, output = _run_fvm(["releases"], timeout=60)
    if not output:
        return []

    versions: list[str] = []
    seen: set[str] = set()
    for line in output.splitlines():
        line = line.strip()
        # Skip table borders, headers, and blank lines
        if not line or re.match(r"^[┌├└─╔╠╚═│┐┤┘╗╣╝]", line):
            continue
        m = _VERSION_RE.search(line)
        if m:
            v = m.group(0)
            if v not in seen:
                seen.add(v)
                versions.append(v)
    return versions


# ── Version install ───────────────────────────────────────────────────────────


def install_version(
    version: str,
    on_line: Callable[[str], None] | None = None,
) -> bool:
    """Install Flutter SDK *version* via ``fvm install``.

    Streams each output line to *on_line* (if provided).
    Returns True on success.
    """
    try:
        proc = subprocess.Popen(
            ["fvm", "install", version],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if proc.stdout:
            for raw_line in proc.stdout:
                stripped = raw_line.rstrip()
                if on_line:
                    on_line(stripped)
        proc.wait()
        return proc.returncode == 0
    except (FileNotFoundError, OSError) as exc:
        if on_line:
            on_line(f"Error: {exc}")
        return False


# ── Version switching ─────────────────────────────────────────────────────────


def use_version(
    version: str,
    project_root: str | None = None,
    global_flag: bool = True,
) -> tuple[bool, str]:
    """Set *version* as the active Flutter SDK.

    Pass *global_flag=True* for system-wide ``--global`` activation.
    Pass *project_root* for project-scoped ``.fvmrc`` activation.
    """
    args = ["use", version]
    if global_flag:
        args.append("--global")
    return _run_fvm(args, cwd=project_root)


# ── Version removal ───────────────────────────────────────────────────────────


def remove_version(version: str) -> tuple[bool, str]:
    """Remove a cached Flutter SDK version via ``fvm remove``."""
    ok, output = _run_fvm(["remove", version, "--force"])
    if not ok:
        # Retry without --force for older FVM
        ok, output = _run_fvm(["remove", version])
    return ok, output


# ── FVM doctor ────────────────────────────────────────────────────────────────


def run_doctor(project_root: str | None = None) -> str:
    """Run ``fvm doctor`` and return combined output."""
    _, output = _run_fvm(["doctor"], cwd=project_root)
    return output


# ── FVM config ────────────────────────────────────────────────────────────────


def get_fvmrc(project_root: str) -> dict | None:
    """Read ``.fvmrc`` from *project_root*.

    Returns the parsed dict on success, or ``None`` if absent or invalid.
    """
    path = os.path.join(project_root, ".fvmrc")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return None


# ── FVM self-install / self-uninstall ─────────────────────────────────────────


def install_fvm() -> tuple[bool, str]:
    """Install FVM itself via ``dart pub global activate fvm``.

    Returns ``(success, output)``.
    """
    try:
        result = subprocess.run(
            ["dart", "pub", "global", "activate", "fvm"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except (FileNotFoundError, OSError):
        return False, "dart not found — install Flutter SDK first"


def uninstall_fvm() -> tuple[bool, str]:
    """Uninstall FVM via ``dart pub global deactivate fvm``."""
    try:
        result = subprocess.run(
            ["dart", "pub", "global", "deactivate", "fvm"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except (FileNotFoundError, OSError):
        return False, "dart not found"
