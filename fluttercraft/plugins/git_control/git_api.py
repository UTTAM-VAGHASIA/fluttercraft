from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


# ── ANSI strip ────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[mGKHF]|\x1b\].*?\x07")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def esc(text: str) -> str:
    """Escape Rich markup brackets in raw subprocess output."""
    return _strip_ansi(text).replace("[", "\\[")


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class GitFile:
    """A file reported by ``git status --porcelain``."""

    path: str
    index_status: str       # X in XY: M/A/D/R/C/U/? or ' '
    work_tree_status: str   # Y in XY: M/D/U/? or ' '

    @property
    def is_staged(self) -> bool:
        return self.index_status not in ("", " ", "?")

    @property
    def is_unstaged(self) -> bool:
        return self.work_tree_status not in ("", " ", "?")

    @property
    def is_untracked(self) -> bool:
        return self.index_status == "?" and self.work_tree_status == "?"


@dataclass(slots=True)
class GitBranch:
    """A local git branch."""

    name: str
    is_current: bool = False


@dataclass(slots=True)
class GitCommit:
    """A git commit entry from the log."""

    short_hash: str
    author: str
    date: str
    message: str


@dataclass(slots=True)
class GitStash:
    """A stash entry."""

    index: int
    ref: str
    message: str


# ── Availability ──────────────────────────────────────────────────────────────


def is_git_installed() -> bool:
    """Return True if git is on PATH."""
    return shutil.which("git") is not None


def is_git_repo(cwd: str | None = None) -> bool:
    """Return True if *cwd* is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_current_branch(cwd: str | None = None) -> str | None:
    """Return the current branch name, or None."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def get_ahead_behind(cwd: str | None = None) -> tuple[int, int]:
    """Return ``(ahead, behind)`` vs upstream, or ``(0, 0)`` if no upstream."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "--left-right", "HEAD...@{upstream}"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
    except Exception:
        pass
    return 0, 0


# ── Internal runner ───────────────────────────────────────────────────────────


def _run_git(
    args: list[str],
    cwd: str | None = None,
    timeout: int = 30,
) -> tuple[bool, str]:
    """Run ``git <args>`` and return ``(success, combined_output)``."""
    try:
        result = subprocess.run(
            ["git"] + args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except (FileNotFoundError, OSError) as exc:
        return False, str(exc)


# ── Status ────────────────────────────────────────────────────────────────────


def get_status(cwd: str | None = None) -> list[GitFile]:
    """Return file statuses from ``git status --porcelain``.

    Uses a direct subprocess call (not ``_run_git``) to preserve the raw stdout
    without stripping — the XY status prefix requires the exact column positions.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-u"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        output = result.stdout  # no .strip() — preserve leading spaces in XY codes
    except Exception:
        return []
    if not output:
        return []
    files: list[GitFile] = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        index_s = line[0]
        work_s = line[1]
        path = line[3:].strip()
        # Renamed: "old -> new"
        if " -> " in path:
            path = path.split(" -> ")[-1].strip()
        path = path.strip('"')
        files.append(GitFile(path=path, index_status=index_s, work_tree_status=work_s))
    return files


# ── Diff ──────────────────────────────────────────────────────────────────────


def get_diff(
    cwd: str | None = None,
    path: str | None = None,
    staged: bool = False,
) -> str:
    """Return diff output for a path (or all changes if path is None)."""
    args = ["diff"]
    if staged:
        args.append("--staged")
    if path:
        args += ["--", path]
    ok, output = _run_git(args, cwd=cwd, timeout=15)
    return output or ("(no staged changes)" if staged else "(no changes)")


# ── Stage / Unstage ───────────────────────────────────────────────────────────


def stage_file(cwd: str | None = None, path: str = "") -> tuple[bool, str]:
    return _run_git(["add", "--", path], cwd=cwd)


def unstage_file(cwd: str | None = None, path: str = "") -> tuple[bool, str]:
    return _run_git(["restore", "--staged", "--", path], cwd=cwd)


def stage_all(cwd: str | None = None) -> tuple[bool, str]:
    return _run_git(["add", "-A"], cwd=cwd)


# ── Commit ────────────────────────────────────────────────────────────────────


def commit(
    cwd: str | None = None,
    message: str = "",
    amend: bool = False,
) -> tuple[bool, str]:
    args = ["commit", "-m", message]
    if amend:
        args.append("--amend")
    return _run_git(args, cwd=cwd, timeout=30)


