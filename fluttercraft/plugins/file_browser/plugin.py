from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from rich.syntax import Syntax
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Input, Label, RichLog, Static

from fluttercraft.plugins.base import Plugin, PluginContext
from fluttercraft.plugins.file_browser.browser_api import (
    GIT_STATUS_COLORS,
    FileNode,
    build_flat_list,
    create_directory,
    create_file,
    delete_path,
    fuzzy_match_files,
    get_all_files,
    get_file_icon,
    get_git_statuses,
    read_file_preview,
    rename_path,
    search_in_files,
)


# ── Extension colours ─────────────────────────────────────────────────────────

_EXT_COLORS: dict[str, str] = {
    ".dart": "#7aa2f7",
    ".yaml": "#e0af68", ".yml": "#e0af68",
    ".json": "#9ece6a",
    ".md": "#bb9af7",
    ".py": "#7aa2f7",
    ".sh": "#9ece6a",
    ".lock": "#565f89",
    ".gradle": "#e0af68",
    ".xml": "#f7768e",
    ".kt": "#7dcfff",
    ".swift": "#f7768e",
    ".html": "#f7768e", ".css": "#7aa2f7",
    ".js": "#e0af68", ".ts": "#7aa2f7",
    ".png": "#ff9e64", ".jpg": "#ff9e64", ".jpeg": "#ff9e64", ".svg": "#ff9e64",
    ".toml": "#e0af68",
}


# ── Modals ────────────────────────────────────────────────────────────────────

