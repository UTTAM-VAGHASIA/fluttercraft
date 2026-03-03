from __future__ import annotations

"""Tests for the FVM Manager plugin — pure functions only.

All tests that call ``fvm`` CLI functions are mocked so the test suite
passes even when FVM is not installed.
"""

from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.plugins.fvm_manager.fvm_api import (
    FvmVersion,
    _run_fvm,
    get_active_version,
    get_fvmrc,
    install_fvm,
    install_version,
    is_fvm_installed,
    list_installed,
    list_releases,
    remove_version,
    run_doctor,
    uninstall_fvm,
    use_version,
)


# ── FvmVersion dataclass ──────────────────────────────────────────────────────


def test_fvm_version_defaults():
    v = FvmVersion(name="3.29.3")
    assert v.name == "3.29.3"
    assert v.is_active is False
    assert v.channel == ""


def test_fvm_version_active():
    v = FvmVersion(name="3.27.1", is_active=True, channel="stable")
    assert v.is_active is True
    assert v.channel == "stable"


# ── is_fvm_installed ──────────────────────────────────────────────────────────


def test_fvm_installed_when_which_returns_path():
    with patch("shutil.which", return_value="/usr/bin/fvm"):
        assert is_fvm_installed() is True


def test_fvm_not_installed_when_which_returns_none():
    with patch("shutil.which", return_value=None):
        assert is_fvm_installed() is False


# ── _run_fvm ─────────────────────────────────────────────────────────────────


def _make_completed_process(stdout="", stderr="", returncode=0):
    mock = MagicMock()
    mock.stdout = stdout
    mock.stderr = stderr
    mock.returncode = returncode
    return mock


def test_run_fvm_success():
    with patch("subprocess.run", return_value=_make_completed_process(stdout="2.4.1")):
        ok, output = _run_fvm(["--version"])
    assert ok is True
    assert output == "2.4.1"


def test_run_fvm_uses_stderr_when_stdout_empty():
    with patch(
        "subprocess.run",
        return_value=_make_completed_process(stdout="", stderr="error msg", returncode=1),
    ):
        ok, output = _run_fvm(["bad"])
    assert ok is False
    assert output == "error msg"


def test_run_fvm_file_not_found():
    import subprocess

    with patch("subprocess.run", side_effect=FileNotFoundError("fvm not found")):
        ok, output = _run_fvm(["list"])
    assert ok is False
    assert "fvm not found" in output


def test_run_fvm_timeout():
    import subprocess

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["fvm"], 5)):
        ok, output = _run_fvm(["list"])
    assert ok is False
    assert "timed out" in output


# ── list_installed ────────────────────────────────────────────────────────────

_FVM_LIST_TABLE = """\
Installed Flutter SDK Versions:
┌─────────────────┬─────────┐
│ Version         │ Channel │
├─────────────────┼─────────┤
│ 3.29.3 (global) │ stable  │
│ 3.27.1          │ stable  │
└─────────────────┴─────────┘
Active: 3.29.3 (GLOBAL)
"""

_FVM_LIST_PLAIN = """\
3.29.3 (global active)
3.27.1
3.24.5
"""


def test_list_installed_parses_table_format():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, _FVM_LIST_TABLE),
    ):
        versions = list_installed()
    names = [v.name for v in versions]
    assert "3.29.3" in names
    assert "3.27.1" in names


def test_list_installed_parses_plain_format():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, _FVM_LIST_PLAIN),
    ):
        versions = list_installed()
    names = [v.name for v in versions]
    assert "3.29.3" in names
    assert "3.27.1" in names
    assert "3.24.5" in names


def test_list_installed_marks_active():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, _FVM_LIST_PLAIN),
    ):
        versions = list_installed()
    active = [v for v in versions if v.is_active]
    assert len(active) >= 1
    assert active[0].name == "3.29.3"


def test_list_installed_empty_when_fvm_fails():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(False, ""),
    ):
        versions = list_installed()
    assert versions == []


def test_list_installed_no_duplicates():
    output = "3.29.3\n3.29.3\n3.27.1\n"
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, output),
    ):
        versions = list_installed()
    names = [v.name for v in versions]
    assert len(names) == len(set(names))


# ── list_releases ─────────────────────────────────────────────────────────────

_FVM_RELEASES = """\
Flutter Releases
──────────────────────────
Channel    Version
stable     3.29.3
stable     3.27.4
stable     3.24.5
"""


def test_list_releases_parses_versions():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, _FVM_RELEASES),
    ):
        versions = list_releases("stable")
    assert "3.29.3" in versions
    assert "3.27.4" in versions
    assert "3.24.5" in versions


def test_list_releases_empty_on_failure():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(False, ""),
    ):
        versions = list_releases()
    assert versions == []


def test_list_releases_fallback_to_plain():
    # First call (with --channel) fails, second call succeeds
    call_count = [0]
    plain = "3.29.3\n3.27.1\n"

    def fake_run(args, **kw):
        call_count[0] += 1
        if "--channel" in args:
            return False, ""
        return True, plain

    with patch("fluttercraft.plugins.fvm_manager.fvm_api._run_fvm", side_effect=fake_run):
        versions = list_releases("stable")
    assert call_count[0] == 2
    assert "3.29.3" in versions


# ── install_version ───────────────────────────────────────────────────────────


