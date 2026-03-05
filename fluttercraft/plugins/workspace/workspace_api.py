from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class FlutterProject:
    """A Flutter project tracked by the workspace manager."""

    path: str
    name: str
    last_opened: float = 0.0       # unix timestamp
    flutter_version: str = ""      # pinned FVM version or "system"
    theme_override: str = ""       # theme name, "" = use app default
    active_plugin: str = ""        # last active plugin ID


@dataclass
class ProjectHealth:
    """Result of a lightweight health check on a project."""

    has_pubspec: bool = False
    flutter_on_path: bool = False
    fvm_version: str = ""          # from .fvm/fvm_config.json, "" = not pinned
    pubspec_name: str = ""
    dart_sdk: str = ""


# ── Pubspec helpers ───────────────────────────────────────────────────────────


def is_flutter_project(path: str) -> bool:
    """Return True if *path* contains a pubspec.yaml."""
    return os.path.isfile(os.path.join(path, "pubspec.yaml"))


def read_pubspec_name(project_path: str) -> str:
    """Extract the ``name:`` field from pubspec.yaml, or return basename."""
    pubspec = os.path.join(project_path, "pubspec.yaml")
    try:
        with open(pubspec, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("name:"):
                    return stripped.split(":", 1)[1].strip()
    except Exception:
        pass
    return os.path.basename(project_path)


def get_flutter_version_for_project(project_path: str) -> str:
    """Return pinned FVM version or ``"system"``."""
    fvm_config = os.path.join(project_path, ".fvm", "fvm_config.json")
    try:
        with open(fvm_config, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("flutterSdkVersion") or data.get("flutter") or "system"
    except Exception:
        return "system"


# ── Project discovery ─────────────────────────────────────────────────────────


def discover_projects(
    roots: list[str],
    max_depth: int = 3,
) -> list[FlutterProject]:
    """Scan *roots* for Flutter projects up to *max_depth* levels deep."""
    found: list[FlutterProject] = []
    seen: set[str] = set()

    for root in roots:
        root = os.path.expanduser(root)
        if not os.path.isdir(root):
            continue
        _scan_dir(root, root, 0, max_depth, found, seen)

    return found


def _scan_dir(
    root: str,
    path: str,
    depth: int,
    max_depth: int,
    found: list[FlutterProject],
    seen: set[str],
) -> None:
    if depth > max_depth:
        return
    if is_flutter_project(path):
        abs_path = os.path.realpath(path)
        if abs_path not in seen:
            seen.add(abs_path)
            found.append(
                FlutterProject(
                    path=abs_path,
                    name=read_pubspec_name(abs_path),
                    flutter_version=get_flutter_version_for_project(abs_path),
                )
            )
        return  # don't recurse into Flutter project sub-dirs

    try:
        entries = [
            e for e in os.scandir(path)
            if e.is_dir(follow_symlinks=False)
            and not e.name.startswith(".")
            and e.name not in ("build", "__pycache__", "node_modules", ".dart_tool")
        ]
    except (PermissionError, OSError):
        return

    for entry in entries:
        _scan_dir(root, entry.path, depth + 1, max_depth, found, seen)


# ── Health check ──────────────────────────────────────────────────────────────


def check_project_health(project_path: str) -> ProjectHealth:
    """Run a lightweight health check (no subprocess for analyze/pub)."""
    health = ProjectHealth()
    health.has_pubspec = is_flutter_project(project_path)
    health.pubspec_name = read_pubspec_name(project_path)
    health.flutter_on_path = shutil.which("flutter") is not None
    health.fvm_version = get_flutter_version_for_project(project_path)

    # Try to get dart SDK version quickly
    dart = shutil.which("dart")
    if dart:
        try:
            result = subprocess.run(
                ["dart", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            out = (result.stdout or result.stderr or "").strip()
            # e.g. "Dart SDK version: 3.3.0 (stable)"
            if "version" in out.lower():
                parts = out.split()
                for i, p in enumerate(parts):
                    if p.lower() == "version:" and i + 1 < len(parts):
                        health.dart_sdk = parts[i + 1]
                        break
        except Exception:
            pass

    return health


# ── Persistence ───────────────────────────────────────────────────────────────


def load_workspace(config_path: str) -> tuple[list[FlutterProject], str]:
    """Load project list from *config_path*. Returns (projects, last_active_path)."""
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        projects = []
        for item in data.get("projects", []):
            projects.append(
                FlutterProject(
                    path=item.get("path", ""),
                    name=item.get("name", ""),
                    last_opened=float(item.get("last_opened", 0.0)),
                    flutter_version=item.get("flutter_version", ""),
                    theme_override=item.get("theme_override", ""),
                    active_plugin=item.get("active_plugin", ""),
                )
            )
        return projects, data.get("last_active", "")
    except Exception:
        return [], ""


def save_workspace(
    projects: list[FlutterProject],
    config_path: str,
    last_active: str = "",
) -> bool:
    """Persist project list to *config_path*."""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        data = {"projects": [asdict(p) for p in projects], "last_active": last_active}
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


# ── Project list operations ───────────────────────────────────────────────────


def add_project(
    projects: list[FlutterProject],
    path: str,
) -> tuple[FlutterProject | None, str]:
    """Add a project by path. Returns (project, error_msg)."""
    abs_path = os.path.realpath(os.path.expanduser(path))
    if not os.path.isdir(abs_path):
        return None, f"Directory not found: {abs_path}"
    if not is_flutter_project(abs_path):
        return None, f"No pubspec.yaml found in: {abs_path}"
    if any(p.path == abs_path for p in projects):
        return None, "Project already in workspace"
    project = FlutterProject(
        path=abs_path,
        name=read_pubspec_name(abs_path),
        flutter_version=get_flutter_version_for_project(abs_path),
        last_opened=time.time(),
    )
    projects.append(project)
    return project, ""


def remove_project(
    projects: list[FlutterProject],
    path: str,
) -> list[FlutterProject]:
    """Return a new list with the project at *path* removed."""
    return [p for p in projects if p.path != path]


def touch_project(projects: list[FlutterProject], path: str) -> None:
    """Update last_opened timestamp for the project at *path*."""
    for p in projects:
        if p.path == path:
            p.last_opened = time.time()
            return


def get_recent_projects(
    projects: list[FlutterProject],
    n: int = 5,
) -> list[FlutterProject]:
    """Return the *n* most recently opened projects."""
    return sorted(projects, key=lambda p: p.last_opened, reverse=True)[:n]


def default_scan_roots() -> list[str]:
    """Return common directories to scan for Flutter projects."""
    home = os.path.expanduser("~")
    candidates = [
        home,
        os.path.join(home, "Desktop"),
        os.path.join(home, "Projects"),
        os.path.join(home, "projects"),
        os.path.join(home, "dev"),
        os.path.join(home, "code"),
        os.path.join(home, "workspace"),
        os.path.join(home, "Documents"),
        os.getcwd(),
    ]
    return [d for d in candidates if os.path.isdir(d)]


def default_config_path() -> str:
    """Return the default workspace.json path."""
    return os.path.join(
        os.path.expanduser("~"), ".fluttercraft", "workspace.json"
    )
