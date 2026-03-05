from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from fluttercraft.plugins.file_browser.browser_api import (
    FileNode,
    build_flat_list,
    create_directory,
    create_file,
    delete_path,
    fuzzy_match_files,
    get_all_files,
    get_file_icon,
    get_lexer,
    read_file_preview,
    rename_path,
    search_in_files,
)
from fluttercraft.plugins.file_browser.plugin import FileBrowserPlugin


# ── get_file_icon ─────────────────────────────────────────────────────────────

class TestGetFileIcon(unittest.TestCase):
    def test_dir_closed(self):
        assert get_file_icon("lib", is_dir=True, expanded=False) == "▶"

    def test_dir_open(self):
        assert get_file_icon("lib", is_dir=True, expanded=True) == "▼"

    def test_dart_file(self):
        assert get_file_icon("main.dart", is_dir=False) == "◆"

    def test_yaml_file(self):
        assert get_file_icon("pubspec.yaml", is_dir=False) == "◈"

    def test_json_file(self):
        assert get_file_icon("config.json", is_dir=False) == "{}"

    def test_md_file(self):
        assert get_file_icon("README.md", is_dir=False) == "≡"

    def test_unknown_extension(self):
        assert get_file_icon("binary.bin", is_dir=False) == "·"

    def test_no_extension(self):
        assert get_file_icon("Makefile", is_dir=False) == "·"


# ── get_lexer ─────────────────────────────────────────────────────────────────

class TestGetLexer(unittest.TestCase):
    def test_dart(self):
        assert get_lexer("main.dart") == "dart"

    def test_python(self):
        assert get_lexer("script.py") == "python"

    def test_yaml(self):
        assert get_lexer("pubspec.yaml") == "yaml"

    def test_json(self):
        assert get_lexer("package.json") == "json"

    def test_unknown(self):
        assert get_lexer("binary.bin") == "text"

    def test_case_insensitive(self):
        assert get_lexer("main.DART") == "dart"


# ── build_flat_list ───────────────────────────────────────────────────────────