# ── Push / Pull / Fetch ───────────────────────────────────────────────────────


def push(cwd: str | None = None, force: bool = False) -> tuple[bool, str]:
    args = ["push"]
    if force:
        args.append("--force-with-lease")
    return _run_git(args, cwd=cwd, timeout=60)


def pull(cwd: str | None = None, rebase: bool = False) -> tuple[bool, str]:
    args = ["pull"]
    if rebase:
        args.append("--rebase")
    return _run_git(args, cwd=cwd, timeout=60)


def fetch(cwd: str | None = None) -> tuple[bool, str]:
    return _run_git(["fetch"], cwd=cwd, timeout=30)


# ── Branches ──────────────────────────────────────────────────────────────────


def get_branches(cwd: str | None = None) -> list[GitBranch]:
    """Return all local branches."""
    ok, output = _run_git(
        ["branch", "--format=%(HEAD)|%(refname:short)"],
        cwd=cwd,
        timeout=10,
    )
    if not output:
        return []
    branches: list[GitBranch] = []
    for line in output.splitlines():
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        head, name = parts
        branches.append(GitBranch(name=name.strip(), is_current=head.strip() == "*"))
    return branches


def create_branch(cwd: str | None = None, name: str = "") -> tuple[bool, str]:
    return _run_git(["checkout", "-b", name], cwd=cwd)


def switch_branch(cwd: str | None = None, name: str = "") -> tuple[bool, str]:
    return _run_git(["checkout", name], cwd=cwd)


def delete_branch(
    cwd: str | None = None, name: str = "", force: bool = False
) -> tuple[bool, str]:
    flag = "-D" if force else "-d"
    return _run_git(["branch", flag, name], cwd=cwd)


def merge_branch(cwd: str | None = None, name: str = "") -> tuple[bool, str]:
    return _run_git(["merge", name], cwd=cwd, timeout=30)


# ── Log ───────────────────────────────────────────────────────────────────────


def get_log(cwd: str | None = None, limit: int = 30) -> list[GitCommit]:
    """Return recent commits from the log."""
    ok, output = _run_git(
        ["log", f"--max-count={limit}", "--pretty=format:%h|%an|%ar|%s"],
        cwd=cwd,
        timeout=10,
    )
    if not output:
        return []
    commits: list[GitCommit] = []
    for line in output.splitlines():
        parts = line.split("|", 3)
        if len(parts) != 4:
            continue
        commits.append(
            GitCommit(
                short_hash=parts[0],
                author=parts[1],
                date=parts[2],
                message=parts[3],
            )
        )
    return commits


# ── Stash ─────────────────────────────────────────────────────────────────────


def get_stashes(cwd: str | None = None) -> list[GitStash]:
    """Return stash list."""
    ok, output = _run_git(["stash", "list", "--format=%gd|%s"], cwd=cwd, timeout=10)
    if not output:
        return []
    stashes: list[GitStash] = []
    for idx, line in enumerate(output.splitlines()):
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        stashes.append(
            GitStash(index=idx, ref=parts[0].strip(), message=parts[1].strip())
        )
    return stashes


def stash_push(cwd: str | None = None, message: str = "") -> tuple[bool, str]:
    args = ["stash", "push"]
    if message:
        args += ["-m", message]
    return _run_git(args, cwd=cwd)


def stash_pop(cwd: str | None = None) -> tuple[bool, str]:
    return _run_git(["stash", "pop"], cwd=cwd)


def stash_apply(cwd: str | None = None, ref: str = "stash@{0}") -> tuple[bool, str]:
    return _run_git(["stash", "apply", ref], cwd=cwd)


def stash_drop(cwd: str | None = None, ref: str = "stash@{0}") -> tuple[bool, str]:
    return _run_git(["stash", "drop", ref], cwd=cwd)


# ── Diff colorizer ────────────────────────────────────────────────────────────


def colorize_diff_line(line: str) -> str:
    """Return Rich markup for a unified diff line."""
    e = esc(line)
    if line.startswith("+++") or line.startswith("---"):
        return f"[#e0af68]{e}[/]"
    if line.startswith("+"):
        return f"[#9ece6a]{e}[/]"
    if line.startswith("-"):
        return f"[#f7768e]{e}[/]"
    if line.startswith("@@"):
        return f"[#7dcfff]{e}[/]"
    if line.startswith("diff ") or line.startswith("index "):
        return f"[dim #565f89]{e}[/]"
    return f"[#a9b1d6]{e}[/]"
