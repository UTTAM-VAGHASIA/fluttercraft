from __future__ import annotations

import json
import os
import tempfile
import time
import unittest

from fluttercraft.plugins.workspace.workspace_api import (
    FlutterProject,
    ProjectHealth,
    add_project,
    default_config_path,
    default_scan_roots,
    discover_projects,
    get_flutter_version_for_project,
    get_recent_projects,
    is_flutter_project,
    load_workspace,
    read_pubspec_name,
    remove_project,
    save_workspace,
    touch_project,
)
from fluttercraft.plugins.workspace.plugin import WorkspacePlugin


# ── is_flutter_project ────────────────────────────────────────────────────────

class TestIsFlutterProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_true_when_pubspec_exists(self):
        open(os.path.join(self.tmp, "pubspec.yaml"), "w").close()
        assert is_flutter_project(self.tmp) is True

    def test_false_when_no_pubspec(self):
        assert is_flutter_project(self.tmp) is False

    def test_false_for_nonexistent_dir(self):
        assert is_flutter_project("/nonexistent/dir") is False


# ── read_pubspec_name ─────────────────────────────────────────────────────────

class TestReadPubspecName(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reads_name_field(self):
        pubspec = os.path.join(self.tmp, "pubspec.yaml")
        with open(pubspec, "w") as f:
            f.write("name: my_flutter_app\nversion: 1.0.0\n")
        assert read_pubspec_name(self.tmp) == "my_flutter_app"

    def test_returns_basename_on_missing_pubspec(self):
        name = read_pubspec_name(self.tmp)
        assert name == os.path.basename(self.tmp)

    def test_reads_name_with_spaces_in_value(self):
        pubspec = os.path.join(self.tmp, "pubspec.yaml")
        with open(pubspec, "w") as f:
            f.write("name:   spaced_name  \n")
        assert read_pubspec_name(self.tmp) == "spaced_name"


# ── get_flutter_version_for_project ──────────────────────────────────────────

class TestGetFlutterVersion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_returns_system_when_no_fvm_config(self):
        assert get_flutter_version_for_project(self.tmp) == "system"

    def test_reads_fvm_config(self):
        fvm_dir = os.path.join(self.tmp, ".fvm")
        os.makedirs(fvm_dir)
        config = {"flutterSdkVersion": "3.19.0"}
        with open(os.path.join(fvm_dir, "fvm_config.json"), "w") as f:
            json.dump(config, f)
        assert get_flutter_version_for_project(self.tmp) == "3.19.0"

    def test_returns_system_on_invalid_json(self):
        fvm_dir = os.path.join(self.tmp, ".fvm")
        os.makedirs(fvm_dir)
        with open(os.path.join(fvm_dir, "fvm_config.json"), "w") as f:
            f.write("not valid json")
        assert get_flutter_version_for_project(self.tmp) == "system"


# ── FlutterProject dataclass ──────────────────────────────────────────────────

class TestFlutterProject(unittest.TestCase):
    def test_fields(self):
        p = FlutterProject(path="/tmp/app", name="app")
        assert p.path == "/tmp/app"
        assert p.name == "app"
        assert p.last_opened == 0.0
        assert p.flutter_version == ""
        assert p.theme_override == ""
        assert p.active_plugin == ""

    def test_custom_fields(self):
        p = FlutterProject(
            path="/tmp/app",
            name="app",
            last_opened=12345.0,
            flutter_version="3.19.0",
            theme_override="tokyo_night",
            active_plugin="git",
        )
        assert p.last_opened == 12345.0
        assert p.flutter_version == "3.19.0"
        assert p.theme_override == "tokyo_night"
        assert p.active_plugin == "git"


# ── save_workspace / load_workspace ──────────────────────────────────────────

class TestWorkspacePersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmp, "workspace.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_and_load_roundtrip(self):
        projects = [
            FlutterProject(path="/tmp/app1", name="app1", last_opened=1000.0),
            FlutterProject(path="/tmp/app2", name="app2", flutter_version="3.19.0"),
        ]
        ok = save_workspace(projects, self.config_path, last_active="/tmp/app1")
        assert ok is True
        loaded, last_active = load_workspace(self.config_path)
        assert len(loaded) == 2
        assert loaded[0].path == "/tmp/app1"
        assert loaded[0].name == "app1"
        assert loaded[0].last_opened == 1000.0
        assert loaded[1].flutter_version == "3.19.0"
        assert last_active == "/tmp/app1"

    def test_load_returns_empty_on_missing_file(self):
        loaded, last_active = load_workspace("/nonexistent/workspace.json")
        assert loaded == []
        assert last_active == ""

    def test_load_returns_empty_on_invalid_json(self):
        with open(self.config_path, "w") as f:
            f.write("not json")
        loaded, last_active = load_workspace(self.config_path)
        assert loaded == []
        assert last_active == ""

    def test_save_creates_parent_dirs(self):
        deep_path = os.path.join(self.tmp, "a", "b", "workspace.json")
        ok = save_workspace([], deep_path)
        assert ok is True
        assert os.path.isfile(deep_path)


# ── add_project ───────────────────────────────────────────────────────────────

class TestAddProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project_dir = tempfile.mkdtemp()
        open(os.path.join(self.project_dir, "pubspec.yaml"), "w").close()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_adds_valid_flutter_project(self):
        projects: list[FlutterProject] = []
        proj, err = add_project(projects, self.project_dir)
        assert err == ""
        assert proj is not None
        assert len(projects) == 1
        assert projects[0].path == os.path.realpath(self.project_dir)

    def test_error_on_nonexistent_path(self):
        projects: list[FlutterProject] = []
        proj, err = add_project(projects, "/nonexistent/path/xyz")
        assert proj is None
        assert "not found" in err.lower()

    def test_error_on_non_flutter_dir(self):
        projects: list[FlutterProject] = []
        proj, err = add_project(projects, self.tmp)
        assert proj is None
        assert "pubspec" in err.lower()

    def test_error_on_duplicate(self):
        projects: list[FlutterProject] = []
        add_project(projects, self.project_dir)
        proj, err = add_project(projects, self.project_dir)
        assert proj is None
        assert "already" in err.lower()

    def test_sets_last_opened(self):
        projects: list[FlutterProject] = []
        before = time.time()
        proj, _ = add_project(projects, self.project_dir)
        after = time.time()
        assert proj is not None
        assert before <= proj.last_opened <= after


# ── remove_project ────────────────────────────────────────────────────────────

class TestRemoveProject(unittest.TestCase):
    def test_removes_by_path(self):
        projects = [
            FlutterProject(path="/a", name="a"),
            FlutterProject(path="/b", name="b"),
        ]
        result = remove_project(projects, "/a")
        assert len(result) == 1
        assert result[0].path == "/b"

    def test_no_op_for_missing_path(self):
        projects = [FlutterProject(path="/a", name="a")]
        result = remove_project(projects, "/nonexistent")
        assert len(result) == 1

    def test_returns_new_list(self):
        projects = [FlutterProject(path="/a", name="a")]
        result = remove_project(projects, "/a")
        assert projects is not result


# ── touch_project ─────────────────────────────────────────────────────────────

class TestTouchProject(unittest.TestCase):
    def test_updates_last_opened(self):
        p = FlutterProject(path="/a", name="a", last_opened=0.0)
        before = time.time()
        touch_project([p], "/a")
        after = time.time()
        assert before <= p.last_opened <= after

    def test_no_op_for_missing_path(self):
        p = FlutterProject(path="/a", name="a", last_opened=0.0)
        touch_project([p], "/b")
        assert p.last_opened == 0.0


# ── get_recent_projects ───────────────────────────────────────────────────────

class TestGetRecentProjects(unittest.TestCase):
    def test_returns_sorted_by_last_opened(self):
        projects = [
            FlutterProject(path="/a", name="a", last_opened=100.0),
            FlutterProject(path="/b", name="b", last_opened=300.0),
            FlutterProject(path="/c", name="c", last_opened=200.0),
        ]
        recent = get_recent_projects(projects, 3)
        assert recent[0].path == "/b"
        assert recent[1].path == "/c"
        assert recent[2].path == "/a"

    def test_respects_n_limit(self):
        projects = [
            FlutterProject(path=f"/{i}", name=str(i), last_opened=float(i))
            for i in range(10)
        ]
        recent = get_recent_projects(projects, 3)
        assert len(recent) == 3

    def test_empty_list(self):
        assert get_recent_projects([], 5) == []


# ── discover_projects ─────────────────────────────────────────────────────────

class TestDiscoverProjects(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Structure: tmp/proj1/pubspec.yaml, tmp/sub/proj2/pubspec.yaml
        proj1 = os.path.join(self.tmp, "proj1")
        proj2 = os.path.join(self.tmp, "sub", "proj2")
        os.makedirs(proj1)
        os.makedirs(proj2)
        with open(os.path.join(proj1, "pubspec.yaml"), "w") as f:
            f.write("name: proj1\n")
        with open(os.path.join(proj2, "pubspec.yaml"), "w") as f:
            f.write("name: proj2\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_finds_flutter_projects(self):
        found = discover_projects([self.tmp])
        names = [p.name for p in found]
        assert "proj1" in names
        assert "proj2" in names

    def test_no_duplicates(self):
        found = discover_projects([self.tmp, self.tmp])
        paths = [p.path for p in found]
        assert len(paths) == len(set(paths))

    def test_skips_nonexistent_roots(self):
        found = discover_projects(["/nonexistent/path"])
        assert found == []

    def test_empty_roots(self):
        assert discover_projects([]) == []

    def test_max_depth_respected(self):
        # Create project 4 levels deep
        deep = os.path.join(self.tmp, "a", "b", "c", "d", "deep_proj")
        os.makedirs(deep)
        open(os.path.join(deep, "pubspec.yaml"), "w").close()
        found = discover_projects([self.tmp], max_depth=2)
        paths = [p.path for p in found]
        assert not any("deep_proj" in p for p in paths)


# ── default_config_path ───────────────────────────────────────────────────────

class TestDefaultConfigPath(unittest.TestCase):
    def test_returns_string(self):
        path = default_config_path()
        assert isinstance(path, str)
        assert path.endswith("workspace.json")

    def test_under_home(self):
        path = default_config_path()
        home = os.path.expanduser("~")
        assert path.startswith(home)


# ── default_scan_roots ────────────────────────────────────────────────────────

class TestDefaultScanRoots(unittest.TestCase):
    def test_returns_list_of_existing_dirs(self):
        roots = default_scan_roots()
        assert isinstance(roots, list)
        assert all(os.path.isdir(r) for r in roots)

    def test_includes_home(self):
        roots = default_scan_roots()
        home = os.path.expanduser("~")
        assert home in roots


# ── WorkspacePlugin ───────────────────────────────────────────────────────────

class TestWorkspacePlugin(unittest.TestCase):
    def _make_plugin(self) -> WorkspacePlugin:
        plugin = WorkspacePlugin()
        plugin._widget = None
        return plugin

    def test_plugin_id(self):
        assert WorkspacePlugin().id == "workspace"

    def test_plugin_name(self):
        assert WorkspacePlugin().name == "Workspace"

    def test_plugin_icon(self):
        assert WorkspacePlugin().icon == "◈"

    def test_commands_returns_list(self):
        plugin = self._make_plugin()
        cmds = plugin.commands()
        assert isinstance(cmds, list)
        assert len(cmds) == 3

    def test_commands_have_workspace_plugin_id(self):
        plugin = self._make_plugin()
        for cmd in plugin.commands():
            assert cmd["plugin_id"] == "workspace"
            assert callable(cmd["action"])

    def test_handle_command_scan(self):
        from unittest.mock import MagicMock
        plugin = self._make_plugin()
        plugin._widget = MagicMock()
        result = plugin.handle_command("scan")
        assert result is True
        plugin._widget.action_scan_projects.assert_called_once()

    def test_handle_command_health(self):
        from unittest.mock import MagicMock
        plugin = self._make_plugin()
        plugin._widget = MagicMock()
        result = plugin.handle_command("health")
        assert result is True
        plugin._widget.action_check_health.assert_called_once()

    def test_handle_command_switch_numeric(self):
        from unittest.mock import MagicMock
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._projects = [
            FlutterProject(path="/a", name="app_a"),
            FlutterProject(path="/b", name="app_b"),
        ]
        plugin._widget = mock_widget
        result = plugin.handle_command("switch 2")
        assert result is True
        assert mock_widget._cursor == 1
        mock_widget.action_switch_project.assert_called_once()

    def test_handle_command_switch_by_name(self):
        from unittest.mock import MagicMock
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._projects = [
            FlutterProject(path="/a", name="my_app"),
            FlutterProject(path="/b", name="other_app"),
        ]
        plugin._widget = mock_widget
        result = plugin.handle_command("switch my_app")
        assert result is True
        assert mock_widget._cursor == 0
        mock_widget.action_switch_project.assert_called_once()

    def test_handle_command_unknown_returns_false(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("flutter doctor") is False
        assert plugin.handle_command("git status") is False
        assert plugin.handle_command("") is False

    def test_handle_command_no_widget(self):
        plugin = self._make_plugin()
        plugin._widget = None
        assert plugin.handle_command("scan") is True    # consumed, no crash
        assert plugin.handle_command("health") is True
        assert plugin.handle_command("switch 1") is True


if __name__ == "__main__":
    unittest.main()
