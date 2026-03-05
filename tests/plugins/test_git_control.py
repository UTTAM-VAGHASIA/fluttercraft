from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.plugins.git_control.git_api import (
    GitBranch,
    GitCommit,
    GitFile,
    GitStash,
    colorize_diff_line,
    esc,
    get_ahead_behind,
    get_branches,
    get_current_branch,
    get_diff,
    get_log,
    get_stashes,
    get_status,
    is_git_installed,
    is_git_repo,
)
from fluttercraft.plugins.git_control.plugin import GitControlPlugin
from fluttercraft.plugins.base import PluginContext


# ── esc() ─────────────────────────────────────────────────────────────────────


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

    def test_empty_string(self):
        assert esc("") == ""


# ── is_git_installed() ────────────────────────────────────────────────────────


class TestIsGitInstalled:
    def test_returns_true_when_git_on_path(self):
        with patch("shutil.which", return_value="/usr/bin/git"):
            assert is_git_installed() is True

    def test_returns_false_when_git_missing(self):
        with patch("shutil.which", return_value=None):
            assert is_git_installed() is False


# ── is_git_repo() ─────────────────────────────────────────────────────────────


class TestIsGitRepo:
    def test_returns_true_when_inside_repo(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert is_git_repo("/some/repo") is True

    def test_returns_false_when_not_a_repo(self):
        mock_result = MagicMock()
        mock_result.returncode = 128
        with patch("subprocess.run", return_value=mock_result):
            assert is_git_repo("/tmp/not-a-repo") is False

    def test_returns_false_on_exception(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert is_git_repo() is False


# ── get_current_branch() ──────────────────────────────────────────────────────


class TestGetCurrentBranch:
    def test_returns_branch_name(self):
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        with patch("subprocess.run", return_value=mock_result):
            assert get_current_branch() == "main"

    def test_returns_none_when_empty(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            assert get_current_branch() is None

    def test_returns_none_on_exception(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert get_current_branch() is None

    def test_strips_whitespace(self):
        mock_result = MagicMock()
        mock_result.stdout = "  feature/my-branch  \n"
        with patch("subprocess.run", return_value=mock_result):
            assert get_current_branch() == "feature/my-branch"


# ── get_ahead_behind() ────────────────────────────────────────────────────────


class TestGetAheadBehind:
    def test_parses_ahead_and_behind(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "2\t1\n"
        with patch("subprocess.run", return_value=mock_result):
            ahead, behind = get_ahead_behind()
        assert ahead == 2
        assert behind == 1

    def test_returns_zeros_on_no_upstream(self):
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            assert get_ahead_behind() == (0, 0)

    def test_returns_zeros_on_exception(self):
        with patch("subprocess.run", side_effect=Exception):
            assert get_ahead_behind() == (0, 0)


# ── get_status() ──────────────────────────────────────────────────────────────


class TestGetStatus:
    def test_parses_modified_staged_file(self):
        mock_result = MagicMock()
        mock_result.stdout = "M  fluttercraft/app.py"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert len(files) == 1
        assert files[0].path == "fluttercraft/app.py"
        assert files[0].index_status == "M"
        assert files[0].work_tree_status == " "
        assert files[0].is_staged is True
        assert files[0].is_untracked is False

    def test_parses_untracked_file(self):
        mock_result = MagicMock()
        mock_result.stdout = "?? test_bare.py"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert len(files) == 1
        assert files[0].is_untracked is True
        assert files[0].is_staged is False

    def test_parses_added_file(self):
        mock_result = MagicMock()
        mock_result.stdout = "A  new_file.py"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert files[0].index_status == "A"
        assert files[0].is_staged is True

    def test_parses_unstaged_modified(self):
        mock_result = MagicMock()
        mock_result.stdout = " M CLAUDE.md"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert files[0].work_tree_status == "M"
        assert files[0].is_staged is False
        assert files[0].is_unstaged is True

    def test_handles_renamed_file(self):
        mock_result = MagicMock()
        mock_result.stdout = "R  old_name.py -> new_name.py"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert files[0].path == "new_name.py"

    def test_returns_empty_on_clean_tree(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_status() == []

    def test_parses_multiple_files(self):
        mock_result = MagicMock()
        mock_result.stdout = "M  file1.py\n?? file2.py\n M file3.py"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            files = get_status()
        assert len(files) == 3


# ── GitFile properties ────────────────────────────────────────────────────────


class TestGitFileProperties:
    def test_staged_file(self):
        f = GitFile(path="app.py", index_status="M", work_tree_status=" ")
        assert f.is_staged is True
        assert f.is_unstaged is False
        assert f.is_untracked is False

    def test_unstaged_file(self):
        f = GitFile(path="app.py", index_status=" ", work_tree_status="M")
        assert f.is_staged is False
        assert f.is_unstaged is True
        assert f.is_untracked is False

    def test_untracked_file(self):
        f = GitFile(path="test.py", index_status="?", work_tree_status="?")
        assert f.is_untracked is True
        assert f.is_staged is False

    def test_both_staged_and_unstaged(self):
        f = GitFile(path="file.py", index_status="M", work_tree_status="M")
        assert f.is_staged is True
        assert f.is_unstaged is True
        assert f.is_untracked is False


# ── get_diff() ────────────────────────────────────────────────────────────────


class TestGetDiff:
    def test_returns_diff_output(self):
        mock_result = MagicMock()
        mock_result.stdout = "diff --git a/file.py b/file.py\n+added line\n-removed line"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            output = get_diff()
        assert "+added line" in output
        assert "-removed line" in output

    def test_returns_placeholder_when_empty(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_diff() == "(no changes)"

    def test_staged_placeholder_when_empty(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_diff(staged=True) == "(no staged changes)"


# ── get_branches() ────────────────────────────────────────────────────────────


class TestGetBranches:
    def test_parses_current_branch(self):
        mock_result = MagicMock()
        mock_result.stdout = "*|main\n |feature/test"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            branches = get_branches()
        assert len(branches) == 2
        current = [b for b in branches if b.is_current]
        assert len(current) == 1
        assert current[0].name == "main"

    def test_returns_empty_when_no_branches(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_branches() == []

    def test_gitbranch_dataclass(self):
        b = GitBranch(name="main", is_current=True)
        assert b.name == "main"
        assert b.is_current is True


# ── get_log() ─────────────────────────────────────────────────────────────────


class TestGetLog:
    def test_parses_log_entries(self):
        mock_result = MagicMock()
        mock_result.stdout = "abc1234|Alice|2 hours ago|feat: add feature\ndef5678|Bob|1 day ago|fix: crash"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            commits = get_log()
        assert len(commits) == 2
        assert commits[0].short_hash == "abc1234"
        assert commits[0].author == "Alice"
        assert commits[0].message == "feat: add feature"

    def test_returns_empty_on_no_commits(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_log() == []

    def test_gitcommit_dataclass(self):
        c = GitCommit(short_hash="abc", author="Alice", date="1h ago", message="fix: bug")
        assert c.short_hash == "abc"
        assert c.message == "fix: bug"


# ── get_stashes() ─────────────────────────────────────────────────────────────


class TestGetStashes:
    def test_parses_stash_entries(self):
        mock_result = MagicMock()
        mock_result.stdout = "stash@{0}|WIP on main: my stash\nstash@{1}|WIP on main: old stash"
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            stashes = get_stashes()
        assert len(stashes) == 2
        assert stashes[0].ref == "stash@{0}"
        assert stashes[0].message == "WIP on main: my stash"
        assert stashes[0].index == 0
        assert stashes[1].index == 1

    def test_returns_empty_when_no_stashes(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert get_stashes() == []

    def test_gitstash_dataclass(self):
        s = GitStash(index=0, ref="stash@{0}", message="WIP")
        assert s.index == 0
        assert s.ref == "stash@{0}"


# ── colorize_diff_line() ──────────────────────────────────────────────────────


class TestColorizeDiffLine:
    def test_added_line_is_green(self):
        result = colorize_diff_line("+    new line")
        assert "#9ece6a" in result

    def test_removed_line_is_red(self):
        result = colorize_diff_line("-    old line")
        assert "#f7768e" in result

    def test_file_header_is_yellow(self):
        result = colorize_diff_line("+++ b/file.py")
        assert "#e0af68" in result

    def test_old_file_header_is_yellow(self):
        result = colorize_diff_line("--- a/file.py")
        assert "#e0af68" in result

    def test_hunk_header_is_cyan(self):
        result = colorize_diff_line("@@ -1,3 +1,4 @@ def foo():")
        assert "#7dcfff" in result

    def test_diff_meta_is_dim(self):
        result = colorize_diff_line("diff --git a/file.py b/file.py")
        assert "#565f89" in result

    def test_context_line_is_default(self):
        result = colorize_diff_line("    context line")
        assert "#a9b1d6" in result


# ── GitControlPlugin ──────────────────────────────────────────────────────────


class TestGitControlPlugin:
    def _make_plugin(self) -> GitControlPlugin:
        plugin = GitControlPlugin()
        ctx = PluginContext(
            work_dir="",
            project_root="",
            config=MagicMock(),
            event_bus=MagicMock(),
            state=MagicMock(),
        )
        plugin.init(ctx)
        return plugin

    def test_plugin_id_is_git(self):
        assert GitControlPlugin().id == "git"

    def test_plugin_name(self):
        assert GitControlPlugin().name == "Git Control"

    def test_plugin_icon(self):
        assert GitControlPlugin().icon == "⎇"

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

    def test_commands_have_git_prefix(self):
        plugin = self._make_plugin()
        cmds = plugin.commands()
        for cmd in cmds:
            assert cmd["title"].startswith("Git:")

    def test_handle_command_ignores_non_git(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("flutter doctor") is False
        assert plugin.handle_command("fvm list") is False
        assert plugin.handle_command("status") is False

    def test_handle_command_git_no_subcommand(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("git") is False

    def test_handle_command_returns_false_without_widget(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("git status") is True  # routes even without widget

    def test_handle_command_git_status(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git status") is True
        mock_widget.trigger_refresh.assert_called_once()

    def test_handle_command_git_push(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git push") is True
        mock_widget.trigger_push.assert_called_once()

    def test_handle_command_git_pull(self):
        # handle_command("git pull") bypasses the modal and calls _worker_pull directly
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git pull") is True
        mock_widget._worker_pull.assert_called_once_with(False)

    def test_handle_command_git_fetch(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git fetch") is True
        mock_widget.trigger_fetch.assert_called_once()

    def test_handle_command_git_log(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git log") is True
        mock_widget.trigger_log.assert_called_once()

    def test_handle_command_git_stash(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git stash") is True
        mock_widget.trigger_stash.assert_called_once()

    def test_handle_command_git_stash_pop(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git stash pop") is True
        mock_widget.trigger_stash_pop.assert_called_once()

    def test_handle_command_git_stash_list(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git stash list") is True
        mock_widget.trigger_stashes.assert_called_once()

    def test_handle_command_git_branch_shows_list(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git branch") is True
        mock_widget.trigger_branches.assert_called_once()

    def test_handle_command_git_checkout_switches_branch(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git checkout feature/test") is True
        mock_widget.trigger_switch_branch.assert_called_once_with("feature/test")

    def test_handle_command_git_add_dot_stages_all(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git add .") is True
        mock_widget.trigger_stage_all.assert_called_once()

    def test_handle_command_git_add_uppercase_a(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git add -A") is True
        mock_widget.trigger_stage_all.assert_called_once()

    def test_handle_command_git_diff(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git diff") is True
        mock_widget.trigger_diff.assert_called_once_with(None)

    def test_handle_command_unknown_subcommand_returns_false(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        assert plugin.handle_command("git unknowncmd") is False
