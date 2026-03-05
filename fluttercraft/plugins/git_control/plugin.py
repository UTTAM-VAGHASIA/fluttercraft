from __future__ import annotations

from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, RichLog, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.git_control.git_api import (
    GitBranch,
    GitCommit,
    GitFile,
    GitStash,
    colorize_diff_line,
    commit,
    create_branch,
    delete_branch,
    esc,
    fetch,
    get_ahead_behind,
    get_branches,
    get_current_branch,
    get_diff,
    get_log,
    get_stashes,
    get_status,
    is_git_repo,
    merge_branch,
    pull,
    push,
    stage_all,
    stage_file,
    stash_drop,
    stash_pop,
    stash_push,
    switch_branch,
    unstage_file,
)


# ── Commit modal ──────────────────────────────────────────────────────────────


class _CommitModal(ModalScreen):
    """Commit message input modal. Dismissed with ``(message, amend)`` or ``None``."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False, priority=True)]

    DEFAULT_CSS = """
    _CommitModal {
        align: center middle;
    }
    _CommitModal > Vertical {
        width: 64;
        height: auto;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 1 2;
    }
    #commit-title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        padding-bottom: 1;
        width: 1fr;
    }
    .commit-hint {
        color: #565f89;
        margin-bottom: 1;
        width: 1fr;
    }
    #commit-input {
        margin-bottom: 1;
    }
    #commit-buttons {
        height: auto;
        align-horizontal: center;
    }
    #commit-buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, amend: bool = False) -> None:
        super().__init__()
        self._amend = amend

    def compose(self) -> ComposeResult:
        title = "Amend Commit" if self._amend else "Create Commit"
        with Vertical():
            yield Static(title, id="commit-title")
            yield Static(
                "[dim]Examples: feat: add feature  ·  fix: crash  ·  refactor: cleanup[/]",
                classes="commit-hint",
            )
            yield Input(placeholder="conventional commit message...", id="commit-input")
            with Center(id="commit-buttons"):
                yield Button("Commit", variant="primary", id="btn-commit")
                if not self._amend:
                    yield Button("Amend", id="btn-amend")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#commit-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        msg = event.value.strip()
        if msg:
            self.dismiss((msg, self._amend))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = str(event.button.id)
        if btn_id == "btn-commit":
            msg = self.query_one("#commit-input", Input).value.strip()
            if msg:
                self.dismiss((msg, False))
        elif btn_id == "btn-amend":
            msg = self.query_one("#commit-input", Input).value.strip()
            if msg:
                self.dismiss((msg, True))
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Create branch modal ───────────────────────────────────────────────────────


class _CreateBranchModal(ModalScreen):
    """Input modal for creating a new branch. Dismissed with branch name or ``None``."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False, priority=True)]

    DEFAULT_CSS = """
    _CreateBranchModal {
        align: center middle;
    }
    _CreateBranchModal > Vertical {
        width: 54;
        height: auto;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 1 2;
    }
    #branch-title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        padding-bottom: 1;
        width: 1fr;
    }
    .branch-hint {
        color: #565f89;
        margin-bottom: 1;
        width: 1fr;
    }
    #branch-input {
        margin-bottom: 1;
    }
    #branch-buttons {
        height: auto;
        align-horizontal: center;
    }
    #branch-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Create New Branch", id="branch-title")
            yield Static(
                "[dim]Example: feature/new-screen  ·  fix/crash-login[/]",
                classes="branch-hint",
            )
            yield Input(placeholder="branch-name", id="branch-input")
            with Center(id="branch-buttons"):
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#branch-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if name:
            self.dismiss(name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.id) == "btn-create":
            name = self.query_one("#branch-input", Input).value.strip()
            if name:
                self.dismiss(name)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Stash modal ───────────────────────────────────────────────────────────────


class _StashModal(ModalScreen):
    """Optional stash message input. Dismissed with message string (may be empty) or ``None``."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False, priority=True)]

    DEFAULT_CSS = """
    _StashModal {
        align: center middle;
    }
    _StashModal > Vertical {
        width: 54;
        height: auto;
        background: #1f2335;
        border: round #7aa2f7;
        padding: 1 2;
    }
    #stash-title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        padding-bottom: 1;
        width: 1fr;
    }
    .stash-hint {
        color: #565f89;
        margin-bottom: 1;
        width: 1fr;
    }
    #stash-input {
        margin-bottom: 1;
    }
    #stash-buttons {
        height: auto;
        align-horizontal: center;
    }
    #stash-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Stash Changes", id="stash-title")
            yield Static(
                "[dim]Leave empty for a default stash message[/]",
                classes="stash-hint",
            )
            yield Input(placeholder="stash message (optional)...", id="stash-input")
            with Center(id="stash-buttons"):
                yield Button("Stash", variant="primary", id="btn-stash")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#stash-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if str(event.button.id) == "btn-stash":
            self.dismiss(self.query_one("#stash-input", Input).value.strip())
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Git Control widget ────────────────────────────────────────────────────────


