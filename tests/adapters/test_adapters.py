"""Tests for Phase 9 — CLI Adapter infrastructure."""
from __future__ import annotations

import time
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.adapters.base import CLIAdapter, AdapterSession, AdapterMessage
from fluttercraft.adapters.detect import detect_adapters, binary_on_path
from fluttercraft.adapters.claude import ClaudeAdapter
from fluttercraft.adapters.gemini import GeminiAdapter
from fluttercraft.adapters.opencode import OpenCodeAdapter
from fluttercraft.plugins.cli_adapter.session_store import (
    save_sessions,
    load_sessions,
    get_history_for_adapter,
)
from fluttercraft.plugins.cli_adapter.plugin import CLIAdapterPlugin


# ── AdapterMessage ────────────────────────────────────────────────────────────


def test_adapter_message_defaults():
    m = AdapterMessage(role="user", content="hello")
    assert m.role == "user"
    assert m.content == "hello"
    assert m.timestamp == 0.0


def test_adapter_message_with_timestamp():
    ts = time.time()
    m = AdapterMessage(role="assistant", content="hi", timestamp=ts)
    assert m.timestamp == ts


# ── AdapterSession ────────────────────────────────────────────────────────────


def test_adapter_session_defaults():
    s = AdapterSession(adapter_id="claude", session_id="abc")
    assert s.adapter_id == "claude"
    assert s.session_id == "abc"
    assert s.messages == []
    assert s.active is False
    assert s.context == {}


def test_adapter_session_with_messages():
    s = AdapterSession(
        adapter_id="gemini",
        session_id="xyz",
        active=True,
        messages=[AdapterMessage("user", "hello")],
    )
    assert len(s.messages) == 1
    assert s.active is True


# ── CLIAdapter ABC ────────────────────────────────────────────────────────────


def test_cannot_instantiate_base():
    with pytest.raises(TypeError):
        CLIAdapter()  # type: ignore[abstract]


def test_build_context_prompt_empty():
    adapter = ClaudeAdapter()
    assert adapter.build_context_prompt({}) == ""


def test_build_context_prompt_full():
    adapter = ClaudeAdapter()
    ctx = {
        "project_name": "my_app",
        "project_path": "/home/user/my_app",
        "flutter_version": "3.22.0",
        "git_branch": "main",
    }
    result = adapter.build_context_prompt(ctx)
    assert "my_app" in result
    assert "3.22.0" in result
    assert "main" in result


def test_build_context_prompt_partial():
    adapter = GeminiAdapter()
    ctx = {"project_name": "app2"}
    result = adapter.build_context_prompt(ctx)
    assert "app2" in result
    assert "Flutter" not in result


# ── detect_adapters ───────────────────────────────────────────────────────────


def test_detect_adapters_all_missing():
    adapters = [ClaudeAdapter(), GeminiAdapter(), OpenCodeAdapter()]
    with patch("shutil.which", return_value=None):
        available = detect_adapters(adapters)
    assert available == []


def test_detect_adapters_one_present():
    adapters = [ClaudeAdapter(), GeminiAdapter(), OpenCodeAdapter()]

    def fake_which(name):
        return "/usr/bin/claude" if name == "claude" else None

    with patch("shutil.which", side_effect=fake_which):
        available = detect_adapters(adapters)
    assert len(available) == 1
    assert available[0].id == "claude"


def test_detect_adapters_all_present():
    adapters = [ClaudeAdapter(), GeminiAdapter(), OpenCodeAdapter()]
    with patch("shutil.which", return_value="/usr/bin/fake"):
        available = detect_adapters(adapters)
    assert len(available) == 3


def test_binary_on_path_false():
    with patch("shutil.which", return_value=None):
        assert binary_on_path("nonexistent_tool_xyz") is False


def test_binary_on_path_true():
    with patch("shutil.which", return_value="/usr/bin/tool"):
        assert binary_on_path("tool") is True


# ── ClaudeAdapter ─────────────────────────────────────────────────────────────


def test_claude_adapter_properties():
    a = ClaudeAdapter()
    assert a.id == "claude"
    assert a.name == "Claude Code"
    assert a.icon


def test_claude_start_session_no_context():
    a = ClaudeAdapter()
    s = a.start_session()
    assert s.adapter_id == "claude"
    assert s.active is True
    assert s.messages == []


def test_claude_start_session_with_context():
    a = ClaudeAdapter()
    ctx = {"project_name": "test_app", "flutter_version": "3.22.0"}
    s = a.start_session(ctx)
    assert s.active is True
    assert len(s.messages) == 1
    assert s.messages[0].role == "system"
    assert "test_app" in s.messages[0].content


def test_claude_stop_session():
    a = ClaudeAdapter()
    s = a.start_session()
    assert s.active is True
    a.stop_session(s)
    assert s.active is False


def test_claude_send_binary_not_found():
    a = ClaudeAdapter()
    s = a.start_session()
    chunks: list[str] = []
    done_called = []

    with patch("subprocess.Popen", side_effect=FileNotFoundError):
        a.send(s, "hello", on_chunk=chunks.append, on_done=lambda: done_called.append(1))

    assert any("error" in c for c in chunks)
    assert done_called == [1]


def test_claude_send_adds_messages():
    a = ClaudeAdapter()
    s = a.start_session()

    mock_proc = MagicMock()
    mock_proc.stdout = iter(["line1\n", "line2\n"])
    mock_proc.wait.return_value = 0

    with patch("subprocess.Popen", return_value=mock_proc):
        chunks: list[str] = []
        a.send(s, "hello", on_chunk=chunks.append)

    # user + assistant messages appended
    roles = [m.role for m in s.messages]
    assert "user" in roles
    assert "assistant" in roles


