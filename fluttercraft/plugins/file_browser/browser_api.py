from __future__ import annotations

import fnmatch
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


# ── File icons ────────────────────────────────────────────────────────────────

_EXT_ICONS: dict[str, str] = {
    ".dart": "◆",
    ".yaml": "◈", ".yml": "◈",
    ".json": "{}",
    ".md": "≡", ".txt": "≡",
    ".py": "◆",
    ".sh": "$",
    ".lock": "○",
    ".gradle": "⚙",
    ".xml": "<>",
    ".kt": "◆", ".swift": "◆",
    ".html": "<>", ".css": "~",
    ".js": "◆", ".ts": "◆",
    ".png": "□", ".jpg": "□", ".jpeg": "□", ".svg": "□",
    ".toml": "◈",
    ".env": "⚙",
}

_DIR_CLOSED = "▶"
_DIR_OPEN = "▼"
_FILE_DEFAULT = "·"


def get_file_icon(name: str, is_dir: bool, expanded: bool = False) -> str:
    if is_dir:
        return _DIR_OPEN if expanded else _DIR_CLOSED
    ext = os.path.splitext(name)[1].lower()
    return _EXT_ICONS.get(ext, _FILE_DEFAULT)


# ── Git status ────────────────────────────────────────────────────────────────

GIT_STATUS_COLORS: dict[str, str] = {
    "M": "#e0af68",
    "A": "#9ece6a",
    "D": "#f7768e",
    "?": "#565f89",
    "R": "#7aa2f7",
}


def get_git_statuses(root: str) -> dict[str, str]:
    """Return {relative_path: status_char} for all changed files under root."""
    result: dict[str, str] = {}
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        if proc.returncode != 0:
            return result
        for raw_line in proc.stdout.splitlines():
            if len(raw_line) < 4:
                continue
            xy = raw_line[:2]
            path = raw_line[3:].strip().strip('"')
            if " -> " in path:
                path = path.split(" -> ")[-1]
            s = xy.strip()
            if not s:
                continue
            if s == "??":
                char = "?"
            elif "D" in s:
                char = "D"
            elif "A" in s:
                char = "A"
            elif "R" in s:
                char = "R"
            else:
                char = "M"
            result[path] = char
            # Mark parent dirs
            parts = path.split("/")
            for i in range(1, len(parts)):
                parent = "/".join(parts[:i])
                if parent not in result:
                    result[parent] = char
    except Exception:
        pass
    return result


# ── Tree data ─────────────────────────────────────────────────────────────────

_SKIP_DIRS = frozenset({
    ".git", "__pycache__", ".dart_tool", "build",
    ".idea", ".vscode", ".gradle", "node_modules",
})


@dataclass
class FileNode:
    """One visible row in the file tree."""

    path: str        # absolute
    name: str        # basename
    is_dir: bool
    depth: int
    expanded: bool = False
    git_status: str = ""


def build_flat_list(
    root: str,
    expanded_dirs: set[str],
    git_statuses: dict[str, str],
    show_hidden: bool = False,
    filter_pattern: str = "",
    max_depth: int = 15,
) -> list[FileNode]:
    """Return a flat visible list of FileNodes respecting expanded_dirs."""
    result: list[FileNode] = []
    _walk(
        root, root, 0,
        expanded_dirs, git_statuses, result,
        show_hidden, filter_pattern, max_depth,
    )
    return result


