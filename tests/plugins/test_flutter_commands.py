from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.plugins.flutter_commands.flutter_api import (
    FlutterDevice,
    colorize_analyze_line,
    colorize_doctor_line,
    colorize_test_line,
    esc,
    get_devices,
    get_flutter_version,
    is_flutter_installed,
)
from fluttercraft.plugins.flutter_commands.plugin import (
    FlutterCommandsPlugin,
    _CATEGORIES,
    _CMD_ARGS,
)
from fluttercraft.plugins.base import PluginContext


# ── flutter_api unit tests ────────────────────────────────────────────────────


class TestEsc:
    def test_escapes_opening_bracket(self):
        assert esc("[bold]hello[/bold]") == "\\[bold]hello\\[/bold]"

    def test_strips_ansi_before_escaping(self):
        ansi = "\x1b[32mGreen\x1b[0m"
        result = esc(ansi)
        assert "\x1b" not in result
        assert "Green" in result

    def test_plain_text_unchanged(self):
        assert esc("hello world") == "hello world"


class TestIsFlutterInstalled:
    def test_returns_true_when_flutter_on_path(self):
        with patch("shutil.which", return_value="/usr/bin/flutter"):
            assert is_flutter_installed() is True

    def test_returns_false_when_flutter_missing(self):
        with patch("shutil.which", return_value=None):
            assert is_flutter_installed() is False


class TestGetFlutterVersion:
    def test_parses_version_from_output(self):
        fake_output = "Flutter 3.29.3 • channel stable • https://github.com/flutter/flutter.git\n"
        mock_result = MagicMock()
        mock_result.stdout = fake_output
        with patch("subprocess.run", return_value=mock_result):
            assert get_flutter_version() == "3.29.3"

    def test_returns_none_on_exception(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert get_flutter_version() is None

    def test_returns_none_when_no_version_in_output(self):
        mock_result = MagicMock()
        mock_result.stdout = "unexpected output\n"
        with patch("subprocess.run", return_value=mock_result):
            assert get_flutter_version() is None


class TestGetDevices:
    def test_parses_device_line(self):
        fake_output = (
            "sdk gphone64 x86 64 • emulator-5554 • android-x64 • Android 14 (API 34)\n"
        )
        mock_result = MagicMock()
        mock_result.stdout = fake_output
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            devices = get_devices()
        assert len(devices) == 1
        assert devices[0].id == "emulator-5554"
        assert devices[0].is_emulator is True

    def test_returns_empty_on_failure(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 1
        with patch("subprocess.run", return_value=mock_result):
            assert get_devices() == []


class TestColorizeDoctorLine:
    def test_check_mark_line_is_green(self):
        result = colorize_doctor_line("  [✓] Flutter (Channel stable)")
        assert "#9ece6a" in result

    def test_cross_line_is_red(self):
        result = colorize_doctor_line("  [✗] Android toolchain")
        assert "#f7768e" in result

    def test_exclamation_line_is_yellow(self):
        result = colorize_doctor_line("  [!] Android Studio (not installed)")
        assert "#e0af68" in result

    def test_doctor_header_is_blue(self):
        result = colorize_doctor_line("Doctor summary (to see all details, run flutter doctor -v):")
        assert "#7aa2f7" in result


class TestColorizeAnalyzeLine:
    def test_error_line_is_red(self):
        result = colorize_analyze_line("error • The function isn't defined • lib/main.dart:5:3")
        assert "#f7768e" in result

    def test_warning_line_is_yellow(self):
        result = colorize_analyze_line("warning • Unused import • lib/main.dart:2:1")
        assert "#e0af68" in result

    def test_no_issues_is_green(self):
        result = colorize_analyze_line("No issues found!")
        assert "#9ece6a" in result


class TestColorizeTestLine:
    def test_all_passed_is_green_bold(self):
        result = colorize_test_line("All tests passed!")
        assert "#9ece6a" in result

    def test_failed_line_is_red(self):
        result = colorize_test_line("Some tests failed.")
        assert "#f7768e" in result

    def test_progress_with_failures_is_red(self):
        result = colorize_test_line("00:02 +3 -1: test name")
        assert "#f7768e" in result

    def test_progress_all_passing_is_green(self):
        result = colorize_test_line("00:01 +5: test name")
        assert "#9ece6a" in result


# ── Plugin unit tests ─────────────────────────────────────────────────────────


class TestFlutterCommandsPlugin:
    def _make_plugin(self) -> FlutterCommandsPlugin:
        plugin = FlutterCommandsPlugin()
        ctx = PluginContext(
            work_dir="",
            project_root="",
            config=MagicMock(),
            event_bus=MagicMock(),
            state=MagicMock(),
        )
        plugin.init(ctx)
        return plugin

    def test_plugin_id_is_flutter(self):
        plugin = self._make_plugin()
        assert plugin.id == "flutter"

    def test_plugin_name(self):
        plugin = self._make_plugin()
        assert plugin.name == "Flutter"

    def test_commands_returns_list(self):
        plugin = self._make_plugin()
        cmds = plugin.commands()
        assert isinstance(cmds, list)
        assert len(cmds) > 0
        for cmd in cmds:
            assert "title" in cmd
            assert "description" in cmd
            assert "action" in cmd
            assert callable(cmd["action"])

    def test_handle_command_ignores_non_flutter(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("fvm list") is False
        assert plugin.handle_command("git status") is False

    def test_handle_command_flutter_no_subcommand(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("flutter") is False

    def test_handle_command_returns_false_without_widget(self):
        plugin = self._make_plugin()
        # _widget is None since we never called compose()
        assert plugin.handle_command("flutter doctor") is False

    def test_handle_command_routes_with_widget(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget

        assert plugin.handle_command("flutter doctor") is True
        mock_widget.trigger_doctor.assert_called_once()

        assert plugin.handle_command("flutter devices") is True
        mock_widget.trigger_devices.assert_called_once()

        assert plugin.handle_command("flutter test") is True
        mock_widget.trigger_test.assert_called_once()

        assert plugin.handle_command("flutter analyze") is True
        mock_widget.trigger_analyze.assert_called_once()

        assert plugin.handle_command("flutter clean") is True
        mock_widget.trigger_clean.assert_called_once()

        assert plugin.handle_command("flutter pub get") is True
        mock_widget.trigger_pub.assert_called_with("get")

        assert plugin.handle_command("flutter build apk") is True
        mock_widget.trigger_build.assert_called_with("apk")

        assert plugin.handle_command("flutter create my_app") is True
        mock_widget.trigger_create.assert_called_with("my_app")

    def test_handle_command_unknown_subcommand_returns_false(self):
        plugin = self._make_plugin()
        plugin._widget = MagicMock()
        assert plugin.handle_command("flutter unknown_cmd") is False

    def test_handle_command_create_without_name_returns_false(self):
        plugin = self._make_plugin()
        plugin._widget = MagicMock()
        assert plugin.handle_command("flutter create") is False


# ── Data integrity tests ───────────────────────────────────────────────────────


class TestCategoryData:
    def test_all_categories_have_name_and_desc(self):
        for item in _CATEGORIES:
            assert len(item) == 2
            assert item[0]  # non-empty name
            assert item[1]  # non-empty description

    def test_cmd_args_values_are_lists(self):
        for key, val in _CMD_ARGS.items():
            assert isinstance(val, list)
            assert len(val) >= 1

    def test_flutter_device_dataclass(self):
        d = FlutterDevice(id="abc", name="Pixel 7", platform="android")
        assert d.id == "abc"
        assert d.is_emulator is False
