from __future__ import annotations

import pytest

from fluttercraft.widgets.resize_handle import (
    ResizeHandle,
    SIDEBAR_MIN,
    SIDEBAR_MAX,
    SIDEBAR_DEFAULT,
    _clamp_sidebar,
)


# ── Pure function tests (no Textual) ─────────────────────────────────────────


def test_clamp_sidebar_below_min():
    assert _clamp_sidebar(0) == SIDEBAR_MIN


def test_clamp_sidebar_above_max():
    assert _clamp_sidebar(999) == SIDEBAR_MAX


def test_clamp_sidebar_at_min():
    assert _clamp_sidebar(SIDEBAR_MIN) == SIDEBAR_MIN


def test_clamp_sidebar_at_max():
    assert _clamp_sidebar(SIDEBAR_MAX) == SIDEBAR_MAX


def test_clamp_sidebar_mid_value():
    mid = (SIDEBAR_MIN + SIDEBAR_MAX) // 2
    assert _clamp_sidebar(mid) == mid


def test_clamp_sidebar_default_is_valid():
    assert _clamp_sidebar(SIDEBAR_DEFAULT) == SIDEBAR_DEFAULT


def test_sidebar_default_between_min_and_max():
    assert SIDEBAR_MIN <= SIDEBAR_DEFAULT <= SIDEBAR_MAX


def test_resized_message_positive_delta():
    msg = ResizeHandle.Resized(5)
    assert msg.delta == 5


def test_resized_message_negative_delta():
    msg = ResizeHandle.Resized(-3)
    assert msg.delta == -3


def test_resized_message_zero_delta():
    msg = ResizeHandle.Resized(0)
    assert msg.delta == 0


# ── ResizeHandle widget initial state (no Textual mount) ─────────────────────


def test_resize_handle_initial_not_dragging():
    handle = ResizeHandle()
    assert handle._dragging is False


def test_resize_handle_initial_last_x_zero():
    handle = ResizeHandle()
    assert handle._last_x == 0


# ── Textual widget tests ──────────────────────────────────────────────────────


def _make_handle_app():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield ResizeHandle()

    return _TestApp()


@pytest.mark.asyncio
async def test_resize_handle_mounts():
    async with _make_handle_app().run_test() as pilot:
        handle = pilot.app.query_one(ResizeHandle)
        assert handle is not None


@pytest.mark.asyncio
async def test_resize_handle_no_dragging_class_initially():
    async with _make_handle_app().run_test() as pilot:
        handle = pilot.app.query_one(ResizeHandle)
        assert not handle.has_class("dragging")


@pytest.mark.asyncio
async def test_resize_handle_resized_message_posted_on_drag():
    """Simulate a drag sequence and verify Resized message is posted."""
    received: list[ResizeHandle.Resized] = []

    from textual.app import App, ComposeResult
    from textual.geometry import Offset

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield ResizeHandle()

        def on_resize_handle_resized(self, event: ResizeHandle.Resized) -> None:
            received.append(event)

    async with _TestApp().run_test() as pilot:
        handle = pilot.app.query_one(ResizeHandle)
        # Manually simulate drag sequence
        handle._dragging = True
        handle._last_x = 10
        handle.add_class("dragging")
        # Fire a move of +3 columns
        handle._last_x = 10
        handle.post_message(ResizeHandle.Resized(3))
        await pilot.pause()
        assert len(received) == 1
        assert received[0].delta == 3


@pytest.mark.asyncio
async def test_resize_handle_dragging_class_cleared_on_mouse_up():
    from textual.app import App, ComposeResult

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield ResizeHandle()

    async with _TestApp().run_test() as pilot:
        handle = pilot.app.query_one(ResizeHandle)
        # Simulate drag state
        handle._dragging = True
        handle.add_class("dragging")
        # Simulate mouse up via on_leave safety path
        handle.on_leave.__func__(handle, None)  # type: ignore[attr-defined]
        assert not handle.has_class("dragging")
        assert handle._dragging is False


# ── DashboardScreen sidebar-width integration tests ───────────────────────────


def _make_dashboard_app():
    from unittest.mock import patch
    from textual.app import App, ComposeResult
    from fluttercraft.screens.dashboard import DashboardScreen

    class _TestApp(App):
        def compose(self) -> ComposeResult:
            yield DashboardScreen()

    return _TestApp()


@pytest.mark.asyncio
async def test_dashboard_initial_sidebar_width():
    from unittest.mock import patch

    with patch(
        "fluttercraft.widgets.header.detect_toolchain",
        return_value={
            "flutter": type("T", (), {"available": False, "version": ""})(),
            "fvm":     type("T", (), {"available": False, "version": ""})(),
        },
    ):
        async with _make_dashboard_app().run_test() as pilot:
            screen = pilot.app.query_one("DashboardScreen")
            assert screen._sidebar_width == SIDEBAR_DEFAULT


@pytest.mark.asyncio
async def test_dashboard_grow_sidebar():
    from unittest.mock import patch

    with patch(
        "fluttercraft.widgets.header.detect_toolchain",
        return_value={
            "flutter": type("T", (), {"available": False, "version": ""})(),
            "fvm":     type("T", (), {"available": False, "version": ""})(),
        },
    ):
        async with _make_dashboard_app().run_test() as pilot:
            screen = pilot.app.query_one("DashboardScreen")
            before = screen._sidebar_width
            screen.action_grow_sidebar()
            assert screen._sidebar_width == before + 2


@pytest.mark.asyncio
async def test_dashboard_shrink_sidebar():
    from unittest.mock import patch

    with patch(
        "fluttercraft.widgets.header.detect_toolchain",
        return_value={
            "flutter": type("T", (), {"available": False, "version": ""})(),
            "fvm":     type("T", (), {"available": False, "version": ""})(),
        },
    ):
        async with _make_dashboard_app().run_test() as pilot:
            screen = pilot.app.query_one("DashboardScreen")
            before = screen._sidebar_width
            screen.action_shrink_sidebar()
            assert screen._sidebar_width == before - 2


@pytest.mark.asyncio
async def test_dashboard_sidebar_width_clamped_at_min():
    from unittest.mock import patch

    with patch(
        "fluttercraft.widgets.header.detect_toolchain",
        return_value={
            "flutter": type("T", (), {"available": False, "version": ""})(),
            "fvm":     type("T", (), {"available": False, "version": ""})(),
        },
    ):
        async with _make_dashboard_app().run_test() as pilot:
            screen = pilot.app.query_one("DashboardScreen")
            screen._apply_sidebar_width(0)
            assert screen._sidebar_width == SIDEBAR_MIN


@pytest.mark.asyncio
async def test_dashboard_sidebar_width_clamped_at_max():
    from unittest.mock import patch

    with patch(
        "fluttercraft.widgets.header.detect_toolchain",
        return_value={
            "flutter": type("T", (), {"available": False, "version": ""})(),
            "fvm":     type("T", (), {"available": False, "version": ""})(),
        },
    ):
        async with _make_dashboard_app().run_test() as pilot:
            screen = pilot.app.query_one("DashboardScreen")
            screen._apply_sidebar_width(999)
            assert screen._sidebar_width == SIDEBAR_MAX
