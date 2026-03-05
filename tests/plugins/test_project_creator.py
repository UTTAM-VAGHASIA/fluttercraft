from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from fluttercraft.plugins.project_creator.creator_api import (
    TEMPLATES,
    ProjectConfig,
    Template,
    add_deps_to_pubspec,
    add_icon_config,
    add_linting,
    add_splash_config,
    create_folder_structure,
    detect_platforms,
    get_template,
    get_template_preview,
    is_flutter_installed,
    is_valid_project_name,
)
from fluttercraft.plugins.project_creator.plugin import (
    ProjectCreatorPlugin,
    _FEATURES,
    _PLATFORMS,
    _STEPS,
)
from fluttercraft.plugins.base import PluginContext


# ── is_valid_project_name() ───────────────────────────────────────────────────


class TestIsValidProjectName:
    def test_valid_snake_case(self):
        assert is_valid_project_name("my_app") is True

    def test_valid_single_word(self):
        assert is_valid_project_name("myapp") is True

    def test_valid_with_numbers(self):
        assert is_valid_project_name("app123") is True

    def test_invalid_starts_with_digit(self):
        assert is_valid_project_name("1app") is False

    def test_invalid_has_uppercase(self):
        assert is_valid_project_name("MyApp") is False

    def test_invalid_has_hyphen(self):
        assert is_valid_project_name("my-app") is False

    def test_invalid_has_space(self):
        assert is_valid_project_name("my app") is False

    def test_invalid_empty(self):
        assert is_valid_project_name("") is False

    def test_valid_underscores_and_digits(self):
        assert is_valid_project_name("my_flutter_app_2") is True


# ── Template registry (6.3) ───────────────────────────────────────────────────


class TestTemplateRegistry:
    def test_all_eight_templates_exist(self):
        assert len(TEMPLATES) == 8

    def test_template_ids_are_unique(self):
        ids = [t.id for t in TEMPLATES]
        assert len(ids) == len(set(ids))

    def test_all_templates_have_required_fields(self):
        for tmpl in TEMPLATES:
            assert tmpl.id
            assert tmpl.name
            assert tmpl.description
            assert isinstance(tmpl.state_deps, dict)
            assert isinstance(tmpl.dev_deps, dict)
            assert isinstance(tmpl.folder_structure, list)

    def test_simple_template_has_no_deps(self):
        tmpl = get_template("simple")
        assert tmpl is not None
        assert tmpl.state_deps == {}
        assert tmpl.dev_deps == {}

    def test_bloc_template_has_flutter_bloc(self):
        tmpl = get_template("bloc")
        assert tmpl is not None
        assert "flutter_bloc" in tmpl.state_deps
        assert "equatable" in tmpl.state_deps

    def test_riverpod_template_has_riverpod(self):
        tmpl = get_template("riverpod")
        assert tmpl is not None
        assert "flutter_riverpod" in tmpl.state_deps
        assert "build_runner" in tmpl.dev_deps

    def test_provider_template(self):
        tmpl = get_template("provider")
        assert tmpl is not None
        assert "provider" in tmpl.state_deps

    def test_getx_template(self):
        tmpl = get_template("getx")
        assert tmpl is not None
        assert "get" in tmpl.state_deps

    def test_mobx_template(self):
        tmpl = get_template("mobx")
        assert tmpl is not None
        assert "flutter_mobx" in tmpl.state_deps
        assert "mobx_codegen" in tmpl.dev_deps

    def test_clean_arch_template(self):
        tmpl = get_template("clean_arch")
        assert tmpl is not None
        assert "flutter_bloc" in tmpl.state_deps
        assert "get_it" in tmpl.state_deps
        assert "dartz" in tmpl.state_deps

    def test_mvvm_template(self):
        tmpl = get_template("mvvm")
        assert tmpl is not None
        assert tmpl.state_deps == {}

    def test_get_template_returns_none_for_unknown(self):
        assert get_template("unknown_template") is None

    def test_all_templates_have_lib_in_folder_structure(self):
        for tmpl in TEMPLATES:
            lib_folders = [f for f in tmpl.folder_structure if f.startswith("lib/")]
            assert len(lib_folders) > 0, f"{tmpl.id} has no lib/ folders"


# ── Platform detection (6.2) ──────────────────────────────────────────────────


