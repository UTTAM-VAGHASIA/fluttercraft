from __future__ import annotations

import platform
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.core.platform import (
    PlatformInfo,
    ToolInfo,
    _extract_version,
    _run_version_cmd,
    detect_tool,
    detect_toolchain,
    get_os,
    get_platform_info,
    is_linux,
    is_macos,
    is_windows,
)


# ── Platform flag helpers ─────────────────────────────────────────────────────


def test_exactly_one_platform_flag_true():
    flags = [is_windows(), is_macos(), is_linux()]
    assert sum(flags) == 1


def test_get_os_matches_platform_system():
    assert get_os() == platform.system()


def test_is_linux_on_linux():
    with patch("fluttercraft.core.platform.platform.system", return_value="Linux"):
        assert is_linux() is True
        assert is_windows() is False
        assert is_macos() is False


def test_is_windows():
    with patch("fluttercraft.core.platform.platform.system", return_value="Windows"):
        assert is_windows() is True
        assert is_linux() is False


def test_is_macos():
    with patch("fluttercraft.core.platform.platform.system", return_value="Darwin"):
        assert is_macos() is True
        assert is_linux() is False


# ── _extract_version ──────────────────────────────────────────────────────────


def test_extract_version_semver():
    assert _extract_version("Flutter 3.27.4 • channel stable") == "3.27.4"


def test_extract_version_two_part():
    assert _extract_version("git version 2.43") == "2.43"


def test_extract_version_dart():
    assert _extract_version("Dart SDK version: 3.3.0 (stable)") == "3.3.0"


def test_extract_version_no_numbers_falls_back_to_first_line():
    text = "some-tool info: no version here\nsecond line"
    result = _extract_version(text)
    assert result == "some-tool info: no version here"


def test_extract_version_truncates_at_40_chars():
    long_line = "a" * 60
    assert len(_extract_version(long_line)) <= 40


# ── _run_version_cmd ──────────────────────────────────────────────────────────


def test_run_version_cmd_returns_stdout():
    mock_result = MagicMock()
    mock_result.stdout = "3.27.4\n"
    mock_result.stderr = ""
    with patch("fluttercraft.core.platform.subprocess.run", return_value=mock_result):
        assert _run_version_cmd(["flutter", "--version"]) == "3.27.4"


def test_run_version_cmd_falls_back_to_stderr():
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_result.stderr = "Dart SDK 3.3.0"
    with patch("fluttercraft.core.platform.subprocess.run", return_value=mock_result):
        assert _run_version_cmd(["dart", "--version"]) == "Dart SDK 3.3.0"


def test_run_version_cmd_timeout_returns_empty():
    with patch(
        "fluttercraft.core.platform.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="flutter", timeout=5),
    ):
        assert _run_version_cmd(["flutter", "--version"]) == ""


def test_run_version_cmd_file_not_found_returns_empty():
    with patch(
        "fluttercraft.core.platform.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        assert _run_version_cmd(["flutter", "--version"]) == ""


# ── detect_tool ───────────────────────────────────────────────────────────────


def test_detect_tool_not_on_path():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        info = detect_tool("flutter", ["flutter", "--version"])
    assert info.available is False
    assert info.version == ""
    assert info.path == ""


def test_detect_tool_found_with_version():
    mock_result = MagicMock()
    mock_result.stdout = "Flutter 3.27.4 • channel stable"
    mock_result.stderr = ""
    with (
        patch("fluttercraft.core.platform.shutil.which", return_value="/usr/bin/flutter"),
        patch("fluttercraft.core.platform.subprocess.run", return_value=mock_result),
    ):
        info = detect_tool("flutter", ["flutter", "--version"])

    assert info.available is True
    assert info.version == "3.27.4"
    assert info.path == "/usr/bin/flutter"


def test_detect_tool_found_but_version_cmd_fails():
    with (
        patch("fluttercraft.core.platform.shutil.which", return_value="/usr/bin/flutter"),
        patch(
            "fluttercraft.core.platform.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="flutter", timeout=5),
        ),
    ):
        info = detect_tool("flutter", ["flutter", "--version"])

    assert info.available is True
    assert info.version == ""
    assert info.path == "/usr/bin/flutter"


# ── detect_toolchain ──────────────────────────────────────────────────────────


def test_detect_toolchain_returns_all_expected_keys():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        tools = detect_toolchain()
    assert set(tools.keys()) == {"flutter", "dart", "fvm", "git"}


def test_detect_toolchain_values_are_tool_info():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        tools = detect_toolchain()
    for info in tools.values():
        assert isinstance(info, ToolInfo)


# ── get_platform_info ─────────────────────────────────────────────────────────


def test_get_platform_info_returns_platform_info():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        info = get_platform_info()
    assert isinstance(info, PlatformInfo)


def test_get_platform_info_system_is_current_os():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        info = get_platform_info()
    assert info.system == platform.system()


def test_get_platform_info_has_python_version():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        info = get_platform_info()
    assert info.python_version == platform.python_version()


def test_get_platform_info_tools_dict_present():
    with patch("fluttercraft.core.platform.shutil.which", return_value=None):
        info = get_platform_info()
    assert isinstance(info.tools, dict)
    assert "flutter" in info.tools


# ── Dataclass fields ──────────────────────────────────────────────────────────


def test_tool_info_defaults():
    t = ToolInfo(name="git", available=True)
    assert t.version == ""
    assert t.path == ""


def test_platform_info_tools_default_empty():
    p = PlatformInfo(system="Linux", machine="x86_64", python_version="3.12", shell="/bin/bash")
    assert p.tools == {}