class GitControlWidget(Widget):
    """Git Control plugin panel.

    Layout::

        ┌─ status bar ─────────────────────────────────────────────────────────┐
        │ ⎇ main  ↑2 ↓0  S:2  U:1  ?:3                                        │
        ├─ left (36) ────────────────┬─ right (1fr) ───────────────────────────┤
        │ ● Staged (2)               │  diff / log / branches / stashes        │
        │  ▶ M  fluttercraft/app.py  │                                          │
        │    A  new_file.py          │                                          │
        │ ─ Unstaged (1)             │                                          │
        │    M  CLAUDE.md            │                                          │
        │ ? Untracked (3)            │                                          │
        │    test_bare.py            │                                          │
        ├─ actions ──────────────────┤                                          │
        │ s stage  a all  u unstage  │                                          │
        │ c commit p push P pull     │                                          │
        │ f fetch  b branch n new    │                                          │
        │ l log    z stash r refresh │                                          │
        └────────────────────────────┴──────────────────────────────────────────┘

    Keyboard shortcuts:
        r — refresh              s — stage selected       a — stage all
        u — unstage selected     c — commit (modal)       p — push
        P — pull                 f — fetch                b — show branches
        n — new branch (modal)   l — show log             z — stash (modal)
        Z — stash pop            ↑/↓ — navigate file list
    """

    can_focus = True

    DEFAULT_CSS = """
    GitControlWidget {
        height: 1fr;
        layout: vertical;
    }
    #git-status-bar {
        height: 1;
        background: #16161e;
        color: #7aa2f7;
        padding: 0 1;
        border-bottom: solid #3b4261;
    }
    #git-body {
        height: 1fr;
    }
    #git-left {
        width: 36;
        background: #1f2335;
        border-right: solid #3b4261;
    }
    #git-file-list {
        height: 1fr;
        background: #1f2335;
        padding: 1 1;
    }
    #git-actions {
        height: auto;
        color: #565f89;
        padding: 0 1 1 1;
        border-top: solid #3b4261;
    }
    #git-right {
        height: 1fr;
        background: #16161e;
    }
    #git-diff {
        height: 1fr;
        background: #16161e;
        color: #a9b1d6;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("r",    "refresh",    "Refresh",    show=True),
        Binding("s",    "stage",      "Stage",      show=True),
        Binding("a",    "stage_all",  "Stage All",  show=True),
        Binding("u",    "unstage",    "Unstage",    show=True),
        Binding("c",    "do_commit",  "Commit",     show=True),
        Binding("p",    "do_push",    "Push",       show=True),
        Binding("P",    "do_pull",    "Pull",       show=True),
        Binding("f",    "do_fetch",   "Fetch",      show=True),
        Binding("b",    "branches",   "Branches",   show=True),
        Binding("n",    "new_branch", "New Branch", show=False),
        Binding("l",    "do_log",     "Log",        show=True),
        Binding("z",    "do_stash",   "Stash",      show=True),
        Binding("Z",    "stash_pop",  "Stash Pop",  show=False),
        Binding("up",   "cursor_up",  "Up",         show=False, priority=True),
        Binding("down", "cursor_down","Down",        show=False, priority=True),
    ]

    def __init__(self, project_root: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._project_root = project_root or None
        self._all_files: list[GitFile] = []
        self._cursor: int = 0
        self._observer: Any = None

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="git-status-bar")
        with Horizontal(id="git-body"):
            with Vertical(id="git-left"):
                yield Static("", id="git-file-list")
                yield Static(
                    "[dim]s[/] stage   [dim]a[/] stage-all  [dim]u[/] unstage\n"
                    "[dim]c[/] commit  [dim]p[/] push       [dim]P[/] pull\n"
                    "[dim]f[/] fetch   [dim]b[/] branches   [dim]n[/] new branch\n"
                    "[dim]l[/] log     [dim]z[/] stash      [dim]r[/] refresh",
                    id="git-actions",
                )
            with Vertical(id="git-right"):
                yield RichLog(id="git-diff", markup=True, highlight=False, wrap=True)

    def on_mount(self) -> None:
        self._check_repo_and_load()
        self._start_file_watcher()
        self.set_interval(10.0, self._auto_refresh)

    def on_unmount(self) -> None:
        self._stop_file_watcher()

    # ── Initial load ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _check_repo_and_load(self) -> None:
        repo_ok = is_git_repo(self._project_root)
        self.app.call_from_thread(self._apply_repo_check, repo_ok)
        if repo_ok:
            self._worker_load_status()

    def _apply_repo_check(self, repo_ok: bool) -> None:
        if not repo_ok:
            self.query_one("#git-status-bar", Static).update(
                "[#f7768e]✗[/] Not a git repository  "
                "[dim #565f89]— start from a git project directory[/]"
            )
            self._log("[#f7768e]Not inside a git repository.[/]")
            self._log("")
            self._log("[dim]Initialize with:[/]")
            self._log("  [#7aa2f7]git init[/]")

    # ── Status loading ────────────────────────────────────────────────────────

    @work(thread=True)
    def _worker_load_status(self) -> None:
        branch = get_current_branch(self._project_root)
        ahead, behind = get_ahead_behind(self._project_root)
        files = get_status(self._project_root)
        self.app.call_from_thread(self._apply_status, branch, ahead, behind, files)

    def _apply_status(
        self,
        branch: str | None,
        ahead: int,
        behind: int,
        files: list[GitFile],
    ) -> None:
        # Build status bar
        branch_str = esc(branch) if branch else "(detached)"
        bar = f"[bold #7aa2f7]⎇ {branch_str}[/]"
        if ahead > 0:
            bar += f"  [#9ece6a]↑{ahead}[/]"
        if behind > 0:
            bar += f"  [#f7768e]↓{behind}[/]"

        staged_count = sum(1 for f in files if f.is_staged)
        unstaged_count = sum(1 for f in files if not f.is_staged and f.is_unstaged)
        untracked_count = sum(1 for f in files if f.is_untracked)
        bar += (
            f"  [dim #565f89]S:{staged_count} U:{unstaged_count} ?:{untracked_count}[/]"
            f"  [dim #3b4261]s stage · a all · c commit · p push · b branch[/]"
        )
        self.query_one("#git-status-bar", Static).update(bar)

        # Rebuild ordered flat file list: staged → unstaged → untracked
        self._all_files = (
            [f for f in files if f.is_staged]
            + [f for f in files if not f.is_staged and f.is_unstaged]
            + [f for f in files if f.is_untracked]
        )

        # Clamp cursor
        if self._cursor >= len(self._all_files):
            self._cursor = max(0, len(self._all_files) - 1)

        self._render_file_list()
        self._render_diff_for_cursor()

    # ── File list rendering ───────────────────────────────────────────────────

    def _render_file_list(self) -> None:
        staged = [f for f in self._all_files if f.is_staged]
        unstaged = [f for f in self._all_files if not f.is_staged and f.is_unstaged]
        untracked = [f for f in self._all_files if f.is_untracked]

        lines: list[str] = []
        flat_idx = 0

        if staged:
            lines.append(f"[bold #9ece6a]● Staged ({len(staged)})[/]")
            for f in staged:
                cursor = " [bold #7aa2f7]▶[/] " if flat_idx == self._cursor else "   "
                s_col = "#9ece6a" if f.index_status == "A" else "#a9b1d6"
                path = esc(f.path)
                if len(f.path) > 26:
                    path = "…" + esc(f.path[-25:])
                lines.append(f"{cursor}[{s_col}]{esc(f.index_status)}[/] [{s_col}]{path}[/]")
                flat_idx += 1

        if unstaged:
            lines.append(f"[bold #e0af68]─ Unstaged ({len(unstaged)})[/]")
            for f in unstaged:
                cursor = " [bold #7aa2f7]▶[/] " if flat_idx == self._cursor else "   "
                path = esc(f.path)
                if len(f.path) > 26:
                    path = "…" + esc(f.path[-25:])
                lines.append(
                    f"{cursor}[#e0af68]{esc(f.work_tree_status)}[/] [#a9b1d6]{path}[/]"
                )
                flat_idx += 1

        if untracked:
            lines.append(f"[dim #565f89]? Untracked ({len(untracked)})[/]")
            for f in untracked:
                cursor = " [bold #7aa2f7]▶[/] " if flat_idx == self._cursor else "   "
                path = esc(f.path)
                if len(f.path) > 26:
                    path = "…" + esc(f.path[-25:])
                lines.append(f"{cursor}[dim #565f89]? {path}[/]")
                flat_idx += 1

        if not lines:
            lines = [
                "[dim #565f89]No changes[/]",
                "",
                "[dim #3b4261]Working tree is clean.[/]",
            ]

        self.query_one("#git-file-list", Static).update("\n".join(lines))

    # ── Diff rendering ────────────────────────────────────────────────────────

    def _render_diff_for_cursor(self) -> None:
        if not self._all_files or self._cursor >= len(self._all_files):
            self._clear_diff()
            return
        f = self._all_files[self._cursor]
        if f.is_untracked:
            self._clear_diff()
            self._log(f"[dim #565f89]{esc(f.path)} — untracked file (not in diff)[/]")
            return
        staged = f.is_staged
        self._worker_diff(f.path, staged)

    @work(thread=True)
    def _worker_diff(self, path: str, staged: bool) -> None:
        diff_output = get_diff(self._project_root, path=path, staged=staged)
        # If no staged diff, fall back to unstaged
        if staged and diff_output in ("(no staged changes)", "(no changes)", ""):
            diff_output = get_diff(self._project_root, path=path, staged=False)
        self.app.call_from_thread(self._show_diff, diff_output, path)

    def _show_diff(self, diff_output: str, path: str) -> None:
        self._clear_diff()
        self._log(f"[dim #565f89]── {esc(path)} ──[/]")
        if diff_output.startswith("("):
            self._log(f"[dim #565f89]{esc(diff_output)}[/]")
            return
        for line in diff_output.splitlines():
            self._log(colorize_diff_line(line))

    # ── Logging helpers ───────────────────────────────────────────────────────

    def _log(self, text: str) -> None:
        try:
            self.query_one("#git-diff", RichLog).write(text)
        except Exception:
            pass

    def _log_cmd(self, cmd: str) -> None:
        self._log(f"[#7aa2f7]$[/] [bold]{cmd}[/]")

    def _log_ok(self, text: str) -> None:
        self._log(f"[#9ece6a]▶[/] {text}")

    def _log_err(self, text: str) -> None:
        self._log(f"[#f7768e]✖[/] {text}")

    def _clear_diff(self) -> None:
        try:
            self.query_one("#git-diff", RichLog).clear()
        except Exception:
            pass

    # ── Cursor navigation ─────────────────────────────────────────────────────

    def action_cursor_up(self) -> None:
        if self._all_files:
            self._cursor = (self._cursor - 1) % len(self._all_files)
            self._render_file_list()
            self._render_diff_for_cursor()

    def action_cursor_down(self) -> None:
        if self._all_files:
            self._cursor = (self._cursor + 1) % len(self._all_files)
            self._render_file_list()
            self._render_diff_for_cursor()

    # ── Action: refresh ───────────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self._clear_diff()
        self._log_cmd("git status")
        self._worker_load_status()

    def _auto_refresh(self) -> None:
        """Called by interval timer and file watcher — silently refreshes."""
        try:
            self._worker_load_status()
        except Exception:
            pass

    # ── Action: stage ─────────────────────────────────────────────────────────

    def action_stage(self) -> None:
        if not self._all_files:
            self._log_err("No files to stage")
            return
        if self._cursor >= len(self._all_files):
            return
        f = self._all_files[self._cursor]
        if f.is_staged:
            self._log(f"[dim #565f89]{esc(f.path)} is already staged[/]")
            return
        self._clear_diff()
        self._log_cmd(f"git add -- {esc(f.path)}")
        self._worker_stage(f.path)

    @work(thread=True)
    def _worker_stage(self, path: str) -> None:
        ok, output = stage_file(self._project_root, path=path)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Staged {esc(path)}")
        else:
            self.app.call_from_thread(self._log_err, output or f"Failed to stage {esc(path)}")
        self._worker_load_status()

    # ── Action: stage all ─────────────────────────────────────────────────────

    def action_stage_all(self) -> None:
        self._clear_diff()
        self._log_cmd("git add -A")
        self._worker_stage_all()

    @work(thread=True)
    def _worker_stage_all(self) -> None:
        ok, output = stage_all(self._project_root)
        if ok:
            self.app.call_from_thread(self._log_ok, "Staged all changes")
        else:
            self.app.call_from_thread(self._log_err, output or "Failed to stage all")
        self._worker_load_status()

    # ── Action: unstage ───────────────────────────────────────────────────────

    def action_unstage(self) -> None:
        if not self._all_files:
            self._log_err("No files to unstage")
            return
        if self._cursor >= len(self._all_files):
            return
        f = self._all_files[self._cursor]
        if not f.is_staged:
            self._log(f"[dim #565f89]{esc(f.path)} is not staged[/]")
            return
        self._clear_diff()
        self._log_cmd(f"git restore --staged -- {esc(f.path)}")
        self._worker_unstage(f.path)

    @work(thread=True)
    def _worker_unstage(self, path: str) -> None:
        ok, output = unstage_file(self._project_root, path=path)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Unstaged {esc(path)}")
        else:
            self.app.call_from_thread(self._log_err, output or f"Failed to unstage {esc(path)}")
        self._worker_load_status()

    # ── Action: commit ────────────────────────────────────────────────────────

    def action_do_commit(self) -> None:
        """Open the commit modal."""
        self.app.push_screen(_CommitModal(amend=False), self._on_commit_result)

    def _on_commit_result(self, result: tuple[str, bool] | None) -> None:
        if not result:
            return
        message, amend = result
        self._clear_diff()
        action = "git commit --amend" if amend else "git commit"
        self._log_cmd(f'{action} -m "{esc(message)}"')
        self._worker_commit(message, amend)

    @work(thread=True)
    def _worker_commit(self, message: str, amend: bool) -> None:
        ok, output = commit(self._project_root, message=message, amend=amend)
        if ok:
            self.app.call_from_thread(self._log_ok, "Committed successfully")
            for line in output.splitlines():
                self.app.call_from_thread(self._log, esc(line))
        else:
            self.app.call_from_thread(self._log_err, output or "Commit failed")
        self._worker_load_status()

    # ── Action: push ──────────────────────────────────────────────────────────

    def action_do_push(self) -> None:
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Push to Remote")
            .section("Push current branch to remote?")
            .buttons("Push", "Cancel")
        )
        self.app.push_screen(modal, self._on_push_result)

    def _on_push_result(self, result: str | None) -> None:
        if result != "Push":
            return
        self._clear_diff()
        self._log_cmd("git push")
        self._log("[dim #565f89]Pushing… this may take a moment[/]")
        self._worker_push()

    @work(thread=True)
    def _worker_push(self) -> None:
        ok, output = push(self._project_root)
        if ok:
            self.app.call_from_thread(self._log_ok, "Pushed successfully")
        else:
            self.app.call_from_thread(self._log_err, output or "Push failed")
        for line in output.splitlines():
            self.app.call_from_thread(self._log, esc(line))

    # ── Action: pull ──────────────────────────────────────────────────────────

    def action_do_pull(self) -> None:
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Pull from Remote")
            .section("Pull changes from remote?")
            .section("[dim]Uses: git pull[/]")
            .buttons("Pull", "Pull --rebase", "Cancel")
        )
        self.app.push_screen(modal, self._on_pull_result)

    def _on_pull_result(self, result: str | None) -> None:
        if result not in ("Pull", "Pull --rebase"):
            return
        rebase = result == "Pull --rebase"
        self._clear_diff()
        cmd = "git pull --rebase" if rebase else "git pull"
        self._log_cmd(cmd)
        self._log("[dim #565f89]Pulling… this may take a moment[/]")
        self._worker_pull(rebase)

    @work(thread=True)
    def _worker_pull(self, rebase: bool) -> None:
        ok, output = pull(self._project_root, rebase=rebase)
        if ok:
            self.app.call_from_thread(self._log_ok, "Pull successful")
        else:
            self.app.call_from_thread(self._log_err, output or "Pull failed")
        for line in output.splitlines():
            self.app.call_from_thread(self._log, esc(line))
        self._worker_load_status()

    # ── Action: fetch ─────────────────────────────────────────────────────────

    def action_do_fetch(self) -> None:
        self._clear_diff()
        self._log_cmd("git fetch")
        self._log("[dim #565f89]Fetching…[/]")
        self._worker_fetch()

    @work(thread=True)
    def _worker_fetch(self) -> None:
        ok, output = fetch(self._project_root)
        if ok:
            self.app.call_from_thread(self._log_ok, "Fetch complete")
        else:
            self.app.call_from_thread(self._log_err, output or "Fetch failed")
        for line in output.splitlines():
            self.app.call_from_thread(self._log, esc(line))
        self._worker_load_status()

    # ── Action: branches ──────────────────────────────────────────────────────

    def action_branches(self) -> None:
        self._clear_diff()
        self._log_cmd("git branch")
        self._worker_branches()

    @work(thread=True)
    def _worker_branches(self) -> None:
        branches = get_branches(self._project_root)
        self.app.call_from_thread(self._show_branches, branches)

    def _show_branches(self, branches: list[GitBranch]) -> None:
        self._clear_diff()
        if not branches:
            self._log("[dim #565f89]No local branches found[/]")
            return
        self._log(f"[bold #7aa2f7]Local branches[/]  ({len(branches)} total)")
        self._log("")
        for b in branches:
            if b.is_current:
                self._log(f"  [bold #9ece6a]▶ {esc(b.name)}[/]  [dim #9ece6a](current)[/]")
            else:
                self._log(f"  [dim #565f89]○[/] [#a9b1d6]{esc(b.name)}[/]")
        self._log("")
        self._log("[dim]Press [bold]n[/] to create a branch[/]")

    # ── Action: new branch ────────────────────────────────────────────────────

    def action_new_branch(self) -> None:
        self.app.push_screen(_CreateBranchModal(), self._on_new_branch_result)

    def _on_new_branch_result(self, name: str | None) -> None:
        if not name:
            return
        self._clear_diff()
        self._log_cmd(f"git checkout -b {esc(name)}")
        self._worker_create_branch(name)

    @work(thread=True)
    def _worker_create_branch(self, name: str) -> None:
        ok, output = create_branch(self._project_root, name=name)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Created and switched to branch '{esc(name)}'")
        else:
            self.app.call_from_thread(self._log_err, output or f"Failed to create branch '{esc(name)}'")
        self._worker_load_status()

    # ── Action: log ───────────────────────────────────────────────────────────

    def action_do_log(self) -> None:
        self._clear_diff()
        self._log_cmd("git log --oneline -30")
        self._worker_log()

    @work(thread=True)
    def _worker_log(self) -> None:
        commits = get_log(self._project_root, limit=30)
        self.app.call_from_thread(self._show_log, commits)

    def _show_log(self, commits: list[GitCommit]) -> None:
        self._clear_diff()
        if not commits:
            self._log("[dim #565f89]No commits found[/]")
            return
        self._log(f"[bold #7aa2f7]Recent commits[/]  ({len(commits)} shown)")
        self._log("")
        for c in commits:
            hash_str = f"[#7aa2f7]{esc(c.short_hash)}[/]"
            date_str = f"[dim #565f89]{esc(c.date)}[/]"
            author_str = f"[dim #a9b1d6]{esc(c.author)}[/]"
            msg_str = f"[#c0caf5]{esc(c.message)}[/]"
            self._log(f"  {hash_str}  {msg_str}  {date_str}  {author_str}")

    # ── Action: stash ─────────────────────────────────────────────────────────

    def action_do_stash(self) -> None:
        self.app.push_screen(_StashModal(), self._on_stash_result)

    def _on_stash_result(self, message: str | None) -> None:
        if message is None:  # user cancelled
            return
        self._clear_diff()
        cmd = f"git stash push -m {esc(message)}" if message else "git stash push"
        self._log_cmd(cmd)
        self._worker_stash_push(message)

    @work(thread=True)
    def _worker_stash_push(self, message: str) -> None:
        ok, output = stash_push(self._project_root, message=message)
        if ok:
            self.app.call_from_thread(self._log_ok, "Stashed changes")
            self.app.call_from_thread(self._show_stash_list_after_push)
        else:
            self.app.call_from_thread(self._log_err, output or "Stash failed")
        self._worker_load_status()

    def _show_stash_list_after_push(self) -> None:
        self._log("")
        self._log("[dim]Press [bold]Z[/] to pop the stash[/]")

    # ── Action: stash pop ─────────────────────────────────────────────────────

    def action_stash_pop(self) -> None:
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Pop Stash")
            .section("Apply and remove the most recent stash?")
            .buttons("Pop", "Cancel")
        )
        self.app.push_screen(modal, self._on_stash_pop_result)

    def _on_stash_pop_result(self, result: str | None) -> None:
        if result != "Pop":
            return
        self._clear_diff()
        self._log_cmd("git stash pop")
        self._worker_stash_pop()

    @work(thread=True)
    def _worker_stash_pop(self) -> None:
        ok, output = stash_pop(self._project_root)
        if ok:
            self.app.call_from_thread(self._log_ok, "Stash applied and removed")
        else:
            self.app.call_from_thread(self._log_err, output or "Stash pop failed")
        for line in output.splitlines():
            self.app.call_from_thread(self._log, esc(line))
        self._worker_load_status()

    # ── File watcher (5.10) ───────────────────────────────────────────────────

    def _start_file_watcher(self) -> None:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            widget_ref = self

            class _Handler(FileSystemEventHandler):
                def on_any_event(self, event) -> None:  # type: ignore[override]
                    # Ignore changes inside .git itself to avoid loops
                    path = getattr(event, "src_path", "")
                    if ".git" in path:
                        return
                    try:
                        widget_ref.app.call_from_thread(widget_ref._auto_refresh)
                    except Exception:
                        pass

            watch_path = self._project_root or "."
            self._observer = Observer()
            self._observer.schedule(_Handler(), path=watch_path, recursive=True)
            self._observer.start()
        except Exception:
            self._observer = None

    def _stop_file_watcher(self) -> None:
        try:
            if self._observer is not None:
                self._observer.stop()
                self._observer.join(timeout=2)
        except Exception:
            pass

    # ── Public trigger API (called by plugin handle_command) ──────────────────

    def trigger_refresh(self) -> None:
        self.action_refresh()

    def trigger_stage_all(self) -> None:
        self.action_stage_all()

    def trigger_log(self) -> None:
        self.action_do_log()

    def trigger_branches(self) -> None:
        self.action_branches()

    def trigger_push(self) -> None:
        self.action_do_push()

    def trigger_pull(self) -> None:
        self.action_do_pull()

    def trigger_fetch(self) -> None:
        self.action_do_fetch()

    def trigger_stash(self) -> None:
        self.action_do_stash()

    def trigger_stash_pop(self) -> None:
        self.action_stash_pop()

    def trigger_commit(self) -> None:
        self.action_do_commit()

    def trigger_new_branch(self) -> None:
        self.action_new_branch()

    def trigger_switch_branch(self, name: str) -> None:
        self._clear_diff()
        self._log_cmd(f"git checkout {esc(name)}")
        self._worker_switch_branch(name)

    @work(thread=True)
    def _worker_switch_branch(self, name: str) -> None:
        ok, output = switch_branch(self._project_root, name=name)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Switched to branch '{esc(name)}'")
        else:
            self.app.call_from_thread(self._log_err, output or f"Failed to switch to '{esc(name)}'")
        self._worker_load_status()

    def trigger_delete_branch(self, name: str) -> None:
        from fluttercraft.widgets.modal import CraftModal

        modal = (
            CraftModal.build("Delete Branch")
            .section(f"Delete branch [bold]{esc(name)}[/]?")
            .section("[dim]Runs: git branch -d (safe delete)[/]")
            .buttons("Delete", "Cancel")
        )
        self.app.push_screen(
            modal, lambda r: self._on_delete_branch(r, name)
        )

    def _on_delete_branch(self, result: str | None, name: str) -> None:
        if result != "Delete":
            return
        self._clear_diff()
        self._log_cmd(f"git branch -d {esc(name)}")
        self._worker_delete_branch(name)

    @work(thread=True)
    def _worker_delete_branch(self, name: str) -> None:
        ok, output = delete_branch(self._project_root, name=name)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Deleted branch '{esc(name)}'")
        else:
            self.app.call_from_thread(self._log_err, output or f"Failed to delete '{esc(name)}'")
        self._worker_load_status()

    @work(thread=True)
    def _worker_merge_branch(self, name: str) -> None:
        ok, output = merge_branch(self._project_root, name=name)
        if ok:
            self.app.call_from_thread(self._log_ok, f"Merged '{esc(name)}' into current branch")
        else:
            self.app.call_from_thread(self._log_err, output or f"Merge failed for '{esc(name)}'")
        self._worker_load_status()

    def trigger_stashes(self) -> None:
        self._clear_diff()
        self._log_cmd("git stash list")
        self._worker_stashes()

    @work(thread=True)
    def _worker_stashes(self) -> None:
        stashes = get_stashes(self._project_root)
        self.app.call_from_thread(self._show_stashes, stashes)

    def _show_stashes(self, stashes: list[GitStash]) -> None:
        self._clear_diff()
        if not stashes:
            self._log("[dim #565f89]No stashes[/]")
            self._log("[dim]Press [bold]z[/] to stash current changes[/]")
            return
        self._log(f"[bold #7aa2f7]Stashes[/]  ({len(stashes)} total)")
        self._log("")
        for s in stashes:
            self._log(f"  [#7aa2f7]{esc(s.ref)}[/]  [#a9b1d6]{esc(s.message)}[/]")
        self._log("")
        self._log("[dim]Press [bold]Z[/] to pop the most recent stash[/]")

    def trigger_diff(self, path: str | None = None) -> None:
        self._clear_diff()
        cmd = f"git diff -- {esc(path)}" if path else "git diff"
        self._log_cmd(cmd)
        self._worker_show_full_diff(path)

    @work(thread=True)
    def _worker_show_full_diff(self, path: str | None) -> None:
        diff_output = get_diff(self._project_root, path=path)
        self.app.call_from_thread(self._show_diff, diff_output, path or "")


# ── Git Control plugin ────────────────────────────────────────────────────────


class GitControlPlugin(Plugin):
    """Phase 5 — Git Control plugin.

    Provides the Git Control panel (plugin ID ``"git"``) accessible via
    sidebar key **3** or the command palette.

    Steps implemented:
        5.1  Plugin shell + widget layout
        5.2  Status display — staged/unstaged/untracked with icons and colors
        5.3  Diff viewer — colorized unified diff, auto-shows on navigation
        5.4  Stage/unstage — per-file (s/u keys) and bulk (a key)
        5.5  Commit — modal with message input and amend option
        5.6  Push/Pull/Fetch — with confirmations and rebase option
        5.7  Branch management — list (b), create (n), switch/delete via trigger
        5.8  Log viewer — recent commits (l key)
        5.9  Stash — push (z), pop (Z), list via trigger
        5.10 File watching — watchdog observer + 10s polling fallback
    """

    def __init__(self) -> None:
        self._widget: GitControlWidget | None = None

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return "git"

    @property
    def name(self) -> str:
        return "Git Control"

    @property
    def icon(self) -> str:
        return "⎇"

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)
        self._project_root: str = ctx.project_root

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        project_root = getattr(self, "_project_root", "")
        self._widget = GitControlWidget(
            project_root=project_root,
            id="git-control-widget",
        )
        yield self._widget

    # ── Commands for palette ───────────────────────────────────────────────────

    def commands(self) -> list[dict]:
        return [
            {
                "title": "Git: Refresh status",
                "description": "Reload git status display",
                "plugin_id": "git",
                "action": self._cmd_refresh,
            },
            {
                "title": "Git: Stage all",
                "description": "Stage all changes (git add -A)",
                "plugin_id": "git",
                "action": self._cmd_stage_all,
            },
            {
                "title": "Git: Commit",
                "description": "Open commit message dialog",
                "plugin_id": "git",
                "action": self._cmd_commit,
            },
            {
                "title": "Git: Push",
                "description": "Push to remote",
                "plugin_id": "git",
                "action": self._cmd_push,
            },
            {
                "title": "Git: Pull",
                "description": "Pull from remote",
                "plugin_id": "git",
                "action": self._cmd_pull,
            },
            {
                "title": "Git: Show log",
                "description": "View recent commit history",
                "plugin_id": "git",
                "action": self._cmd_log,
            },
            {
                "title": "Git: Show branches",
                "description": "List all local branches",
                "plugin_id": "git",
                "action": self._cmd_branches,
            },
            {
                "title": "Git: Stash changes",
                "description": "Stash working tree changes",
                "plugin_id": "git",
                "action": self._cmd_stash,
            },
        ]

    def _call(self, fn_name: str, *args: Any) -> None:
        if self._widget:
            try:
                getattr(self._widget, fn_name)(*args)
            except Exception:
                pass

    def _cmd_refresh(self) -> None:
        self._call("trigger_refresh")

    def _cmd_stage_all(self) -> None:
        self._call("trigger_stage_all")

    def _cmd_commit(self) -> None:
        self._call("trigger_commit")

    def _cmd_push(self) -> None:
        self._call("trigger_push")

    def _cmd_pull(self) -> None:
        self._call("trigger_pull")

    def _cmd_log(self) -> None:
        self._call("trigger_log")

    def _cmd_branches(self) -> None:
        self._call("trigger_branches")

    def _cmd_stash(self) -> None:
        self._call("trigger_stash")

    # ── Text command routing ───────────────────────────────────────────────────

    def handle_command(self, text: str) -> bool:
        """Route ``git <subcommand>`` typed in the command input."""
        if not text.startswith("git"):
            return False
        parts = text.split()
        if len(parts) < 2:
            return False
        sub = parts[1].lower()

        if sub == "status":
            self._call("trigger_refresh")
        elif sub in ("add",) and len(parts) >= 3:
            arg = parts[2]
            if arg in (".", "-A", "--all"):
                self._call("trigger_stage_all")
            else:
                # Stage specific file via widget action
                if self._widget:
                    try:
                        self._widget._clear_diff()
                        self._widget._log_cmd(f"git add -- {arg}")
                        self._widget._worker_stage(arg)
                    except Exception:
                        pass
        elif sub == "commit" and "-m" in parts:
            idx = parts.index("-m")
            if idx + 1 < len(parts):
                message = " ".join(parts[idx + 1:]).strip('"\'')
                amend = "--amend" in parts
                if self._widget:
                    try:
                        self._widget._clear_diff()
                        self._widget._log_cmd(text)
                        self._widget._worker_commit(message, amend)
                    except Exception:
                        pass
        elif sub == "push":
            self._call("trigger_push")
        elif sub == "pull":
            rebase = "--rebase" in parts
            if self._widget:
                try:
                    self._widget._clear_diff()
                    self._widget._log_cmd(text)
                    self._widget._log("[dim #565f89]Pulling…[/]")
                    self._widget._worker_pull(rebase)
                except Exception:
                    pass
        elif sub == "fetch":
            self._call("trigger_fetch")
        elif sub in ("log",):
            self._call("trigger_log")
        elif sub == "stash":
            if len(parts) >= 3 and parts[2] == "pop":
                self._call("trigger_stash_pop")
            elif len(parts) >= 3 and parts[2] == "list":
                self._call("trigger_stashes")
            else:
                self._call("trigger_stash")
        elif sub == "branch":
            if len(parts) >= 3 and parts[2] not in ("-d", "-D"):
                name = parts[2]
                if self._widget:
                    try:
                        self._widget._clear_diff()
                        self._widget._log_cmd(f"git checkout -b {name}")
                        self._widget._worker_create_branch(name)
                    except Exception:
                        pass
            else:
                self._call("trigger_branches")
        elif sub in ("checkout", "switch") and len(parts) >= 3:
            if parts[2] == "-b" and len(parts) >= 4:
                name = parts[3]
                if self._widget:
                    try:
                        self._widget._clear_diff()
                        self._widget._log_cmd(f"git checkout -b {name}")
                        self._widget._worker_create_branch(name)
                    except Exception:
                        pass
            else:
                name = parts[2]
                self._call("trigger_switch_branch", name)
        elif sub == "diff":
            path = parts[2] if len(parts) >= 3 else None
            self._call("trigger_diff", path)
        elif sub == "merge" and len(parts) >= 3:
            name = parts[2]
            if self._widget:
                try:
                    self._widget._clear_diff()
                    self._widget._log_cmd(f"git merge {name}")
                    self._widget._worker_merge_branch(name)
                except Exception:
                    pass
        else:
            return False

        return True
