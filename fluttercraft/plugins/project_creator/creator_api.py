from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess

_ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-9;:<=>?]*[a-zA-Z]|\][^\x07]*\x07|[^[\]])")
from dataclasses import dataclass, field
from typing import Callable


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass(slots=True)
class Template:
    """An architecture template for Flutter projects."""

    id: str
    name: str
    description: str
    state_deps: dict[str, str]     # package -> version constraint
    dev_deps: dict[str, str]       # dev package -> version constraint
    folder_structure: list[str]    # relative paths to create under project root


@dataclass
class ProjectConfig:
    """All choices made in the project creation wizard."""

    name: str = ""
    org: str = "com.example"
    platforms: list[str] = field(default_factory=lambda: ["android", "ios"])
    template_id: str = "simple"
    app_icon: bool = False
    splash_screen: bool = False
    linting: bool = False
    output_dir: str = ""


# ── Template registry (6.3) ───────────────────────────────────────────────────


TEMPLATES: list[Template] = [
    Template(
        id="simple",
        name="Simple",
        description="Basic Flutter starter — no state library",
        state_deps={},
        dev_deps={},
        folder_structure=["lib/screens/", "lib/widgets/", "test/"],
    ),
    Template(
        id="bloc",
        name="BLoC",
        description="Business Logic Component (flutter_bloc + equatable)",
        state_deps={"flutter_bloc": "^8.1.6", "equatable": "^2.0.5"},
        dev_deps={},
        folder_structure=["lib/blocs/", "lib/screens/", "lib/models/", "test/blocs/"],
    ),
    Template(
        id="riverpod",
        name="Riverpod",
        description="Reactive state management (flutter_riverpod)",
        state_deps={"flutter_riverpod": "^2.5.1"},
        dev_deps={
            "riverpod_annotation": "^2.3.5",
            "riverpod_generator": "^2.4.0",
            "build_runner": "^2.4.9",
        },
        folder_structure=["lib/providers/", "lib/screens/", "lib/models/", "test/"],
    ),
    Template(
        id="provider",
        name="Provider",
        description="Simple state management (provider)",
        state_deps={"provider": "^6.1.2"},
        dev_deps={},
        folder_structure=["lib/providers/", "lib/screens/", "lib/models/", "test/"],
    ),
    Template(
        id="getx",
        name="GetX",
        description="All-in-one: state, routing, DI (get)",
        state_deps={"get": "^4.6.6"},
        dev_deps={},
        folder_structure=[
            "lib/controllers/",
            "lib/screens/",
            "lib/bindings/",
            "lib/models/",
            "test/",
        ],
    ),
    Template(
        id="mobx",
        name="MobX",
        description="Observable state management (flutter_mobx)",
        state_deps={"flutter_mobx": "^2.2.1", "mobx": "^2.3.3"},
        dev_deps={"build_runner": "^2.4.9", "mobx_codegen": "^2.6.1"},
        folder_structure=["lib/stores/", "lib/screens/", "lib/models/", "test/"],
    ),
    Template(
        id="mvvm",
        name="MVVM",
        description="Model-View-ViewModel pattern",
        state_deps={},
        dev_deps={},
        folder_structure=["lib/viewmodels/", "lib/views/", "lib/models/", "test/"],
    ),
    Template(
        id="clean_arch",
        name="Clean Architecture",
        description="Domain-driven layers + BLoC",
        state_deps={
            "flutter_bloc": "^8.1.6",
            "equatable": "^2.0.5",
            "get_it": "^7.7.0",
            "dartz": "^0.10.1",
        },
        dev_deps={},
        folder_structure=[
            "lib/core/",
            "lib/data/datasources/",
            "lib/data/repositories/",
            "lib/domain/entities/",
            "lib/domain/repositories/",
            "lib/domain/usecases/",
            "lib/presentation/pages/",
            "lib/presentation/blocs/",
            "test/",
        ],
    ),
]


def get_template(template_id: str) -> Template | None:
    """Return a template by id, or None."""
    return next((t for t in TEMPLATES if t.id == template_id), None)


# ── Platform detection (6.2) ──────────────────────────────────────────────────