def test_install_version_success():
    mock_proc = MagicMock()
    mock_proc.stdout = iter(["Downloading 3.29.3\n", "Done\n"])
    mock_proc.wait.return_value = None
    mock_proc.returncode = 0

    with patch("subprocess.Popen", return_value=mock_proc):
        collected: list[str] = []
        ok = install_version("3.29.3", on_line=collected.append)

    assert ok is True
    assert "Downloading 3.29.3" in collected


def test_install_version_failure():
    mock_proc = MagicMock()
    mock_proc.stdout = iter([])
    mock_proc.wait.return_value = None
    mock_proc.returncode = 1

    with patch("subprocess.Popen", return_value=mock_proc):
        ok = install_version("9.9.9")

    assert ok is False


def test_install_version_fvm_not_found():
    with patch("subprocess.Popen", side_effect=FileNotFoundError("no fvm")):
        errors: list[str] = []
        ok = install_version("3.29.3", on_line=errors.append)

    assert ok is False
    assert any("Error" in e for e in errors)


# ── use_version ───────────────────────────────────────────────────────────────


def test_use_version_global_passes_flag():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, "Now using Flutter 3.29.3"),
    ) as mock_run:
        ok, output = use_version("3.29.3", global_flag=True)
    args_used = mock_run.call_args[0][0]
    assert "--global" in args_used
    assert ok is True


def test_use_version_without_global_no_flag():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, ""),
    ) as mock_run:
        use_version("3.29.3", global_flag=False)
    args_used = mock_run.call_args[0][0]
    assert "--global" not in args_used


# ── remove_version ────────────────────────────────────────────────────────────


def test_remove_version_success():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, "Removed"),
    ):
        ok, output = remove_version("3.27.1")
    assert ok is True


def test_remove_version_failure_retries():
    call_count = [0]

    def fake(args, **kw):
        call_count[0] += 1
        # First call with --force fails
        if "--force" in args:
            return False, "flag not recognized"
        return True, "Removed"

    with patch("fluttercraft.plugins.fvm_manager.fvm_api._run_fvm", side_effect=fake):
        ok, _ = remove_version("3.27.1")
    assert call_count[0] == 2
    assert ok is True


# ── run_doctor ────────────────────────────────────────────────────────────────


def test_run_doctor_returns_output():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, "FVM is healthy"),
    ):
        output = run_doctor()
    assert "FVM is healthy" in output


def test_run_doctor_empty_on_failure():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(False, ""),
    ):
        output = run_doctor()
    assert output == ""


# ── get_fvmrc ─────────────────────────────────────────────────────────────────


def test_get_fvmrc_reads_valid_json(tmp_path):
    fvmrc = tmp_path / ".fvmrc"
    fvmrc.write_text('{"flutter": "3.29.3"}')
    result = get_fvmrc(str(tmp_path))
    assert result == {"flutter": "3.29.3"}


def test_get_fvmrc_returns_none_when_absent(tmp_path):
    result = get_fvmrc(str(tmp_path))
    assert result is None


def test_get_fvmrc_returns_none_on_invalid_json(tmp_path):
    fvmrc = tmp_path / ".fvmrc"
    fvmrc.write_text("not json{{{")
    result = get_fvmrc(str(tmp_path))
    assert result is None


# ── get_active_version ────────────────────────────────────────────────────────


def test_get_active_version_parses_version():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(True, "Flutter 3.29.3 • channel stable"),
    ):
        v = get_active_version()
    assert v == "3.29.3"


def test_get_active_version_none_when_not_found():
    with patch(
        "fluttercraft.plugins.fvm_manager.fvm_api._run_fvm",
        return_value=(False, ""),
    ):
        v = get_active_version()
    assert v is None


# ── install_fvm ───────────────────────────────────────────────────────────────


def test_install_fvm_success():
    with patch(
        "subprocess.run",
        return_value=_make_completed_process(stdout="Activated fvm 2.4.1"),
    ):
        ok, output = install_fvm()
    assert ok is True
    assert "Activated" in output


def test_install_fvm_dart_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError("dart")):
        ok, output = install_fvm()
    assert ok is False
    assert "dart not found" in output


# ── uninstall_fvm ─────────────────────────────────────────────────────────────


def test_uninstall_fvm_success():
    with patch(
        "subprocess.run",
        return_value=_make_completed_process(stdout="Deactivated fvm"),
    ):
        ok, output = uninstall_fvm()
    assert ok is True


def test_uninstall_fvm_dart_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError("dart")):
        ok, output = uninstall_fvm()
    assert ok is False
    assert "dart not found" in output


# ── Plugin class smoke test ───────────────────────────────────────────────────


def test_plugin_identity():
    from fluttercraft.plugins.fvm_manager.plugin import FvmManagerPlugin

    p = FvmManagerPlugin()
    assert p.id == "fvm"
    assert p.name == "FVM Manager"
    assert p.icon == "◈"


def test_plugin_commands_list():
    from fluttercraft.plugins.fvm_manager.plugin import FvmManagerPlugin

    p = FvmManagerPlugin()
    cmds = p.commands()
    assert len(cmds) >= 3
    titles = [c["title"] for c in cmds]
    assert any("Refresh" in t for t in titles)
    assert any("doctor" in t for t in titles)
    assert any("releases" in t for t in titles)


def test_plugin_commands_have_required_keys():
    from fluttercraft.plugins.fvm_manager.plugin import FvmManagerPlugin

    p = FvmManagerPlugin()
    for cmd in p.commands():
        assert "title" in cmd
        assert "description" in cmd
        assert "action" in cmd
        assert callable(cmd["action"])