def _walk(
    root: str,
    path: str,
    depth: int,
    expanded_dirs: set[str],
    git_statuses: dict[str, str],
    result: list[FileNode],
    show_hidden: bool,
    filter_pattern: str,
    max_depth: int,
) -> None:
    if depth > max_depth:
        return
    try:
        entries = sorted(
            os.scandir(path),
            key=lambda e: (not e.is_dir(), e.name.lower()),
        )
    except (PermissionError, OSError):
        return

    for entry in entries:
        name = entry.name
        if not show_hidden and name.startswith("."):
            continue
        if name in _SKIP_DIRS:
            continue
        is_dir = entry.is_dir(follow_symlinks=False)
        abs_path = entry.path
        rel = os.path.relpath(abs_path, root)

        # Apply filter: hide files that don't match (dirs always shown)
        if filter_pattern and not is_dir:
            if not fnmatch.fnmatch(name, filter_pattern):
                continue

        node = FileNode(
            path=abs_path,
            name=name,
            is_dir=is_dir,
            depth=depth,
            expanded=abs_path in expanded_dirs,
            git_status=git_statuses.get(rel, ""),
        )
        result.append(node)

        if is_dir and abs_path in expanded_dirs:
            _walk(
                root, abs_path, depth + 1,
                expanded_dirs, git_statuses, result,
                show_hidden, filter_pattern, max_depth,
            )


# ── File preview ──────────────────────────────────────────────────────────────

_LEXER_MAP: dict[str, str] = {
    ".dart": "dart",
    ".py": "python",
    ".yaml": "yaml", ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".sh": "bash",
    ".kt": "kotlin",
    ".swift": "swift",
    ".java": "java",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".js": "javascript",
    ".ts": "typescript",
    ".toml": "toml",
    ".gradle": "groovy",
    ".txt": "text",
    ".env": "bash",
}


def get_lexer(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _LEXER_MAP.get(ext, "text")


def read_file_preview(path: str, max_lines: int = 500) -> tuple[str, str]:
    """Return (content, lexer_name)."""
    try:
        size = os.path.getsize(path)
        if size > 512_000:
            return f"[File too large: {size // 1024} KB]", "text"
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"  ... (truncated at {max_lines} lines)")
                    break
                lines.append(line.rstrip())
        return "\n".join(lines), get_lexer(path)
    except Exception as exc:
        return f"[Cannot read: {exc}]", "text"


# ── File operations ───────────────────────────────────────────────────────────

def create_file(path: str) -> tuple[bool, str]:
    try:
        if os.path.exists(path):
            return False, "Already exists"
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        open(path, "w").close()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def create_directory(path: str) -> tuple[bool, str]:
    try:
        os.makedirs(path, exist_ok=True)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def rename_path(src: str, dst: str) -> tuple[bool, str]:
    try:
        if os.path.exists(dst):
            return False, "Destination already exists"
        os.rename(src, dst)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def delete_path(path: str) -> tuple[bool, str]:
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, ""
    except Exception as exc:
        return False, str(exc)


# ── Fuzzy file search ─────────────────────────────────────────────────────────

def get_all_files(root: str, max_files: int = 2000) -> list[str]:
    """Return all relative file paths under root."""
    result: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIRS and not d.startswith(".")
        ]
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            result.append(rel)
            if len(result) >= max_files:
                return result
    return result


def fuzzy_match_files(files: list[str], query: str, max_results: int = 20) -> list[str]:
    if not query:
        return files[:max_results]
    q = query.lower()
    scored: list[tuple[int, str]] = []
    for f in files:
        base = os.path.basename(f).lower()
        if q == base:
            scored.append((0, f))
        elif base.startswith(q):
            scored.append((1, f))
        elif q in base:
            scored.append((2, f))
        elif q in f.lower():
            scored.append((3, f))
    scored.sort(key=lambda x: x[0])
    return [f for _, f in scored[:max_results]]


# ── Content search ────────────────────────────────────────────────────────────

def search_in_files(
    root: str,
    query: str,
    on_result: Callable[[str, int, str], None],
    max_results: int = 100,
) -> int:
    """Call on_result(rel_path, line_num, line) for each match. Returns count."""
    count = 0
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames
                if d not in _SKIP_DIRS and not d.startswith(".")
            ]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, root)
                try:
                    with open(fpath, encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if pattern.search(line):
                                on_result(rel, lineno, line.rstrip())
                                count += 1
                                if count >= max_results:
                                    return count
                except Exception:
                    continue
    except Exception:
        pass
    return count
