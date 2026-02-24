from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from fluttercraft.core.compat import (
    GLYPHS_ASCII,
    GLYPHS_UNICODE,
    REQUIRED_TOOLS,
    RECOMMENDED_TOOLS,
    check_dependencies,
    get_config_dir,
    get_glyph,
    get_terminal_size,
    missing_required,
    normalise_newlines,
    supports_mouse,
    supports_truecolor,
    supports_unicode,
)


# ── get_config_dir ────────────────────────────────────────────────────────────


def test_get_config_dir_returns_path():
    result = get_config_dir()
    assert isinstance(result, Path)


def test_get_config_dir_posix_uses_home_dot_fluttercraft():
    with patch("sys.platform", "linux"):
        result = get_config_dir()
    assert result == Path.home() / ".fluttercraft"


def test_get_config_dir_macos_uses_home_dot_fluttercraft():
    with patch("sys.platform", "darwin"):
        result = get_config_dir()
    assert result == Path.home() / ".fluttercraft"


def test_get_config_dir_windows_uses_appdata():
    with patch("sys.platform", "win32"), \
         patch("os.environ", {"APPDATA": "C:\\Users\\test\\AppData\\Roaming"}):
        result = get_config_dir()
    assert "FlutterCraft" in str(result)
    assert "Roaming" in str(result) or "AppData" in str(result)


def test_get_config_dir_windows_fallback_no_appdata():
    with patch("sys.platform", "win32"), \
         patch("os.environ", {}):
        result = get_config_dir()
    assert "FlutterCraft" in str(result)


def test_get_config_dir_ends_with_fluttercraft():
    result = get_config_dir()
    # Last path component is always FlutterCraft or .fluttercraft
    assert "fluttercraft" in str(result).lower()


# ── supports_unicode ──────────────────────────────────────────────────────────


def test_supports_unicode_utf8_encoding():
    class _FakeStdout:
        encoding = "utf-8"

    with patch("sys.stdout", _FakeStdout()):
        assert supports_unicode() is True


def test_supports_unicode_utf8_no_dash():
    class _FakeStdout:
        encoding = "utf8"

    with patch("sys.stdout", _FakeStdout()):
        assert supports_unicode() is True


def test_supports_unicode_lang_env_utf8():
    class _FakeStdout:
        encoding = "ascii"

    with patch("sys.stdout", _FakeStdout()), \
         patch("os.environ", {"LANG": "en_US.UTF-8"}):
        assert supports_unicode() is True


def test_supports_unicode_lc_all_env():
    class _FakeStdout:
        encoding = "ascii"

    with patch("sys.stdout", _FakeStdout()), \
         patch("os.environ", {"LC_ALL": "en_US.utf8"}):
        assert supports_unicode() is True


def test_supports_unicode_windows_terminal():
    class _FakeStdout:
        encoding = "ascii"

    with patch("sys.platform", "win32"), \
         patch("sys.stdout", _FakeStdout()), \
         patch("os.environ", {"WT_SESSION": "some-uuid"}):
        assert supports_unicode() is True


def test_supports_unicode_iterm():
    class _FakeStdout:
        encoding = "ascii"

    with patch("sys.stdout", _FakeStdout()), \
         patch("os.environ", {"TERM_PROGRAM": "iTerm.app"}):
        assert supports_unicode() is True


# ── supports_truecolor ────────────────────────────────────────────────────────


def test_supports_truecolor_colorterm_truecolor():
    with patch("os.environ", {"COLORTERM": "truecolor"}):
        assert supports_truecolor() is True


def test_supports_truecolor_colorterm_24bit():
    with patch("os.environ", {"COLORTERM": "24bit"}):
        assert supports_truecolor() is True


def test_supports_truecolor_256_is_false():
    with patch("os.environ", {"COLORTERM": "256colors"}):
        assert supports_truecolor() is False


def test_supports_truecolor_xterm_direct():
    with patch("os.environ", {"COLORTERM": "", "TERM": "xterm-direct"}):
        assert supports_truecolor() is True


def test_supports_truecolor_empty_env():
    with patch("os.environ", {}):
        assert supports_truecolor() is False


# ── supports_mouse ────────────────────────────────────────────────────────────