class TestDetectPlatforms:
    def test_returns_dict_with_all_platform_keys(self):
        with patch("shutil.which", return_value=None):
            result = detect_platforms()
        expected_keys = {"android", "ios", "web", "linux", "windows", "macos"}
        assert set(result.keys()) == expected_keys

    def test_detects_android_via_adb(self):
        def mock_which(cmd):
            return "/usr/bin/adb" if cmd == "adb" else None

        with patch("shutil.which", side_effect=mock_which):
            result = detect_platforms()
        assert result["android"] is True

    def test_detects_android_via_env_var(self):
        with patch("shutil.which", return_value=None):
            with patch.dict(os.environ, {"ANDROID_HOME": "/opt/android"}):
                result = detect_platforms()
        assert result["android"] is True

    def test_detects_web_via_chrome(self):
        def mock_which(cmd):
            return "/usr/bin/google-chrome" if cmd == "google-chrome" else None

        with patch("shutil.which", side_effect=mock_which):
            result = detect_platforms()
        assert result["web"] is True

    def test_detects_linux_on_linux(self):
        with patch("platform.system", return_value="Linux"):
            with patch("shutil.which", return_value=None):
                result = detect_platforms()
        assert result["linux"] is True

    def test_detects_windows_on_windows(self):
        with patch("platform.system", return_value="Windows"):
            with patch("shutil.which", return_value=None):
                result = detect_platforms()
        assert result["windows"] is True

    def test_no_ios_on_linux(self):
        with patch("platform.system", return_value="Linux"):
            with patch("shutil.which", return_value=None):
                result = detect_platforms()
        assert result["ios"] is False
        assert result["macos"] is False

    def test_all_false_when_nothing_detected(self):
        with patch("platform.system", return_value="FreeBSD"):
            with patch("shutil.which", return_value=None):
                with patch.dict(os.environ, {}, clear=True):
                    result = detect_platforms()
        # On FreeBSD, linux/windows/macos/ios should be False
        assert result["windows"] is False
        assert result["ios"] is False


# ── is_flutter_installed() ────────────────────────────────────────────────────


class TestIsFlutterInstalled:
    def test_returns_true_when_flutter_on_path(self):
        with patch("shutil.which", return_value="/usr/bin/flutter"):
            assert is_flutter_installed() is True

    def test_returns_false_when_flutter_missing(self):
        with patch("shutil.which", return_value=None):
            assert is_flutter_installed() is False


# ── add_deps_to_pubspec() (6.4) ───────────────────────────────────────────────


