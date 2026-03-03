from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


# ── ANSI strip ────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[mGKHF]|\x1b\].*?\x07")


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from *text*."""
    return _ANSI_RE.sub("", text)


def esc(text: str) -> str:
    """Escape Rich markup brackets in raw subprocess output."""
    return _strip_ansi(text).replace("[", "\\[")


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class FlutterDevice:
    """A connected device reported by ``flutter devices``."""

    id: str
    name: str
    platform: str
    is_emulator: bool = False


# ── Flutter availability ──────────────────────────────────────────────────────


def is_flutter_installed() -> bool:
    """Return True if the ``flutter`` binary is on PATH."""
    return shutil.which("flutter") is not None


def get_flutter_version() -> str | None:
    """Return the active Flutter version string, or None."""
    try:
        result = subprocess.run(
            ["flutter", "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=15,
        )
        for line in result.stdout.splitlines():
            m = re.search(r"Flutter\s+(\d+\.\d+[\.\d]*)", line)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


# ── Internal runner ───────────────────────────────────────────────────────────


def _run_flutter(
    args: list[str],
    cwd: str | None = None,
    timeout: int = 30,
) -> tuple[bool, str]:
    """Run ``flutter <args>`` and return ``(success, combined_output)``."""
    try:
        result = subprocess.run(
            ["flutter"] + args,
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


# ── Streaming runner ──────────────────────────────────────────────────────────


def run_flutter_streaming(
    args: list[str],
    cwd: str | None = None,
    on_line: Callable[[str], None] | None = None,
) -> bool:
    """Run ``flutter <args>`` streaming each output line to *on_line*.

    Returns True on success (exit code 0). Never raises.
    """
    try:
        proc = subprocess.Popen(
            ["flutter"] + args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
        )
        if proc.stdout:
            for raw_line in proc.stdout:
                if on_line:
                    on_line(raw_line.rstrip())
        proc.wait()
        return proc.returncode == 0
    except (FileNotFoundError, OSError) as exc:
        if on_line:
            on_line(f"Error: {exc}")
        return False


# ── Flutter run (interactive, stdin=PIPE) ─────────────────────────────────────


def start_flutter_run(
    extra_args: list[str] | None = None,
    cwd: str | None = None,
) -> subprocess.Popen | None:
    """Start ``flutter run`` and return the live Popen process.

    The process has ``stdin=PIPE`` so the caller can send interactive
    keys (``r`` hot-reload, ``R`` restart, ``q`` quit).
    Returns None if flutter is not found.
    """
    try:
        return subprocess.Popen(
            ["flutter", "run"] + (extra_args or []),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
        )
    except (FileNotFoundError, OSError):
        return None


# ── Device list ───────────────────────────────────────────────────────────────

# flutter devices line format: "name • id • platform • sdk"
_DEVICE_LINE = re.compile(r"^(.+?)\s+•\s+(.+?)\s+•\s+(.+?)\s+•\s+.+$")


def get_devices(cwd: str | None = None) -> list[FlutterDevice]:
    """Return connected Flutter devices via ``flutter devices``."""
    ok, output = _run_flutter(["devices"], cwd=cwd, timeout=20)
    if not output:
        return []
    devices: list[FlutterDevice] = []
    for line in output.splitlines():
        stripped = line.strip()
        m = _DEVICE_LINE.match(stripped)
        if m:
            name = m.group(1).strip()
            dev_id = m.group(2).strip()
            platform = m.group(3).strip()
            is_emu = (
                "emulator" in platform.lower()
                or "simulator" in platform.lower()
                or "emulator" in dev_id.lower()
                or "simulator" in dev_id.lower()
            )
            devices.append(
                FlutterDevice(id=dev_id, name=name, platform=platform, is_emulator=is_emu)
            )
    return devices


# ── Output colorisers ─────────────────────────────────────────────────────────


def colorize_doctor_line(line: str) -> str:
    """Return Rich markup for a ``flutter doctor`` output line."""
    s = line.strip()
    e = esc(line)
    if "✓" in s or "[✓]" in s:
        return f"[#9ece6a]{e}[/]"
    if "✗" in s or "[✗]" in s:
        return f"[#f7768e]{e}[/]"
    if "!" in s or "[!]" in s or "⚠" in s:
        return f"[#e0af68]{e}[/]"
    if s.startswith("Doctor") or s.startswith("Flutter") or s.startswith("Running"):
        return f"[bold #7aa2f7]{e}[/]"
    if s.startswith("•") or s.startswith(" "):
        return f"[dim #565f89]{e}[/]"
    return f"[#a9b1d6]{e}[/]"


def colorize_analyze_line(line: str) -> str:
    """Return Rich markup for a ``flutter analyze`` output line."""
    s = line.strip()
    e = esc(line)
    if "error" in s[:10] or "error •" in s:
        return f"[#f7768e]{e}[/]"
    if "warning" in s[:10] or "warning •" in s:
        return f"[#e0af68]{e}[/]"
    if "info" in s[:10] or "info •" in s:
        return f"[dim #a9b1d6]{e}[/]"
    if "No issues found" in s:
        return f"[bold #9ece6a]{e}[/]"
    if "Analyzing" in s or "done" in s.lower():
        return f"[dim #565f89]{e}[/]"
    return f"[#a9b1d6]{e}[/]"


def colorize_test_line(line: str) -> str:
    """Return Rich markup for a ``flutter test`` output line."""
    s = line.strip()
    e = esc(line)
    if "All tests passed" in s:
        return f"[bold #9ece6a]{e}[/]"
    if "Some tests failed" in s or "test failed" in s.lower():
        return f"[bold #f7768e]{e}[/]"
    # Progress lines: "00:01 +3: description"
    if re.match(r"^\d+:\d+\s+\+\d+", s):
        return f"[#f7768e]{e}[/]" if " -" in s else f"[#9ece6a]{e}[/]"
    if "FAILED" in s:
        return f"[#f7768e]{e}[/]"
    if "PASSED" in s or "SKIP" in s:
        return f"[#9ece6a]{e}[/]"
    return f"[#a9b1d6]{e}[/]"