def detect_platforms() -> dict[str, bool]:
    """Return ``{platform: detected}`` based on available toolchains."""
    system = platform.system().lower()
    result: dict[str, bool] = {
        "android": False,
        "ios": False,
        "web": False,
        "linux": False,
        "windows": False,
        "macos": False,
    }

    # Android: env var or adb on PATH
    if (
        os.environ.get("ANDROID_HOME")
        or os.environ.get("ANDROID_SDK_ROOT")
        or shutil.which("adb")
    ):
        result["android"] = True

    # iOS / macOS: Xcode (macOS only)
    if system == "darwin" and shutil.which("xcodebuild"):
        result["ios"] = True
        result["macos"] = True

    # Web: Chrome or Chromium
    for browser in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        if shutil.which(browser):
            result["web"] = True
            break

    # Linux / Windows: native on matching OS
    if system == "linux":
        result["linux"] = True
    if system == "windows":
        result["windows"] = True

    return result


def is_flutter_installed() -> bool:
    """Return True if flutter is on PATH."""
    return shutil.which("flutter") is not None


# ── Name validation ───────────────────────────────────────────────────────────


def is_valid_project_name(name: str) -> bool:
    """Return True if name is a valid Flutter project name (snake_case)."""
    return bool(re.match(r"^[a-z][a-z0-9_]*$", name))


# ── Pubspec editing (6.4, 6.6, 6.7) ──────────────────────────────────────────


def add_deps_to_pubspec(
    pubspec_path: str,
    deps: dict[str, str],
    dev: bool = False,
) -> bool:
    """Append *deps* to the dependencies or dev_dependencies section."""
    if not deps:
        return True
    try:
        with open(pubspec_path) as f:
            content = f.read()
        section = "dev_dependencies:" if dev else "dependencies:"
        new_lines = "\n".join(f"  {pkg}: {ver}" for pkg, ver in deps.items())
        content = content.replace(section, f"{section}\n{new_lines}", 1)
        with open(pubspec_path, "w") as f:
            f.write(content)
        return True
    except Exception:
        return False


_ICON_CONFIG = """
flutter_launcher_icons:
  android: true
  ios: true
  image_path: "assets/icon/icon.png"
  web:
    generate: true
    image_path: "assets/icon/icon.png"
"""

_SPLASH_CONFIG = """
flutter_native_splash:
  color: "#ffffff"
  image: assets/icon/icon.png
"""


def add_icon_config(pubspec_path: str) -> bool:
    add_deps_to_pubspec(pubspec_path, {"flutter_launcher_icons": "^0.14.1"}, dev=True)
    try:
        with open(pubspec_path, "a") as f:
            f.write(_ICON_CONFIG)
        return True
    except Exception:
        return False


def add_splash_config(pubspec_path: str) -> bool:
    add_deps_to_pubspec(pubspec_path, {"flutter_native_splash": "^2.4.1"}, dev=True)
    try:
        with open(pubspec_path, "a") as f:
            f.write(_SPLASH_CONFIG)
        return True
    except Exception:
        return False


# ── Folder structure generation (6.5) ─────────────────────────────────────────


def create_folder_structure(project_dir: str, template: Template) -> bool:
    """Create template-specific directories; add .gitkeep to empty ones."""
    try:
        for folder in template.folder_structure:
            full_path = os.path.join(project_dir, folder)
            os.makedirs(full_path, exist_ok=True)
            if not os.listdir(full_path):
                open(os.path.join(full_path, ".gitkeep"), "w").close()
        return True
    except Exception:
        return False


# ── Linting (6.5 extra) ───────────────────────────────────────────────────────


_ANALYSIS_OPTIONS = """\
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - prefer_single_quotes
    - always_declare_return_types
    - avoid_print
    - prefer_const_constructors
    - prefer_const_declarations
    - sort_constructors_first
"""


def add_linting(project_dir: str) -> bool:
    """Write a strict analysis_options.yaml to the project root."""
    try:
        path = os.path.join(project_dir, "analysis_options.yaml")
        with open(path, "w") as f:
            f.write(_ANALYSIS_OPTIONS)
        return True
    except Exception:
        return False


# ── Subprocess streaming ───────────────────────────────────────────────────────


def _run_streaming(
    cmd: list[str],
    cwd: str | None,
    on_line: Callable[[str], None],
    timeout: int = 120,
) -> bool:
    """Run *cmd* and stream stdout line-by-line via *on_line*."""
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, ""):
            on_line(_ANSI_ESCAPE.sub("", line.rstrip()))
        proc.wait(timeout=timeout)
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        proc.kill()
        on_line("Command timed out")
        return False
    except (FileNotFoundError, OSError) as exc:
        on_line(str(exc))
        return False


