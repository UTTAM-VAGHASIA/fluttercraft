from __future__ import annotations

import pytest

from fluttercraft.plugins.base import Plugin, PluginContext, PluginRegistry


# ── Helpers ───────────────────────────────────────────────────────────────────


class _DummyPlugin(Plugin):
    """Minimal concrete plugin for testing."""

    def __init__(self, plugin_id: str = "dummy", crash_on: str = "") -> None:
        self._id = plugin_id
        self._crash_on = crash_on
        self.init_called = False
        self.start_called = False
        self.stop_called = False

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return "Dummy"

    @property
    def icon(self) -> str:
        return "◈"

    def init(self, ctx: PluginContext) -> None:
        if self._crash_on == "init":
            raise RuntimeError("init crash")
        self.init_called = True
        super().init(ctx)

    def start(self) -> None:
        if self._crash_on == "start":
            raise RuntimeError("start crash")
        self.start_called = True

    def stop(self) -> None:
        if self._crash_on == "stop":
            raise RuntimeError("stop crash")
        self.stop_called = True

    def commands(self) -> list[dict]:
        return [{"title": f"{self._id}: Do thing", "description": "test", "action": None}]


def _make_ctx() -> PluginContext:
    from unittest.mock import MagicMock
    return PluginContext(
        work_dir="/tmp",
        project_root="/tmp",
        config=MagicMock(),
        event_bus=MagicMock(),
        state=MagicMock(),
    )


# ── Plugin ABC tests ──────────────────────────────────────────────────────────


def test_plugin_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Plugin()  # type: ignore[abstract]


def test_plugin_identity():
    p = _DummyPlugin("fvm")
    assert p.id == "fvm"
    assert p.name == "Dummy"
    assert p.icon == "◈"


def test_plugin_focus_context_defaults_to_id():
    p = _DummyPlugin("git")
    assert p.focus_context == "git"


def test_plugin_is_focused_default_false():
    p = _DummyPlugin()
    assert p.is_focused is False


def test_plugin_commands_default_empty():
    class _MinPlugin(Plugin):
        @property
        def id(self): return "min"
        @property
        def name(self): return "Min"
        @property
        def icon(self): return "•"

    assert _MinPlugin().commands() == []


def test_plugin_lifecycle():
    p = _DummyPlugin()
    ctx = _make_ctx()
    p.init(ctx)
    assert p.init_called
    assert p._ctx is ctx

    p.start()
    assert p.start_called

    p.stop()
    assert p.stop_called


def test_plugin_reinit_calls_stop_init_start():
    p = _DummyPlugin()
    ctx1 = _make_ctx()
    ctx2 = _make_ctx()
    p.init(ctx1)
    p.start()
    p.stop_called = False  # reset

    p.reinit(ctx2)
    assert p.stop_called
    assert p._ctx is ctx2
    assert p.start_called


def test_plugin_compose_returns_empty_iter():
    p = _DummyPlugin()
    result = list(p.compose())
    assert result == []


# ── PluginContext tests ────────────────────────────────────────────────────────


def test_plugin_context_fields():
    from unittest.mock import MagicMock
    config = MagicMock()
    bus = MagicMock()
    state = MagicMock()
    ctx = PluginContext(
        work_dir="/home/user",
        project_root="/home/user/myapp",
        config=config,
        event_bus=bus,
        state=state,
    )
    assert ctx.work_dir == "/home/user"
    assert ctx.project_root == "/home/user/myapp"
    assert ctx.config is config
    assert ctx.event_bus is bus
    assert ctx.state is state
    assert ctx.adapters == {}
    assert ctx.keymap is None


def test_plugin_context_adapters_default():
    ctx = _make_ctx()
    assert isinstance(ctx.adapters, dict)
    assert ctx.adapters == {}


# ── PluginRegistry tests ──────────────────────────────────────────────────────