# ── GeminiAdapter ─────────────────────────────────────────────────────────────


def test_gemini_adapter_properties():
    a = GeminiAdapter()
    assert a.id == "gemini"
    assert a.name == "Gemini CLI"
    assert a.icon


def test_gemini_start_session():
    a = GeminiAdapter()
    s = a.start_session()
    assert s.adapter_id == "gemini"
    assert s.active is True


def test_gemini_send_binary_not_found():
    a = GeminiAdapter()
    s = a.start_session()
    chunks: list[str] = []
    with patch("subprocess.Popen", side_effect=FileNotFoundError):
        a.send(s, "test", on_chunk=chunks.append)
    assert any("error" in c for c in chunks)


# ── OpenCodeAdapter ───────────────────────────────────────────────────────────


def test_opencode_adapter_properties():
    a = OpenCodeAdapter()
    assert a.id == "opencode"
    assert a.name == "OpenCode"
    assert a.icon


def test_opencode_start_session():
    a = OpenCodeAdapter()
    s = a.start_session()
    assert s.adapter_id == "opencode"
    assert s.active is True


def test_opencode_send_binary_not_found():
    a = OpenCodeAdapter()
    s = a.start_session()
    chunks: list[str] = []
    with patch("subprocess.Popen", side_effect=FileNotFoundError):
        a.send(s, "test", on_chunk=chunks.append)
    assert any("error" in c for c in chunks)


# ── session_store ─────────────────────────────────────────────────────────────


def test_save_and_load_sessions(tmp_path):
    path = str(tmp_path / "sessions.json")
    s = AdapterSession(
        adapter_id="claude",
        session_id="sess-1",
        active=True,
        context={"project_name": "app"},
        messages=[
            AdapterMessage("user", "hello", timestamp=1000.0),
            AdapterMessage("assistant", "world", timestamp=1001.0),
        ],
    )
    assert save_sessions([s], path) is True

    loaded = load_sessions(path)
    assert len(loaded) == 1
    assert loaded[0].adapter_id == "claude"
    assert loaded[0].session_id == "sess-1"
    assert loaded[0].active is False   # never restored as active
    assert loaded[0].context == {"project_name": "app"}
    assert len(loaded[0].messages) == 2
    assert loaded[0].messages[0].content == "hello"


def test_load_sessions_missing_file(tmp_path):
    sessions = load_sessions(str(tmp_path / "nonexistent.json"))
    assert sessions == []


def test_save_sessions_invalid_path():
    result = save_sessions([], "/no_such_dir_xyz/sessions.json")
    assert result is False


def test_get_history_for_adapter():
    sessions = [
        AdapterSession(
            "claude", "s1",
            messages=[AdapterMessage("user", "hi", timestamp=100.0)]
        ),
        AdapterSession(
            "gemini", "s2",
            messages=[AdapterMessage("user", "hello", timestamp=200.0)]
        ),
        AdapterSession(
            "claude", "s3",
            messages=[AdapterMessage("user", "hey", timestamp=300.0)]
        ),
    ]
    result = get_history_for_adapter(sessions, "claude")
    assert len(result) == 2
    assert result[0].session_id == "s3"   # most recent first
    assert result[1].session_id == "s1"


def test_get_history_for_adapter_limit():
    sessions = [
        AdapterSession("claude", f"s{i}", messages=[AdapterMessage("user", "x", timestamp=float(i))])
        for i in range(30)
    ]
    result = get_history_for_adapter(sessions, "claude", limit=5)
    assert len(result) == 5


def test_get_history_for_adapter_empty():
    result = get_history_for_adapter([], "claude")
    assert result == []


def test_get_history_for_adapter_no_match():
    sessions = [AdapterSession("gemini", "s1")]
    result = get_history_for_adapter(sessions, "claude")
    assert result == []


def test_save_sessions_multiple(tmp_path):
    path = str(tmp_path / "multi.json")
    sessions = [
        AdapterSession("claude", "s1", messages=[AdapterMessage("user", "a", timestamp=1.0)]),
        AdapterSession("gemini", "s2", messages=[AdapterMessage("user", "b", timestamp=2.0)]),
    ]
    save_sessions(sessions, path)
    loaded = load_sessions(path)
    assert len(loaded) == 2
    ids = {s.adapter_id for s in loaded}
    assert ids == {"claude", "gemini"}


# ── CLIAdapterPlugin ──────────────────────────────────────────────────────────


def test_plugin_id():
    p = CLIAdapterPlugin()
    assert p.id == "cli"


def test_plugin_name():
    p = CLIAdapterPlugin()
    assert p.name == "CLI Adapters"


def test_plugin_commands():
    p = CLIAdapterPlugin()
    cmds = p.commands()
    assert isinstance(cmds, list)
    assert all(isinstance(c, dict) for c in cmds)
    assert all(c["plugin_id"] == "cli" for c in cmds)


def test_plugin_handle_command_new():
    p = CLIAdapterPlugin()
    # No widget mounted, but should return True without crashing
    assert p.handle_command("new") is True
    assert p.handle_command("new session") is True


def test_plugin_handle_command_history():
    p = CLIAdapterPlugin()
    assert p.handle_command("history") is True


def test_plugin_handle_command_clear():
    p = CLIAdapterPlugin()
    assert p.handle_command("clear") is True


def test_plugin_handle_command_switch():
    p = CLIAdapterPlugin()
    assert p.handle_command("switch claude") is True
    assert p.handle_command("switch gemini") is True


def test_plugin_handle_command_ask():
    p = CLIAdapterPlugin()
    assert p.handle_command("ask what is flutter?") is True


def test_plugin_handle_command_unknown():
    p = CLIAdapterPlugin()
    assert p.handle_command("foobar") is False