class TestBuildFlatList(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Create structure: lib/ main.dart, test/
        os.makedirs(os.path.join(self.tmp, "lib"))
        os.makedirs(os.path.join(self.tmp, "test"))
        open(os.path.join(self.tmp, "pubspec.yaml"), "w").close()
        open(os.path.join(self.tmp, "lib", "main.dart"), "w").close()
        open(os.path.join(self.tmp, "test", "widget_test.dart"), "w").close()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_top_level_only_when_nothing_expanded(self):
        flat = build_flat_list(self.tmp, set(), {})
        names = [n.name for n in flat]
        # Dirs come first (sorted), then files
        assert "lib" in names
        assert "test" in names
        assert "pubspec.yaml" in names
        # Children not visible yet
        assert "main.dart" not in names

    def test_children_visible_when_expanded(self):
        lib_path = os.path.join(self.tmp, "lib")
        flat = build_flat_list(self.tmp, {lib_path}, {})
        names = [n.name for n in flat]
        assert "main.dart" in names

    def test_depth_is_correct(self):
        lib_path = os.path.join(self.tmp, "lib")
        flat = build_flat_list(self.tmp, {lib_path}, {})
        lib_node = next(n for n in flat if n.name == "lib")
        main_node = next(n for n in flat if n.name == "main.dart")
        assert lib_node.depth == 0
        assert main_node.depth == 1

    def test_is_dir_flag(self):
        flat = build_flat_list(self.tmp, set(), {})
        lib_node = next(n for n in flat if n.name == "lib")
        yaml_node = next(n for n in flat if n.name == "pubspec.yaml")
        assert lib_node.is_dir is True
        assert yaml_node.is_dir is False

    def test_expanded_flag_set(self):
        lib_path = os.path.join(self.tmp, "lib")
        flat = build_flat_list(self.tmp, {lib_path}, {})
        lib_node = next(n for n in flat if n.name == "lib")
        assert lib_node.expanded is True

    def test_git_status_applied(self):
        flat = build_flat_list(self.tmp, set(), {"pubspec.yaml": "M"})
        yaml_node = next(n for n in flat if n.name == "pubspec.yaml")
        assert yaml_node.git_status == "M"

    def test_filter_pattern_hides_non_matching_files(self):
        flat = build_flat_list(self.tmp, set(), {}, filter_pattern="*.yaml")
        names = [n.name for n in flat]
        assert "pubspec.yaml" in names
        # Dirs always shown
        assert "lib" in names

    def test_hidden_files_excluded_by_default(self):
        hidden = os.path.join(self.tmp, ".hidden_file")
        open(hidden, "w").close()
        flat = build_flat_list(self.tmp, set(), {})
        names = [n.name for n in flat]
        assert ".hidden_file" not in names

    def test_hidden_files_included_when_requested(self):
        hidden = os.path.join(self.tmp, ".hidden_file")
        open(hidden, "w").close()
        flat = build_flat_list(self.tmp, set(), {}, show_hidden=True)
        names = [n.name for n in flat]
        assert ".hidden_file" in names


# ── FileNode ──────────────────────────────────────────────────────────────────

class TestFileNode(unittest.TestCase):
    def test_dataclass_fields(self):
        node = FileNode(
            path="/tmp/lib",
            name="lib",
            is_dir=True,
            depth=0,
            expanded=True,
            git_status="M",
        )
        assert node.path == "/tmp/lib"
        assert node.name == "lib"
        assert node.is_dir is True
        assert node.depth == 0
        assert node.expanded is True
        assert node.git_status == "M"

    def test_defaults(self):
        node = FileNode(path="/tmp/f", name="f", is_dir=False, depth=1)
        assert node.expanded is False
        assert node.git_status == ""


# ── read_file_preview ─────────────────────────────────────────────────────────

class TestReadFilePreview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reads_content(self):
        p = os.path.join(self.tmp, "main.dart")
        with open(p, "w") as f:
            f.write("void main() {}\n")
        content, lexer = read_file_preview(p)
        assert "void main()" in content
        assert lexer == "dart"

    def test_returns_error_on_missing_file(self):
        content, lexer = read_file_preview("/nonexistent/file.dart")
        assert "Cannot read" in content

    def test_truncates_large_files(self):
        p = os.path.join(self.tmp, "big.txt")
        with open(p, "w") as f:
            for i in range(600):
                f.write(f"line {i}\n")
        content, _ = read_file_preview(p, max_lines=500)
        assert "truncated" in content

    def test_lexer_for_yaml(self):
        p = os.path.join(self.tmp, "pubspec.yaml")
        open(p, "w").close()
        _, lexer = read_file_preview(p)
        assert lexer == "yaml"


# ── create_file ───────────────────────────────────────────────────────────────

class TestCreateFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_file(self):
        p = os.path.join(self.tmp, "new.dart")
        ok, err = create_file(p)
        assert ok is True
        assert err == ""
        assert os.path.isfile(p)

    def test_fails_if_exists(self):
        p = os.path.join(self.tmp, "existing.dart")
        open(p, "w").close()
        ok, err = create_file(p)
        assert ok is False
        assert "Already exists" in err

    def test_creates_in_new_subdirectory(self):
        p = os.path.join(self.tmp, "sub", "file.dart")
        ok, _ = create_file(p)
        assert ok is True
        assert os.path.isfile(p)


# ── create_directory ──────────────────────────────────────────────────────────

class TestCreateDirectory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_directory(self):
        p = os.path.join(self.tmp, "new_dir")
        ok, _ = create_directory(p)
        assert ok is True
        assert os.path.isdir(p)

    def test_idempotent_on_existing(self):
        p = os.path.join(self.tmp, "existing")
        os.makedirs(p)
        ok, _ = create_directory(p)
        assert ok is True

    def test_creates_nested(self):
        p = os.path.join(self.tmp, "a", "b", "c")
        ok, _ = create_directory(p)
        assert ok is True
        assert os.path.isdir(p)


# ── rename_path ───────────────────────────────────────────────────────────────

class TestRenamePath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_renames_file(self):
        src = os.path.join(self.tmp, "old.dart")
        dst = os.path.join(self.tmp, "new.dart")
        open(src, "w").close()
        ok, _ = rename_path(src, dst)
        assert ok is True
        assert os.path.isfile(dst)
        assert not os.path.exists(src)

    def test_fails_if_dst_exists(self):
        src = os.path.join(self.tmp, "a.dart")
        dst = os.path.join(self.tmp, "b.dart")
        open(src, "w").close()
        open(dst, "w").close()
        ok, err = rename_path(src, dst)
        assert ok is False
        assert "already exists" in err.lower()


# ── delete_path ───────────────────────────────────────────────────────────────

class TestDeletePath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_deletes_file(self):
        p = os.path.join(self.tmp, "file.dart")
        open(p, "w").close()
        ok, _ = delete_path(p)
        assert ok is True
        assert not os.path.exists(p)

    def test_deletes_directory_recursively(self):
        d = os.path.join(self.tmp, "dir")
        os.makedirs(d)
        open(os.path.join(d, "file.txt"), "w").close()
        ok, _ = delete_path(d)
        assert ok is True
        assert not os.path.exists(d)

    def test_fails_on_nonexistent(self):
        ok, err = delete_path(os.path.join(self.tmp, "ghost.dart"))
        assert ok is False
        assert err != ""


# ── fuzzy_match_files ─────────────────────────────────────────────────────────

class TestFuzzyMatchFiles(unittest.TestCase):
    FILES = [
        "lib/main.dart",
        "lib/screens/home_screen.dart",
        "lib/widgets/button.dart",
        "pubspec.yaml",
        "test/widget_test.dart",
    ]

    def test_empty_query_returns_all(self):
        result = fuzzy_match_files(self.FILES, "", max_results=10)
        assert len(result) == len(self.FILES)

    def test_exact_basename_match_first(self):
        result = fuzzy_match_files(self.FILES, "main.dart")
        assert result[0] == "lib/main.dart"

    def test_partial_match(self):
        result = fuzzy_match_files(self.FILES, "home")
        assert any("home_screen" in r for r in result)

    def test_path_match(self):
        result = fuzzy_match_files(self.FILES, "widgets")
        assert any("button" in r for r in result)

    def test_max_results_respected(self):
        result = fuzzy_match_files(self.FILES, "dart", max_results=2)
        assert len(result) <= 2

    def test_no_match_returns_empty(self):
        result = fuzzy_match_files(self.FILES, "zzznomatch")
        assert result == []


# ── get_all_files ─────────────────────────────────────────────────────────────

class TestGetAllFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "lib"))
        open(os.path.join(self.tmp, "pubspec.yaml"), "w").close()
        open(os.path.join(self.tmp, "lib", "main.dart"), "w").close()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_returns_relative_paths(self):
        files = get_all_files(self.tmp)
        assert all(not os.path.isabs(f) for f in files)

    def test_finds_nested_files(self):
        files = get_all_files(self.tmp)
        names = [os.path.basename(f) for f in files]
        assert "main.dart" in names
        assert "pubspec.yaml" in names

    def test_skips_build_dirs(self):
        build_dir = os.path.join(self.tmp, "build")
        os.makedirs(build_dir)
        open(os.path.join(build_dir, "output.dart"), "w").close()
        files = get_all_files(self.tmp)
        assert not any("output.dart" in f for f in files)

    def test_max_files_respected(self):
        for i in range(10):
            open(os.path.join(self.tmp, f"file{i}.txt"), "w").close()
        files = get_all_files(self.tmp, max_files=5)
        assert len(files) <= 5