class TestAddDepsToPubspec:
    def _make_pubspec(self, tmp_path: str) -> str:
        content = (
            "name: my_app\n"
            "version: 1.0.0\n"
            "\n"
            "environment:\n"
            "  sdk: '>=3.0.0 <4.0.0'\n"
            "\n"
            "dependencies:\n"
            "  flutter:\n"
            "    sdk: flutter\n"
            "\n"
            "dev_dependencies:\n"
            "  flutter_test:\n"
            "    sdk: flutter\n"
        )
        path = os.path.join(tmp_path, "pubspec.yaml")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_adds_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            ok = add_deps_to_pubspec(path, {"flutter_bloc": "^8.1.6"})
            assert ok is True
            with open(path) as f:
                content = f.read()
            assert "flutter_bloc: ^8.1.6" in content

    def test_adds_dev_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            ok = add_deps_to_pubspec(path, {"build_runner": "^2.4.9"}, dev=True)
            assert ok is True
            with open(path) as f:
                content = f.read()
            assert "build_runner: ^2.4.9" in content

    def test_empty_deps_returns_true_without_modifying(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            with open(path) as f:
                original = f.read()
            ok = add_deps_to_pubspec(path, {})
            assert ok is True
            with open(path) as f:
                assert f.read() == original

    def test_multiple_deps_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            deps = {"flutter_bloc": "^8.1.6", "equatable": "^2.0.5"}
            add_deps_to_pubspec(path, deps)
            with open(path) as f:
                content = f.read()
            assert "flutter_bloc: ^8.1.6" in content
            assert "equatable: ^2.0.5" in content

    def test_returns_false_on_nonexistent_file(self):
        ok = add_deps_to_pubspec("/nonexistent/pubspec.yaml", {"x": "1.0.0"})
        assert ok is False


# ── create_folder_structure() (6.5) ──────────────────────────────────────────


class TestCreateFolderStructure:
    def test_creates_dirs_for_bloc_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpl = get_template("bloc")
            assert tmpl is not None
            ok = create_folder_structure(tmp, tmpl)
            assert ok is True
            assert os.path.isdir(os.path.join(tmp, "lib", "blocs"))
            assert os.path.isdir(os.path.join(tmp, "lib", "screens"))
            assert os.path.isdir(os.path.join(tmp, "lib", "models"))

    def test_creates_dirs_for_clean_arch_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpl = get_template("clean_arch")
            assert tmpl is not None
            ok = create_folder_structure(tmp, tmpl)
            assert ok is True
            assert os.path.isdir(os.path.join(tmp, "lib", "core"))
            assert os.path.isdir(os.path.join(tmp, "lib", "domain", "entities"))
            assert os.path.isdir(os.path.join(tmp, "lib", "presentation", "pages"))

    def test_creates_gitkeep_in_empty_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpl = get_template("bloc")
            assert tmpl is not None
            create_folder_structure(tmp, tmpl)
            blocs_dir = os.path.join(tmp, "lib", "blocs")
            assert os.path.isfile(os.path.join(blocs_dir, ".gitkeep"))

    def test_creates_all_templates_without_error(self):
        for tmpl in TEMPLATES:
            with tempfile.TemporaryDirectory() as tmp:
                ok = create_folder_structure(tmp, tmpl)
                assert ok is True, f"Failed for template {tmpl.id}"


# ── add_linting() ─────────────────────────────────────────────────────────────


class TestAddLinting:
    def test_creates_analysis_options_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = add_linting(tmp)
            assert ok is True
            path = os.path.join(tmp, "analysis_options.yaml")
            assert os.path.isfile(path)
            with open(path) as f:
                content = f.read()
            assert "flutter_lints" in content
            assert "prefer_const_constructors" in content


# ── add_icon_config() / add_splash_config() ───────────────────────────────────


class TestIconAndSplashConfig:
    def _make_pubspec(self, tmp_path: str) -> str:
        content = (
            "name: test\n"
            "dependencies:\n"
            "  flutter:\n"
            "    sdk: flutter\n"
            "dev_dependencies:\n"
            "  flutter_test:\n"
            "    sdk: flutter\n"
        )
        path = os.path.join(tmp_path, "pubspec.yaml")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_add_icon_config_adds_dep_and_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            ok = add_icon_config(path)
            assert ok is True
            with open(path) as f:
                content = f.read()
            assert "flutter_launcher_icons" in content
            assert "image_path" in content

    def test_add_splash_config_adds_dep_and_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._make_pubspec(tmp)
            ok = add_splash_config(path)
            assert ok is True
            with open(path) as f:
                content = f.read()
            assert "flutter_native_splash" in content
            assert "color" in content


# ── get_template_preview() (6.9) ─────────────────────────────────────────────


class TestGetTemplatePreview:
    def test_preview_contains_project_name(self):
        cfg = ProjectConfig(name="my_test_app", template_id="simple")
        preview = get_template_preview(cfg)
        assert "my_test_app" in preview

    def test_preview_contains_lib_folder(self):
        cfg = ProjectConfig(name="app", template_id="bloc")
        preview = get_template_preview(cfg)
        assert "lib/" in preview

    def test_preview_contains_bloc_folders(self):
        cfg = ProjectConfig(name="app", template_id="bloc")
        preview = get_template_preview(cfg)
        assert "blocs/" in preview or "screens/" in preview

    def test_preview_contains_state_deps_for_bloc(self):
        cfg = ProjectConfig(name="app", template_id="bloc")
        preview = get_template_preview(cfg)
        assert "flutter_bloc" in preview

    def test_preview_includes_app_icon_note(self):
        cfg = ProjectConfig(name="app", template_id="simple", app_icon=True)
        preview = get_template_preview(cfg)
        assert "flutter_launcher_icons" in preview

    def test_preview_includes_splash_note(self):
        cfg = ProjectConfig(name="app", template_id="simple", splash_screen=True)
        preview = get_template_preview(cfg)
        assert "flutter_native_splash" in preview

    def test_preview_uses_my_app_when_name_empty(self):
        cfg = ProjectConfig(name="", template_id="simple")
        preview = get_template_preview(cfg)
        assert "my_app" in preview

    def test_preview_works_for_all_templates(self):
        for tmpl in TEMPLATES:
            cfg = ProjectConfig(name="test_app", template_id=tmpl.id)
            preview = get_template_preview(cfg)
            assert "test_app" in preview


# ── ProjectConfig dataclass ───────────────────────────────────────────────────


class TestProjectConfig:
    def test_default_values(self):
        cfg = ProjectConfig()
        assert cfg.name == ""
        assert cfg.org == "com.example"
        assert "android" in cfg.platforms
        assert "ios" in cfg.platforms
        assert cfg.template_id == "simple"
        assert cfg.app_icon is False
        assert cfg.splash_screen is False
        assert cfg.linting is False

    def test_custom_values(self):
        cfg = ProjectConfig(
            name="my_app",
            org="com.mycompany",
            platforms=["android", "web"],
            template_id="bloc",
            app_icon=True,
        )
        assert cfg.name == "my_app"
        assert cfg.org == "com.mycompany"
        assert cfg.platforms == ["android", "web"]
        assert cfg.template_id == "bloc"
        assert cfg.app_icon is True


# ── Wizard constants ───────────────────────────────────────────────────────────


class TestWizardConstants:
    def test_steps_count(self):
        assert len(_STEPS) == 6

    def test_platforms_count(self):
        assert len(_PLATFORMS) == 6

    def test_features_count(self):
        assert len(_FEATURES) == 3

    def test_platform_keys_match_expected(self):
        keys = [p[0] for p in _PLATFORMS]
        assert "android" in keys
        assert "ios" in keys
        assert "web" in keys

    def test_feature_keys(self):
        keys = [f[0] for f in _FEATURES]
        assert "app_icon" in keys
        assert "splash" in keys
        assert "linting" in keys


# ── ProjectCreatorPlugin ──────────────────────────────────────────────────────


class TestProjectCreatorPlugin:
    def _make_plugin(self) -> ProjectCreatorPlugin:
        plugin = ProjectCreatorPlugin()
        ctx = PluginContext(
            work_dir="",
            project_root="",
            config=MagicMock(),
            event_bus=MagicMock(),
            state=MagicMock(),
        )
        plugin.init(ctx)
        return plugin

    def test_plugin_id(self):
        assert ProjectCreatorPlugin().id == "project"

    def test_plugin_name(self):
        assert ProjectCreatorPlugin().name == "Project Creator"

    def test_plugin_icon(self):
        assert ProjectCreatorPlugin().icon == "✦"

    def test_commands_returns_list(self):
        plugin = self._make_plugin()
        cmds = plugin.commands()
        assert isinstance(cmds, list)
        assert len(cmds) > 0

    def test_commands_have_creator_prefix(self):
        plugin = self._make_plugin()
        for cmd in plugin.commands():
            assert cmd["title"].startswith("Creator:")
            assert callable(cmd["action"])

    def test_handle_command_ignores_non_creator(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("flutter doctor") is False
        assert plugin.handle_command("git status") is False

    def test_handle_command_create_with_valid_name(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._creating = False
        plugin._widget = mock_widget
        assert plugin.handle_command("create my_app") is True

    def test_handle_command_new_with_valid_name(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._creating = False
        plugin._widget = mock_widget
        assert plugin.handle_command("new my_project") is True

    def test_handle_command_create_without_name(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("create") is False

    def test_handle_command_unknown_returns_false(self):
        plugin = self._make_plugin()
        assert plugin.handle_command("open project") is False

    def test_handle_command_bare_valid_name_on_step_0(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._creating = False
        mock_widget._step = 0
        plugin._widget = mock_widget
        assert plugin.handle_command("my_test_app") is True

    def test_handle_command_bare_name_not_handled_on_other_steps(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._creating = False
        mock_widget._step = 2  # Platforms step — bare name should not match
        plugin._widget = mock_widget
        assert plugin.handle_command("my_test_app") is False

    def test_handle_command_invalid_name_not_handled(self):
        plugin = self._make_plugin()
        mock_widget = MagicMock()
        mock_widget._creating = False
        mock_widget._step = 0
        plugin._widget = mock_widget
        # "MyApp" is not valid snake_case — should fall through to unknown command
        assert plugin.handle_command("MyApp") is False