class _InputModal(ModalScreen):
    """Generic single-line input modal (new file, rename, filter, search)."""

    DEFAULT_CSS = """
    _InputModal { align: center middle; }
    _InputModal > Vertical {
        width: 60; height: auto;
        background: #1f2335; border: round #7aa2f7; padding: 1 2;
    }
    _InputModal Label { margin-bottom: 1; color: #c0caf5; }
    _InputModal Input { margin-bottom: 1; }
    _InputModal #modal-hint { color: #565f89; height: 1; }
    """

    def __init__(
        self,
        title: str,
        placeholder: str = "",
        initial: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._placeholder = placeholder
        self._initial = initial

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"[bold #7aa2f7]{self._title}[/]")
            yield Input(
                value=self._initial,
                placeholder=self._placeholder,
                id="modal-input",
            )
            yield Label("[dim]Enter to confirm · Escape to cancel[/]", id="modal-hint")

    def on_mount(self) -> None:
        self.query_one("#modal-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def on_key(self, event: Any) -> None:
        if event.key == "escape":
            self.dismiss(None)


class _ConfirmModal(ModalScreen):
    """Delete confirmation modal."""

    DEFAULT_CSS = """
    _ConfirmModal { align: center middle; }
    _ConfirmModal > Vertical {
        width: 60; height: auto;
        background: #1f2335; border: round #f7768e; padding: 1 2;
    }
    _ConfirmModal Label { color: #c0caf5; margin-bottom: 1; }
    _ConfirmModal #confirm-hint { color: #565f89; }
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold #f7768e]⚠  Confirm Delete[/]")
            yield Label(self._message)
            yield Label(
                "[dim]y / Enter to confirm · n / Escape to cancel[/]",
                id="confirm-hint",
            )

    def on_mount(self) -> None:
        self.focus()

    def on_key(self, event: Any) -> None:
        if event.key in ("y", "enter"):
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)


class _QuickOpenModal(ModalScreen):
    """Fuzzy file search (Ctrl+O)."""

    DEFAULT_CSS = """
    _QuickOpenModal { align: center middle; }
    _QuickOpenModal > Vertical {
        width: 70; height: 30;
        background: #1f2335; border: round #7aa2f7; padding: 1 2;
    }
    _QuickOpenModal Label { color: #c0caf5; margin-bottom: 1; }
    _QuickOpenModal Input { margin-bottom: 1; }
    _QuickOpenModal #qo-results { height: 1fr; color: #a9b1d6; }
    _QuickOpenModal #qo-hint { height: 1; color: #565f89; }
    """

    def __init__(self, files: list[str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._files = files
        self._matches: list[str] = files[:20]
        self._cursor: int = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold #7aa2f7]Quick Open[/]")
            yield Input(placeholder="Type to search files…", id="qo-input")
            yield Static("", id="qo-results")
            yield Label(
                "[dim]↑↓ navigate · Enter open · Escape cancel[/]",
                id="qo-hint",
            )

    def on_mount(self) -> None:
        self.query_one("#qo-input", Input).focus()
        self._render_results()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._matches = fuzzy_match_files(self._files, event.value)
        self._cursor = 0
        self._render_results()

    def on_key(self, event: Any) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "up":
            self._cursor = max(0, self._cursor - 1)
            self._render_results()
            event.stop()
        elif event.key == "down":
            self._cursor = min(len(self._matches) - 1, self._cursor + 1)
            self._render_results()
            event.stop()
        elif event.key == "enter":
            self._open_selected()

    def _open_selected(self) -> None:
        if 0 <= self._cursor < len(self._matches):
            self.dismiss(self._matches[self._cursor])
        else:
            self.dismiss(None)

    def _render_results(self) -> None:
        lines = []
        for i, f in enumerate(self._matches):
            if i == self._cursor:
                lines.append(f"[bold #7aa2f7]▶ {f}[/]")
            else:
                lines.append(f"[dim #565f89]  {f}[/]")
        text = "\n".join(lines) if lines else "[dim #565f89](no matches)[/]"
        self.query_one("#qo-results", Static).update(text)


# ── Main widget ───────────────────────────────────────────────────────────────

class FileBrowserWidget(Widget):
    """File browser with tree view, syntax-highlighted preview, and file ops."""

    can_focus = True

    DEFAULT_CSS = """
    FileBrowserWidget { height: 1fr; layout: vertical; }
    #browser-path-bar {
        height: 1; background: #16161e; color: #7aa2f7;
        padding: 0 1; border-bottom: solid #3b4261;
    }
    #browser-body { height: 1fr; }
    #browser-left {
        width: 30; background: #1f2335;
        border-right: solid #3b4261;
    }
    #browser-tree { height: 1fr; padding: 0 1; color: #a9b1d6; }
    #browser-right { height: 1fr; background: #16161e; }
    #browser-preview { height: 1fr; padding: 0 1; }
    #browser-status-bar {
        height: 1; background: #1f2335; color: #565f89;
        padding: 0 1; border-top: solid #3b4261;
    }
    #browser-footer {
        height: 1; background: #16161e; color: #565f89; padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("up",     "tree_up",         "Up",       show=False, priority=True),
        Binding("down",   "tree_down",        "Down",     show=False, priority=True),
        Binding("right",  "expand_node",      "Expand",   show=False, priority=True),
        Binding("left",   "collapse_node",    "Collapse", show=False, priority=True),
        Binding("space",  "toggle_node",      "Toggle",   show=False, priority=True),
        Binding("enter",  "open_node",        "Open",     show=True),
        Binding("ctrl+o", "quick_open",       "Quick Open", show=True),
        Binding("n",      "new_file",         "New File", show=True),
        Binding("N",      "new_dir",          "New Dir",  show=False),
        Binding("d",      "delete_node",      "Delete",   show=True),
        Binding("r",      "rename_node",      "Rename",   show=True),
        Binding("e",      "open_in_editor",   "Editor",   show=True),
        Binding("s",      "search_content",   "Search",   show=True),
        Binding("f",      "filter_tree",      "Filter",   show=True),
        Binding("R",      "refresh",          "Refresh",  show=False),
        Binding("h",      "toggle_hidden",    "Hidden",   show=False),
    ]

    def __init__(self, root_dir: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._root: str = root_dir or os.getcwd()
        self._flat: list[FileNode] = []
        self._cursor: int = 0
        self._expanded_dirs: set[str] = set()
        self._git_statuses: dict[str, str] = {}
        self._show_hidden: bool = False
        self._filter_pattern: str = ""

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="browser-path-bar")
        with Horizontal(id="browser-body"):
            with Vertical(id="browser-left"):
                yield Static("", id="browser-tree")
            with Vertical(id="browser-right"):
                yield RichLog(
                    id="browser-preview",
                    markup=False,
                    highlight=False,
                    wrap=False,
                )
        yield Static("", id="browser-status-bar")
        yield Static(
            "[dim]↑↓[/] nav  [dim]Enter[/] open  [dim]n[/] new  [dim]d[/] del  "
            "[dim]r[/] rename  [dim]e[/] editor  [dim]s[/] search  "
            "[dim]f[/] filter  [dim]Ctrl+O[/] quick open  [dim]R[/] refresh",
            id="browser-footer",
        )

    def on_mount(self) -> None:
        self._worker_refresh()
        self.set_timer(0.1, self.focus)

    # ── Background workers ─────────────────────────────────────────────────────

    @work(thread=True)
    def _worker_refresh(self) -> None:
        git_statuses = get_git_statuses(self._root)
        flat = build_flat_list(
            self._root,
            self._expanded_dirs,
            git_statuses,
            show_hidden=self._show_hidden,
            filter_pattern=self._filter_pattern,
        )
        self.app.call_from_thread(self._apply_tree, flat, git_statuses)

    def _apply_tree(self, flat: list[FileNode], git_statuses: dict[str, str]) -> None:
        self._flat = flat
        self._git_statuses = git_statuses
        self._cursor = min(self._cursor, max(0, len(flat) - 1))
        self._render_path_bar()
        self._render_tree()
        self._render_status_bar()

    @work(thread=True)
    def _worker_preview(self, path: str) -> None:
        content, lexer = read_file_preview(path)
        self.app.call_from_thread(self._show_preview, content, lexer)

    def _show_preview(self, content: str, lexer: str) -> None:
        rlog = self.query_one("#browser-preview", RichLog)
        rlog.clear()
        if lexer and lexer != "text":
            try:
                rlog.write(
                    Syntax(
                        content,
                        lexer,
                        theme="monokai",
                        line_numbers=True,
                        word_wrap=False,
                    )
                )
                return
            except Exception:
                pass
        # Fallback: plain text
        rlog.markup = True
        rlog.write(f"[#a9b1d6]{content}[/]")
        rlog.markup = False

    @work(thread=True)
    def _worker_load_files_for_qo(self) -> None:
        files = get_all_files(self._root)
        self.app.call_from_thread(self._open_quick_open_modal, files)

    @work(thread=True)
    def _worker_search(self, query: str) -> None:
        results: list[str] = []

        def on_result(rel: str, lineno: int, line: str) -> None:
            results.append(
                f"[dim #565f89]{rel}:{lineno}[/]  [#a9b1d6]{line[:100]}[/]"
            )

        count = search_in_files(self._root, query, on_result)
        self.app.call_from_thread(self._show_search_results, query, results, count)

    def _show_search_results(
        self, query: str, results: list[str], count: int
    ) -> None:
        rlog = self.query_one("#browser-preview", RichLog)
        rlog.clear()
        rlog.markup = True
        rlog.write(
            f"[bold #7aa2f7]Search: {query}[/]  "
            f"[dim #565f89]({count} match{'es' if count != 1 else ''})[/]"
        )
        rlog.write("")
        for line in results:
            rlog.write(line)
        if count == 0:
            rlog.write("[dim #565f89](no matches)[/]")
        rlog.markup = False

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_path_bar(self) -> None:
        try:
            rel = os.path.relpath(self._root)
        except ValueError:
            rel = self._root
        filter_info = f"  [dim #e0af68][{self._filter_pattern}][/]" if self._filter_pattern else ""
        bar = f"[bold #7aa2f7]● File Browser[/]  [dim #565f89]{rel}[/]{filter_info}"
        self.query_one("#browser-path-bar", Static).update(bar)

    def _render_tree(self) -> None:
        if not self._flat:
            msg = "[dim #565f89](empty — press h to show hidden)[/]"
            self.query_one("#browser-tree", Static).update(msg)
            return

        lines: list[str] = []
        for i, node in enumerate(self._flat):
            is_cursor = i == self._cursor
            indent = "  " * node.depth
            icon = get_file_icon(node.name, node.is_dir, node.expanded)

            if node.is_dir:
                name_color = "#7aa2f7"
                icon_color = "#7aa2f7"
            else:
                ext = os.path.splitext(node.name)[1].lower()
                name_color = _EXT_COLORS.get(ext, "#a9b1d6")
                icon_color = "#565f89"

            git_part = ""
            if node.git_status:
                gc = GIT_STATUS_COLORS.get(node.git_status, "#565f89")
                git_part = f" [bold {gc}]{node.git_status}[/]"

            if is_cursor:
                line = (
                    f"{indent}[{icon_color}]{icon}[/] "
                    f"[bold reverse]{node.name}[/]{git_part}"
                )
            else:
                line = (
                    f"{indent}[{icon_color}]{icon}[/] "
                    f"[{name_color}]{node.name}[/]{git_part}"
                )
            lines.append(line)

        self.query_one("#browser-tree", Static).update("\n".join(lines))

    def _render_status_bar(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            self.query_one("#browser-status-bar", Static).update("")
            return
        node = self._flat[self._cursor]
        try:
            rel = os.path.relpath(node.path, self._root)
        except ValueError:
            rel = node.path
        kind = "dir" if node.is_dir else "file"
        git_info = ""
        if node.git_status:
            gc = GIT_STATUS_COLORS.get(node.git_status, "#565f89")
            git_info = f"  [bold {gc}]{node.git_status}[/]"
        self.query_one("#browser-status-bar", Static).update(
            f"[dim #565f89]{kind}: {rel}[/]{git_info}"
        )

    # ── Tree navigation ────────────────────────────────────────────────────────

    def action_tree_up(self) -> None:
        if self._cursor > 0:
            self._cursor -= 1
            self._render_tree()
            self._render_status_bar()
            self._auto_preview()

    def action_tree_down(self) -> None:
        if self._cursor < len(self._flat) - 1:
            self._cursor += 1
            self._render_tree()
            self._render_status_bar()
            self._auto_preview()

    def _auto_preview(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        if not node.is_dir:
            self._worker_preview(node.path)

    def action_open_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        if node.is_dir:
            self.action_toggle_node()
        else:
            self._worker_preview(node.path)

    def action_expand_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        if node.is_dir and node.path not in self._expanded_dirs:
            self._expanded_dirs.add(node.path)
            self._worker_refresh()

    def action_collapse_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        if node.is_dir and node.path in self._expanded_dirs:
            self._expanded_dirs.discard(node.path)
            self._worker_refresh()
        elif node.depth > 0:
            parent = os.path.dirname(node.path)
            for i, n in enumerate(self._flat):
                if n.path == parent:
                    self._cursor = i
                    break
            self._render_tree()
            self._render_status_bar()

    def action_toggle_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        if not node.is_dir:
            return
        if node.path in self._expanded_dirs:
            self._expanded_dirs.discard(node.path)
        else:
            self._expanded_dirs.add(node.path)
        self._worker_refresh()

    def action_refresh(self) -> None:
        self._worker_refresh()

    def action_toggle_hidden(self) -> None:
        self._show_hidden = not self._show_hidden
        self._worker_refresh()

    # ── Quick open ────────────────────────────────────────────────────────────

    def action_quick_open(self) -> None:
        self._worker_load_files_for_qo()

    def _open_quick_open_modal(self, files: list[str]) -> None:
        self.app.push_screen(
            _QuickOpenModal(files),
            self._on_quick_open_result,
        )

    def _on_quick_open_result(self, rel_path: str | None) -> None:
        if rel_path:
            abs_path = os.path.join(self._root, rel_path)
            # Expand parent dirs
            parts = rel_path.replace("\\", "/").split("/")
            for i in range(1, len(parts)):
                dir_path = os.path.join(self._root, *parts[:i])
                self._expanded_dirs.add(dir_path)
            self._worker_refresh()
            self._worker_preview(abs_path)
        self.set_timer(0.05, self.focus)

    # ── File operations ───────────────────────────────────────────────────────

    def _current_dir(self) -> str:
        if not self._flat or self._cursor >= len(self._flat):
            return self._root
        node = self._flat[self._cursor]
        return node.path if node.is_dir else os.path.dirname(node.path)

    def action_new_file(self) -> None:
        self.app.push_screen(
            _InputModal("New File", placeholder="filename.dart"),
            self._on_new_file,
        )

    def _on_new_file(self, name: str | None) -> None:
        if name:
            ok, err = create_file(os.path.join(self._current_dir(), name))
            if not ok:
                self._set_status_error(f"Create failed: {err}")
            else:
                self._worker_refresh()
        self.set_timer(0.05, self.focus)

    def action_new_dir(self) -> None:
        self.app.push_screen(
            _InputModal("New Directory", placeholder="folder_name"),
            self._on_new_dir,
        )

    def _on_new_dir(self, name: str | None) -> None:
        if name:
            ok, err = create_directory(os.path.join(self._current_dir(), name))
            if not ok:
                self._set_status_error(f"Create failed: {err}")
            else:
                self._worker_refresh()
        self.set_timer(0.05, self.focus)

    def action_delete_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        self.app.push_screen(
            _ConfirmModal(f"Delete [bold]{node.name}[/]?"),
            lambda confirmed: self._on_delete_confirm(confirmed, node.path),
        )

    def _on_delete_confirm(self, confirmed: bool | None, path: str) -> None:
        if confirmed:
            ok, err = delete_path(path)
            if not ok:
                self._set_status_error(f"Delete failed: {err}")
            else:
                self._cursor = max(0, self._cursor - 1)
                self._worker_refresh()
        self.set_timer(0.05, self.focus)

    def action_rename_node(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        node = self._flat[self._cursor]
        self.app.push_screen(
            _InputModal("Rename", placeholder="new name", initial=node.name),
            lambda new_name: self._on_rename(new_name, node.path),
        )

    def _on_rename(self, new_name: str | None, old_path: str) -> None:
        if new_name and new_name != os.path.basename(old_path):
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            ok, err = rename_path(old_path, new_path)
            if not ok:
                self._set_status_error(f"Rename failed: {err}")
            else:
                self._worker_refresh()
        self.set_timer(0.05, self.focus)

    # ── Open in editor ────────────────────────────────────────────────────────

    def action_open_in_editor(self) -> None:
        if not self._flat or self._cursor >= len(self._flat):
            return
        target = self._flat[self._cursor].path
        for editor in ("code", "cursor", "codium"):
            if shutil.which(editor):
                try:
                    subprocess.Popen([editor, target])
                    return
                except Exception:
                    pass

    # ── Content search ────────────────────────────────────────────────────────

    def action_search_content(self) -> None:
        self.app.push_screen(
            _InputModal("Search in Files", placeholder="search query"),
            self._on_search,
        )

    def _on_search(self, query: str | None) -> None:
        if query:
            self._worker_search(query)
        self.set_timer(0.05, self.focus)

    # ── Filter ────────────────────────────────────────────────────────────────

    def action_filter_tree(self) -> None:
        self.app.push_screen(
            _InputModal(
                "Filter Tree",
                placeholder="*.dart  (empty to clear)",
                initial=self._filter_pattern,
            ),
            self._on_filter,
        )

    def _on_filter(self, pattern: str | None) -> None:
        if pattern is not None:
            self._filter_pattern = pattern
            self._worker_refresh()
        self.set_timer(0.05, self.focus)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status_error(self, msg: str) -> None:
        try:
            self.query_one("#browser-status-bar", Static).update(
                f"[bold #f7768e]{msg}[/]"
            )
        except Exception:
            pass

    # ── Public API ────────────────────────────────────────────────────────────

    def set_root(self, path: str) -> None:
        """Change the browser root directory."""
        self._root = path
        self._expanded_dirs.clear()
        self._cursor = 0
        self._filter_pattern = ""
        self._worker_refresh()


# ── File Browser Plugin ───────────────────────────────────────────────────────


class FileBrowserPlugin(Plugin):
    """Phase 7 — File Browser plugin (plugin ID ``"files"``)."""

    def __init__(self) -> None:
        self._widget: FileBrowserWidget | None = None

    @property
    def id(self) -> str:
        return "files"

    @property
    def name(self) -> str:
        return "File Browser"

    @property
    def icon(self) -> str:
        return "◉"

    def init(self, ctx: PluginContext) -> None:
        super().init(ctx)
        self._root_dir: str = ctx.project_root or ctx.work_dir or ""

    def compose(self) -> ComposeResult:
        root = getattr(self, "_root_dir", "") or os.getcwd()
        self._widget = FileBrowserWidget(root_dir=root, id="file-browser-widget")
        yield self._widget

    def commands(self) -> list[dict]:
        return [
            {
                "title": "Browser: Refresh tree",
                "description": "Reload the file tree",
                "plugin_id": "files",
                "action": self._cmd_refresh,
            },
            {
                "title": "Browser: Quick open file",
                "description": "Ctrl+O — fuzzy file search",
                "plugin_id": "files",
                "action": self._cmd_quick_open,
            },
            {
                "title": "Browser: Search in files",
                "description": "Grep-style content search",
                "plugin_id": "files",
                "action": self._cmd_search,
            },
        ]

    def _call(self, method: str, *args: Any) -> None:
        if self._widget:
            try:
                getattr(self._widget, method)(*args)
            except Exception:
                pass

    def _cmd_refresh(self) -> None:
        self._call("action_refresh")

    def _cmd_quick_open(self) -> None:
        self._call("action_quick_open")

    def _cmd_search(self) -> None:
        self._call("action_search_content")

    def handle_command(self, text: str) -> bool:
        """Route commands from the bottom command input.

        Accepted:
            ``cd <path>``    — change browser root
            ``open <path>``  — preview a file by path
            ``search <q>``   — search in files
        """
        parts = text.strip().split(None, 1)
        if not parts:
            return False
        cmd = parts[0].lower()

        if cmd == "cd" and len(parts) == 2:
            path = os.path.expanduser(parts[1])
            if not os.path.isabs(path):
                base = self._widget._root if self._widget else os.getcwd()
                path = os.path.join(base, path)
            if os.path.isdir(path):
                self._call("set_root", path)
            return True

        if cmd in ("open", "preview") and len(parts) == 2:
            if self._widget:
                path = os.path.expanduser(parts[1])
                if not os.path.isabs(path):
                    path = os.path.join(self._widget._root, path)
                if os.path.isfile(path):
                    self._widget._worker_preview(path)
            return True

        if cmd == "search" and len(parts) == 2:
            self._call("_worker_search", parts[1])
            return True

        return False
