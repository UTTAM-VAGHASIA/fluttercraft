from __future__ import annotations

from unittest.mock import patch

import pytest

from fluttercraft.widgets.header import FlutterCraftHeader, _format_info


# ── Pure function tests (no Textual) ─────────────────────────────────────────


def test_format_info_minimal():
    result = _format_info("3.27.4", "3.1.6", "linux")
    assert "Flutter 3.27.4" in result
    assert "FVM 3.1.6" in result
    assert "linux" in result


def test_format_info_with_project():
    result = _format_info("3.27.4", "3.1.6", "linux", project_name="my_app")
    assert "my_app" in result


def test_format_info_with_git_branch():
    result = _format_info("3.27.4", "3.1.6", "linux", git_branch="main")
    assert "main" in result


def test_format_info_all_fields():
    result = _format_info("3.27.4", "3.1.6", "linux", "my_app", "feature/x")
    assert "Flutter 3.27.4" in result
    assert "FVM 3.1.6" in result
    assert "linux" in result
    assert "my_app" in result
    assert "feature/x" in result


def test_format_info_empty_project_omitted():
    result = _format_info("3.27.4", "3.1.6", "linux", project_name="")
    parts = result.split("  ·  ")
    assert len(parts) == 3  # flutter, fvm, os — no project


def test_format_info_empty_branch_omitted():
    result = _format_info("3.27.4", "3.1.6", "linux", git_branch="")
    parts = result.split("  ·  ")
    assert len(parts) == 3  # flutter, fvm, os — no branch


def test_format_info_separator():
    result = _format_info("3.27.4", "3.1.6", "linux")
    assert "  ·  " in result


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_test_app():
    """Return a minimal App that mounts FlutterCraftHeader."""
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield FlutterCraftHeader()

    return _TestApp()


@pytest.mark.asyncio
async def test_header_mounts_without_error():
    with patch("fluttercraft.widgets.header.detect_toolchain", return_value={
        "flutter": type("T", (), {"available": True, "version": "3.27.4"})(),
        "fvm": type("T", (), {"available": True, "version": "3.1.6"})(),
        "dart": type("T", (), {"available": False, "version": ""})(),
        "git": type("T", (), {"available": True, "version": "2.43"})(),
    }):
        async with _make_test_app().run_test() as pilot:
            header = pilot.app.query_one(FlutterCraftHeader)
            assert header is not None


@pytest.mark.asyncio
async def test_header_set_project_updates_reactive():
    with patch("fluttercraft.widgets.header.detect_toolchain", return_value={
        "flutter": type("T", (), {"available": False, "version": ""})(),
        "fvm": type("T", (), {"available": False, "version": ""})(),
        "dart": type("T", (), {"available": False, "version": ""})(),
        "git": type("T", (), {"available": False, "version": ""})(),
    }):
        async with _make_test_app().run_test() as pilot:
            header = pilot.app.query_one(FlutterCraftHeader)
            header.set_project("awesome_app")
            assert header.project_name == "awesome_app"


@pytest.mark.asyncio
async def test_header_set_git_branch_updates_reactive():
    with patch("fluttercraft.widgets.header.detect_toolchain", return_value={
        "flutter": type("T", (), {"available": False, "version": ""})(),
        "fvm": type("T", (), {"available": False, "version": ""})(),
        "dart": type("T", (), {"available": False, "version": ""})(),
        "git": type("T", (), {"available": False, "version": ""})(),
    }):
        async with _make_test_app().run_test() as pilot:
            header = pilot.app.query_one(FlutterCraftHeader)
            header.set_git_branch("feature/v0.2.0-tui")
            assert header.git_branch == "feature/v0.2.0-tui"


@pytest.mark.asyncio
async def test_header_reactive_defaults():
    with patch("fluttercraft.widgets.header.detect_toolchain", return_value={
        "flutter": type("T", (), {"available": False, "version": ""})(),
        "fvm": type("T", (), {"available": False, "version": ""})(),
        "dart": type("T", (), {"available": False, "version": ""})(),
        "git": type("T", (), {"available": False, "version": ""})(),
    }):
        async with _make_test_app().run_test() as pilot:
            header = pilot.app.query_one(FlutterCraftHeader)
            assert header.project_name == ""
            assert header.git_branch == ""
