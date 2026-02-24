from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from fluttercraft.core.platform import detect_toolchain, get_os


# ── Pure helper (testable without Textual) ────────────────────────────────────


def _format_info(
    flutter_version: str,
    fvm_version: str,
    os_name: str,
    project_name: str = "",
    git_branch: str = "",
) -> str:
    """Build the right-side info string for the header bar.

    Only non-empty optional fields are included in the output.
    """
    parts = [
        f"Flutter {flutter_version}",
        f"FVM {fvm_version}",
        os_name,
    ]
    if project_name:
        parts.append(project_name)
    if git_branch:
        parts.append(git_branch)
    return "  ·  ".join(parts)


# ── Header widget ─────────────────────────────────────────────────────────────


class FlutterCraftHeader(Widget):
    """Status bar displaying Flutter version, FVM, OS, active project, and git branch.

    Versions are detected in a background thread on mount so the UI is never
    blocked. Call :meth:`set_project` and :meth:`set_git_branch` to push
    updates from plugins or the EventBus (wired in Phase 2).
    """

    DEFAULT_CSS = """
    FlutterCraftHeader {
        height: 1;
        layout: horizontal;
        background: #1f2335;
    }
    #header-title {
        width: auto;
        padding: 0 2;
        color: #7aa2f7;
        text-style: bold;
    }
    #header-info {
        width: 1fr;
        padding: 0 2;
        color: #565f89;
        content-align: right middle;
    }
    """

    flutter_version: reactive[str] = reactive("…")
    fvm_version: reactive[str] = reactive("…")
    git_branch: reactive[str] = reactive("")
    project_name: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("⚡ FlutterCraft", id="header-title")
        yield Label(self._build_info(), id="header-info")

    def on_mount(self) -> None:
        self._detect_versions()

    @work(thread=True)
    def _detect_versions(self) -> None:
        """Blocking toolchain detection — runs in a thread pool worker."""
        tools = detect_toolchain()
        flutter_ver = tools["flutter"].version if tools["flutter"].available else "not found"
        fvm_ver = tools["fvm"].version if tools["fvm"].available else "not found"
        self.app.call_from_thread(self._apply_versions, flutter_ver, fvm_ver)

    def _apply_versions(self, flutter_ver: str, fvm_ver: str) -> None:
        """Apply detected versions on the main thread."""
        self.flutter_version = flutter_ver
        self.fvm_version = fvm_ver

    # ── Reactive watchers ─────────────────────────────────────────────────────

    def watch_flutter_version(self, _: str) -> None:
        self._refresh_info_label()

    def watch_fvm_version(self, _: str) -> None:
        self._refresh_info_label()

    def watch_git_branch(self, _: str) -> None:
        self._refresh_info_label()

    def watch_project_name(self, _: str) -> None:
        self._refresh_info_label()

    def _build_info(self) -> str:
        return _format_info(
            self.flutter_version,
            self.fvm_version,
            get_os().lower(),
            self.project_name,
            self.git_branch,
        )

    def _refresh_info_label(self) -> None:
        try:
            self.query_one("#header-info", Label).update(self._build_info())
        except Exception:
            pass  # Widget not yet mounted — watcher fires before compose

    # ── Public setters (called by EventBus handlers in Phase 2) ──────────────

    def set_project(self, name: str) -> None:
        """Update the active project name shown in the header."""
        self.project_name = name

    def set_git_branch(self, branch: str) -> None:
        """Update the git branch shown in the header."""
        self.git_branch = branch

    def set_flutter_version(self, version: str) -> None:
        """Override the detected Flutter version (e.g. from a RefreshNeededEvent)."""
        self.flutter_version = version

    def set_fvm_version(self, version: str) -> None:
        """Override the detected FVM version."""
        self.fvm_version = version