def test_supports_mouse_normal_term():
    with patch("os.environ", {"TERM": "xterm-256color"}):
        assert supports_mouse() is True


def test_supports_mouse_dumb_term():
    with patch("os.environ", {"TERM": "dumb"}):
        assert supports_mouse() is False


def test_supports_mouse_empty_term():
    with patch("os.environ", {"TERM": ""}):
        assert supports_mouse() is False


# ── Glyph sets ────────────────────────────────────────────────────────────────


def test_glyphs_unicode_and_ascii_have_same_keys():
    assert set(GLYPHS_UNICODE.keys()) == set(GLYPHS_ASCII.keys())


def test_glyphs_ascii_all_printable():
    for key, val in GLYPHS_ASCII.items():
        assert val.isprintable(), f"GLYPHS_ASCII[{key!r}] = {val!r} is not printable"


def test_glyphs_ascii_all_ascii():
    for key, val in GLYPHS_ASCII.items():
        assert val.isascii(), f"GLYPHS_ASCII[{key!r}] = {val!r} contains non-ASCII"


def test_glyphs_unicode_has_bullet():
    assert "bullet" in GLYPHS_UNICODE


def test_glyphs_unicode_has_success():
    assert "success" in GLYPHS_UNICODE


# ── get_glyph ─────────────────────────────────────────────────────────────────


def test_get_glyph_force_ascii():
    result = get_glyph("success", force_ascii=True)
    assert result == GLYPHS_ASCII["success"]


def test_get_glyph_unicode_when_supported():
    class _FakeStdout:
        encoding = "utf-8"

    with patch("sys.stdout", _FakeStdout()):
        result = get_glyph("success")
    assert result == GLYPHS_UNICODE["success"]


def test_get_glyph_ascii_when_not_supported():
    class _FakeStdout:
        encoding = "ascii"

    with patch("sys.stdout", _FakeStdout()), \
         patch("os.environ", {"TERM": "dumb"}):
        result = get_glyph("bullet", force_ascii=True)
    assert result == GLYPHS_ASCII["bullet"]


def test_get_glyph_unknown_key_returns_key():
    result = get_glyph("unknown_glyph_xyz", force_ascii=True)
    assert result == "unknown_glyph_xyz"


# ── check_dependencies ────────────────────────────────────────────────────────


def test_check_dependencies_returns_dict():
    result = check_dependencies(["git"])
    assert isinstance(result, dict)
    assert "git" in result


def test_check_dependencies_bool_values():
    result = check_dependencies(["git"])
    for val in result.values():
        assert isinstance(val, bool)


def test_check_dependencies_git_found():
    # git should be available in any dev environment
    result = check_dependencies(["git"])
    assert result["git"] is True


def test_check_dependencies_fake_tool_not_found():
    result = check_dependencies(["___nonexistent_tool_xyz___"])
    assert result["___nonexistent_tool_xyz___"] is False


def test_missing_required_returns_list():
    result = missing_required()
    assert isinstance(result, list)


def test_required_tools_not_empty():
    assert len(REQUIRED_TOOLS) > 0


def test_recommended_tools_includes_flutter():
    assert "flutter" in RECOMMENDED_TOOLS


# ── get_terminal_size ─────────────────────────────────────────────────────────


def test_get_terminal_size_returns_tuple():
    result = get_terminal_size()
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_get_terminal_size_positive_values():
    cols, rows = get_terminal_size()
    assert cols > 0
    assert rows > 0


def test_get_terminal_size_custom_fallback():
    with patch("shutil.get_terminal_size", return_value=type("S", (), {"columns": 132, "lines": 50})()):
        cols, rows = get_terminal_size(fallback=(132, 50))
    assert cols == 132
    assert rows == 50


# ── normalise_newlines ────────────────────────────────────────────────────────


def test_normalise_newlines_crlf():
    assert normalise_newlines("a\r\nb") == "a\nb"


def test_normalise_newlines_cr():
    assert normalise_newlines("a\rb") == "a\nb"


def test_normalise_newlines_lf_unchanged():
    assert normalise_newlines("a\nb") == "a\nb"


def test_normalise_newlines_mixed():
    result = normalise_newlines("a\r\nb\rc\nd")
    assert result == "a\nb\nc\nd"


def test_normalise_newlines_empty():
    assert normalise_newlines("") == ""