def test_registry_register_and_get():
    reg = PluginRegistry()
    p = _DummyPlugin("fvm")
    reg.register(p)
    assert reg.get("fvm") is p
    assert "fvm" in reg


def test_registry_duplicate_register_ignored():
    reg = PluginRegistry()
    p1 = _DummyPlugin("fvm")
    p2 = _DummyPlugin("fvm")
    reg.register(p1)
    reg.register(p2)
    assert reg.get("fvm") is p1
    assert len(reg) == 1


def test_registry_get_missing_returns_none():
    reg = PluginRegistry()
    assert reg.get("nonexistent") is None


def test_registry_init_all():
    reg = PluginRegistry()
    p1 = _DummyPlugin("a")
    p2 = _DummyPlugin("b")
    reg.register(p1)
    reg.register(p2)
    ctx = _make_ctx()
    reg.init_all(ctx)
    assert p1.init_called
    assert p2.init_called


def test_registry_start_all():
    reg = PluginRegistry()
    p = _DummyPlugin("a")
    reg.register(p)
    ctx = _make_ctx()
    reg.init_all(ctx)
    reg.start_all()
    assert p.start_called


def test_registry_stop_all():
    reg = PluginRegistry()
    p = _DummyPlugin("a")
    reg.register(p)
    ctx = _make_ctx()
    reg.init_all(ctx)
    reg.stop_all()
    assert p.stop_called


def test_registry_reinit_all():
    reg = PluginRegistry()
    p = _DummyPlugin("a")
    reg.register(p)
    ctx1 = _make_ctx()
    ctx2 = _make_ctx()
    reg.init_all(ctx1)
    reg.reinit_all(ctx2)
    assert p._ctx is ctx2


def test_registry_silent_degradation_init():
    """A crashing plugin must not stop others from being inited."""
    reg = PluginRegistry()
    crash = _DummyPlugin("crash", crash_on="init")
    good = _DummyPlugin("good")
    reg.register(crash)
    reg.register(good)
    ctx = _make_ctx()
    reg.init_all(ctx)  # must not raise
    assert good.init_called


def test_registry_silent_degradation_start():
    reg = PluginRegistry()
    crash = _DummyPlugin("crash", crash_on="start")
    good = _DummyPlugin("good")
    reg.register(crash)
    reg.register(good)
    ctx = _make_ctx()
    reg.init_all(ctx)
    reg.start_all()  # must not raise
    assert good.start_called


def test_registry_silent_degradation_stop():
    reg = PluginRegistry()
    crash = _DummyPlugin("crash", crash_on="stop")
    good = _DummyPlugin("good")
    reg.register(crash)
    reg.register(good)
    ctx = _make_ctx()
    reg.init_all(ctx)
    reg.stop_all()  # must not raise
    assert good.stop_called


def test_registry_all_commands():
    reg = PluginRegistry()
    p1 = _DummyPlugin("a")
    p2 = _DummyPlugin("b")
    reg.register(p1)
    reg.register(p2)
    ctx = _make_ctx()
    reg.init_all(ctx)
    cmds = reg.all_commands()
    assert len(cmds) == 2
    assert any(c["title"].startswith("a:") for c in cmds)
    assert any(c["title"].startswith("b:") for c in cmds)
    # plugin_id injected automatically
    assert all("plugin_id" in c for c in cmds)


def test_registry_plugins_property_order():
    reg = PluginRegistry()
    p1 = _DummyPlugin("first")
    p2 = _DummyPlugin("second")
    p3 = _DummyPlugin("third")
    reg.register(p1)
    reg.register(p2)
    reg.register(p3)
    ids = [p.id for p in reg.plugins]
    assert ids == ["first", "second", "third"]


def test_registry_len():
    reg = PluginRegistry()
    assert len(reg) == 0
    reg.register(_DummyPlugin("a"))
    reg.register(_DummyPlugin("b"))
    assert len(reg) == 2