# ── search_in_files ───────────────────────────────────────────────────────────

class TestSearchInFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        with open(os.path.join(self.tmp, "main.dart"), "w") as f:
            f.write("void main() {\n  print('hello world');\n}\n")
        with open(os.path.join(self.tmp, "README.md"), "w") as f:
            f.write("# Hello World\nThis is a Flutter project.\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_finds_match(self):
        results = []
        count = search_in_files(self.tmp, "hello", lambda r, l, line: results.append(r))
        assert count > 0
        assert any("main.dart" in r or "README.md" in r for r in results)

    def test_case_insensitive(self):
        results = []
        count = search_in_files(self.tmp, "HELLO", lambda r, l, line: results.append(r))
        assert count > 0

    def test_no_match_returns_zero(self):
        count = search_in_files(self.tmp, "zzznomatch", lambda r, l, line: None)
        assert count == 0

    def test_max_results_respected(self):
        # Create many files with matches
        for i in range(20):
            with open(os.path.join(self.tmp, f"file{i}.txt"), "w") as f:
                f.write("target line\n")
        count = search_in_files(
            self.tmp, "target", lambda r, l, line: None, max_results=5
        )
        assert count <= 5

    def test_provides_line_number(self):
        line_nums = []
        search_in_files(
            self.tmp, "print", lambda r, lineno, line: line_nums.append(lineno)
        )
        assert 2 in line_nums  # "print" is on line 2


# ── FileBrowserPlugin ─────────────────────────────────────────────────────────

class TestFileBrowserPlugin(unittest.TestCase):
    def _make_plugin(self) -> FileBrowserPlugin:
        plugin = FileBrowserPlugin()
        plugin._widget = None
        return plugin

    def test_plugin_id(self):
        assert FileBrowserPlugin().id == "files"

    def test_plugin_name(self):
        assert FileBrowserPlugin().name == "File Browser"

    def test_plugin_icon(self):
        assert FileBrowserPlugin().icon == "◉"

    def test_commands_returns_list(self):
        plugin = self._make_plugin()
        cmds = plugin.commands()
        assert isinstance(cmds, list)
        assert len(cmds) == 3

    def test_commands_have_files_plugin_id(self):
        plugin = self._make_plugin()
        for cmd in plugin.commands():
            assert cmd["plugin_id"] == "files"
            assert callable(cmd["action"])

    def test_handle_command_cd_valid_dir(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._root = "/tmp"
        plugin._widget = mock_widget
        with tempfile.TemporaryDirectory() as d:
            result = plugin.handle_command(f"cd {d}")
        assert result is True

    def test_handle_command_cd_invalid_dir(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._root = "/tmp"
        plugin._widget = mock_widget
        result = plugin.handle_command("cd /nonexistent/path/xyz")
        assert result is True  # command is consumed, silently ignores invalid

    def test_handle_command_open_existing_file(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._root = "/tmp"
        plugin._widget = mock_widget
        with tempfile.NamedTemporaryFile(delete=False) as f:
            tmp = f.name
        try:
            result = plugin.handle_command(f"open {tmp}")
            assert result is True
            mock_widget._worker_preview.assert_called_once_with(tmp)
        finally:
            os.unlink(tmp)

    def test_handle_command_search(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        plugin._widget = mock_widget
        result = plugin.handle_command("search flutter")
        assert result is True
        mock_widget._worker_search.assert_called_once_with("flutter")

    def test_handle_command_unknown_returns_false(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("flutter doctor") is False
        assert plugin.handle_command("git status") is False
        assert plugin.handle_command("") is False

    def test_handle_command_no_widget(self):
        plugin = self._make_plugin()
        plugin._widget = None
        assert plugin.handle_command("cd /tmp") is True  # consumed, no crash
        assert plugin.handle_command("open /tmp/file") is True
        assert plugin.handle_command("search hello") is True


if __name__ == "__main__":
    unittest.main()