# ── Main creation flow (6.1 → 6.8) ───────────────────────────────────────────


def create_flutter_project(
    config: ProjectConfig,
    on_line: Callable[[str], None],
) -> tuple[bool, str]:
    """Create a Flutter project and apply the chosen template.

    Steps:
        1. ``flutter create --org ... --platforms ... <name>``
        2. Add state management deps to pubspec.yaml
        3. Create template folder structure
        4. Optionally: add linting, app icon config, splash config
        5. ``flutter pub get``

    Returns ``(success, project_dir)``.
    """
    cwd = config.output_dir or os.getcwd()
    project_dir = os.path.join(cwd, config.name)

    # 1. flutter create
    platforms_str = ",".join(config.platforms) if config.platforms else "android,ios"
    cmd = [
        "flutter",
        "create",
        "--org",
        config.org,
        f"--platforms={platforms_str}",
        config.name,
    ]
    on_line(f"$ {' '.join(cmd)}")
    ok = _run_streaming(cmd, cwd=cwd, on_line=on_line)
    if not ok:
        return False, project_dir

    pubspec = os.path.join(project_dir, "pubspec.yaml")
    template = get_template(config.template_id)

    # 2. State management deps
    if template and (template.state_deps or template.dev_deps):
        on_line("")
        on_line("Adding state management dependencies…")
        if template.state_deps:
            add_deps_to_pubspec(pubspec, template.state_deps, dev=False)
        if template.dev_deps:
            add_deps_to_pubspec(pubspec, template.dev_deps, dev=True)

    # 3. Folder structure
    if template:
        on_line("Creating folder structure…")
        create_folder_structure(project_dir, template)

    # 4a. Linting
    if config.linting:
        on_line("Adding analysis_options.yaml…")
        add_linting(project_dir)

    # 4b. App icon
    if config.app_icon:
        assets_dir = os.path.join(project_dir, "assets", "icon")
        os.makedirs(assets_dir, exist_ok=True)
        on_line("Configuring flutter_launcher_icons…")
        add_icon_config(pubspec)
        on_line("  → Add your icon to assets/icon/icon.png")
        on_line("  → Then run: dart run flutter_launcher_icons")

    # 4c. Splash screen
    if config.splash_screen:
        on_line("Configuring flutter_native_splash…")
        add_splash_config(pubspec)
        on_line("  → After pub get, run: dart run flutter_native_splash:create")

    # 5. pub get
    on_line("")
    on_line("$ flutter pub get")
    ok = _run_streaming(["flutter", "pub", "get"], cwd=project_dir, on_line=on_line)

    return ok, project_dir


# ── Open in editor (6.8) ──────────────────────────────────────────────────────


def open_in_editor(project_dir: str) -> bool:
    """Try to open *project_dir* in VS Code, Cursor, or system file manager."""
    for editor in ("code", "cursor", "codium"):
        if shutil.which(editor):
            try:
                subprocess.Popen([editor, project_dir])
                return True
            except Exception:
                pass
    return False


# ── Template preview (6.9) ────────────────────────────────────────────────────


def get_template_preview(config: ProjectConfig) -> str:
    """Return a folder-tree string showing the project layout."""
    template = get_template(config.template_id)
    name = config.name or "my_app"

    lines: list[str] = [f"{name}/", "├── lib/"]

    if template:
        lib_folders = [
            f[4:].rstrip("/")
            for f in template.folder_structure
            if f.startswith("lib/") and f != "lib/"
        ]
        for i, folder in enumerate(lib_folders):
            connector = "└── " if i == len(lib_folders) - 1 else "├── "
            lines.append(f"│   {connector}{folder}/")
    lines.append("│   └── main.dart")
    lines.append("├── test/")
    lines.append("├── pubspec.yaml")
    lines.append("└── README.md")

    if template and template.state_deps:
        lines.append("")
        lines.append("State management deps:")
        for pkg, ver in template.state_deps.items():
            lines.append(f"  {pkg}: {ver}")

    if config.app_icon:
        lines.append("  flutter_launcher_icons: ^0.14.1  (dev)")
    if config.splash_screen:
        lines.append("  flutter_native_splash: ^2.4.1  (dev)")

    return "\n".join(lines)
