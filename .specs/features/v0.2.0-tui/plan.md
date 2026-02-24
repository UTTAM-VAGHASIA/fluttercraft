# FlutterCraft v0.2.0 — TUI Rewrite Plan

## Branch Setup (Do This First)

**Current branch:** `main`
**Target branch:** `feature/v0.2.0-tui`

Run these commands before writing a single line of code:

```bash
# Create and switch to the working branch
git checkout -b feature/v0.2.0-tui

# Verify
git branch
# Expected output: * feature/v0.2.0-tui
```

> Untracked files carry over automatically. Nothing is lost.
>
> **Why not branch off `feature/v0.1.3-signature-ui`?**
> That branch has older versions of AGENTS.md, CLAUDE.md, and .context/ that conflict
> with the v0.2.0-tui planning files already set up on main. Branching from main avoids
> merge conflicts and keeps the setup clean. The v0.1.3 branch is available as a read-only
> reference via `git show origin/feature/v0.1.3-signature-ui:<file>`.

---

## Overview

Complete rewrite of FlutterCraft from a Rich + prompt_toolkit CLI to a full Textual TUI application. Inspired by [Sidecar](https://github.com/marcus/sidecar) architecture but built for Flutter/FVM development workflows.

**Version:** 0.2.0
**Framework:** Textual (Python)
**Branch:** `feature/v0.2.0-tui` (off `feature/v0.1.3-signature-ui`)

---

## Target Architecture

```
fluttercraft/
├── app.py                          # Main Textual App
├── screens/                        # Textual Screens
│   ├── dashboard.py                # Main dashboard screen
│   ├── project_wizard.py           # Project creation wizard
│   └── settings.py                 # Settings screen
├── widgets/                        # Reusable UI components
│   ├── header.py                   # Status bar: Flutter ver, FVM ver, platform
│   ├── footer.py                   # Keybindings bar
│   ├── command_input.py            # Command input with autocomplete
│   ├── output_panel.py             # Scrollable command output
│   ├── sidebar.py                  # Plugin tab list
│   ├── modal.py                    # Declarative modal builder
│   └── spinner.py                  # Loading indicators
├── plugins/                        # Plugin system
│   ├── base.py                     # Plugin interface + registry + lifecycle
│   ├── fvm_manager/                # FVM plugin
│   ├── flutter_commands/           # Flutter command runner plugin
│   ├── project_creator/            # Project creation + templates plugin
│   ├── git_control/                # Git management plugin
│   ├── file_browser/               # File browser plugin
│   ├── workspace/                  # Workspace manager plugin
│   ├── cli_adapter/                # External CLI integration plugin
│   └── icon_generator/             # App icon setup plugin
├── adapters/                       # CLI adapters
│   ├── base.py                     # Adapter interface
│   ├── detect.py                   # Auto-detect available CLIs
│   ├── claude.py                   # Claude Code adapter
│   ├── gemini.py                   # Gemini CLI adapter
│   └── opencode.py                 # OpenCode adapter
├── core/                           # Core infrastructure
│   ├── events.py                   # Event bus (pub/sub)
│   ├── config.py                   # Config manager
│   ├── state.py                    # Persistent state
│   ├── keymap.py                   # Key binding registry
│   └── platform.py                 # Platform detection
├── themes/                         # Theme system (migrated)
│   ├── theme.py                    # Theme dataclass
│   ├── manager.py                  # ThemeManager singleton
│   ├── professional.py             # Built-in themes
│   └── styles.tcss                 # Textual CSS base styles
├── commands/                       # Command registry (reused from v0.1.x)
│   └── core/                       # Registry, executor, models, base
└── main.py                         # Entry point
```

---

## Phase 1 — TUI Shell & Core Infrastructure

**Goal:** Replace prompt_toolkit REPL with a working Textual app that matches current functionality.

| Step | What | Details |
|------|------|---------|
| 1.1 | Textual App skeleton | `FlutterCraftApp`, base screen layout, CSS foundation |
| 1.2 | Event bus | Typed pub/sub: `file_changed`, `git_changed`, `session_update`, `focus_changed`, `refresh_needed`, `error` |
| 1.3 | Config manager | `~/.fluttercraft/config.json`, dot-notation access, deep merge, default schema |
| 1.4 | State persistence | `~/.fluttercraft/state.json`, per-project state, active plugin, pane widths, thread-safe |
| 1.5 | Platform utils | Migrate existing + add device/toolchain detection |
| 1.6 | Header widget | Flutter ver, FVM ver, platform, active project, git branch — auto-refresh via events |
| 1.7 | Footer widget | Context-aware keybinding hints, changes per focused plugin |
| 1.8 | Command input widget | Text input with history, fuzzy autocomplete from registry |
| 1.9 | Output panel widget | Scrollable rich text, real-time subprocess streaming, ANSI support |
| 1.10 | Sidebar widget | Plugin tab list with icons, keyboard nav (1-9), active indicator |
| 1.11 | Draggable panes | Resizable split views (sidebar <-> content <-> output), persist widths |
| 1.12 | Mouse support | Click to focus, click sidebar tabs, scroll output, resize panes |
| 1.13 | Theme integration | Migrate 13 themes to Textual CSS variables, live switching |
| 1.14 | Cross-platform | Linux, macOS, Windows — no platform guards |

**Testing (after each step, before commit):**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 1.1 | Manual | App launches, shows empty layout, Ctrl+Q quits |
| 1.2 | Unit + Manual | `tests/core/test_events.py` — subscribe, publish, unsubscribe, typed events |
| 1.3 | Unit | `tests/core/test_config.py` — load defaults, dot-notation get/set, file persistence |
| 1.4 | Unit | `tests/core/test_state.py` — save/load, per-project keys, thread safety |
| 1.5 | Unit | `tests/core/test_platform.py` — platform detection, toolchain detection |
| 1.6 | Widget + Manual | `tests/widgets/test_header.py` — renders version info; Manual: visually correct |
| 1.7 | Widget + Manual | `tests/widgets/test_footer.py` — shows keybindings; Manual: visually correct |
| 1.8 | Widget + Manual | `tests/widgets/test_command_input.py` — input, history, autocomplete; Manual: type and submit |
| 1.9 | Widget + Manual | `tests/widgets/test_output_panel.py` — append text, scroll, ANSI; Manual: run a command |
| 1.10 | Widget + Manual | `tests/widgets/test_sidebar.py` — tab rendering, keyboard nav; Manual: press 1-9 |
| 1.11 | Manual | Drag pane borders with mouse, verify resize persists |
| 1.12 | Manual | Click sidebar tabs, scroll output with mouse wheel |
| 1.13 | Unit + Manual | `tests/themes/test_manager.py` — theme switching; Manual: visual theme change |
| 1.14 | Manual | Launch on Linux/macOS/Windows — no crashes, layout renders |

**Commits:**
```
feat(tui): scaffold Textual app with base layout and CSS
test(tui): add app skeleton tests
feat(core): implement event bus with typed events
test(core): add event bus tests
feat(core): implement config manager and state persistence
test(core): add config and state tests
feat(tui): implement header, footer, sidebar widgets
test(tui): add widget tests for header, footer, sidebar
feat(tui): implement command input with fuzzy autocomplete
test(tui): add command input tests
feat(tui): implement output panel with real-time streaming
test(tui): add output panel tests
feat(tui): add draggable panes and mouse support
feat(tui): migrate theme system to Textual CSS
test(themes): add theme migration tests
feat(tui): enable cross-platform support
```

**-> PUSH (backup: working TUI shell + tests)**

```
## Git Command Required — Phase 1 Push

You should be on: feature/v0.2.0-tui
Verify with: git branch

Run:
    git push -u origin feature/v0.2.0-tui

Expected: branch pushed to remote, tracking set up.
```

---

## Phase 2 — Plugin Architecture & Core Systems

**Goal:** Build the modular plugin system so all features are independent panels.

| Step | What | Details |
|------|------|---------|
| 2.1 | Plugin interface | `Plugin` base: `id`, `name`, `icon`, `init(ctx)`, `start()`, `stop()`, `compose()`, `update(event)`, `commands()`, `is_focused`, `focus_context` |
| 2.2 | Plugin registry | Lifecycle (init -> start -> stop), silent degradation, panic recovery, `reinit()` for project switching |
| 2.3 | Plugin context | Shared bag: `work_dir`, `project_root`, `config`, `event_bus`, `adapters`, `keymap`, `state` |
| 2.4 | Declarative modal system | Builder: `Modal("Title").section(text).section(input).buttons("OK", "Cancel")`, priority stack |
| 2.5 | Command palette | **Ctrl+P** global fuzzy search across all commands from all plugins |
| 2.6 | Keybinding registry | Default bindings + user overrides via `keymap.overrides`, context-aware per plugin |
| 2.7 | Feature flags | Runtime toggle: `features.is_enabled("notes")`, config-driven + CLI override |
| 2.8 | Notification system | Toast notifications (success/error/info), auto-dismiss, stacked |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 2.1 | Unit | `tests/plugins/test_base.py` — Plugin ABC, required methods, init/start/stop lifecycle |
| 2.2 | Unit | `tests/plugins/test_base.py` — Registry: register, silent failure, panic recovery, reinit |
| 2.3 | Unit | `tests/plugins/test_base.py` — PluginContext creation, field access |
| 2.4 | Widget + Manual | `tests/widgets/test_modal.py` — builder API, sections, buttons; Manual: modal renders centered |
| 2.5 | Manual | Ctrl+P opens palette, type to fuzzy search, Enter selects, Escape closes |
| 2.6 | Unit | `tests/core/test_keymap.py` — register bindings, user overrides, context filtering |
| 2.7 | Unit | `tests/core/test_features.py` — enable/disable flags, config-driven |
| 2.8 | Manual | Trigger a notification, verify toast appears and auto-dismisses |

**Commits:**
```
feat(plugins): implement plugin interface with lifecycle and context
test(plugins): add plugin interface and registry tests
feat(plugins): implement registry with silent degradation and panic recovery
feat(tui): implement declarative modal system with priority stack
test(tui): add modal system tests
feat(tui): implement command palette with Ctrl+P fuzzy search
feat(core): implement keybinding registry with context-aware activation
test(core): add keybinding registry tests
feat(core): add feature flags and notification system
test(core): add feature flag tests
```

**-> PUSH (backup: plugin architecture ready + tests)**

```
## Git Command Required — Phase 2 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 3 — FVM Manager Plugin

**Goal:** Full FVM management as a plugin panel.

| Step | What | Details |
|------|------|---------|
| 3.1 | Plugin shell | Panel: installed versions list (left) + actions/details (right) |
| 3.2 | Install/Uninstall FVM | Cross-platform install with progress bar |
| 3.3 | Releases browser | Scrollable table by channel (stable/beta/dev/all), filterable, sortable |
| 3.4 | Version install | Install specific SDK version, progress tracking, cancel support |
| 3.5 | Version switching | `fvm use <version>` project or global, confirmation modal |
| 3.6 | Version removal | `fvm remove <version>` with confirmation modal |
| 3.7 | FVM doctor | Health check with status indicators |
| 3.8 | FVM config | `.fvmrc` editor, flavor management |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 3.1 | Widget + Manual | Plugin panel renders, split layout works |
| 3.2 | Unit + Manual | `tests/plugins/test_fvm_manager.py` — install flow logic; Manual: actually install/uninstall FVM |
| 3.3 | Unit + Manual | Releases parsing, channel filtering; Manual: view real releases list |
| 3.4 | Manual | Install a Flutter SDK version via FVM, verify progress shows |
| 3.5 | Manual | Switch Flutter version with `fvm use`, verify header updates |
| 3.6 | Manual | Remove a version, confirm modal appears, version removed |
| 3.7 | Manual | Run FVM doctor, verify output displays correctly |
| 3.8 | Manual | Edit .fvmrc, verify changes saved |

**Commits:**
```
feat(fvm): implement FVM manager plugin with version listing
test(fvm): add FVM plugin unit tests
feat(fvm): add releases browser with channel filtering
feat(fvm): add install, switch, and remove version flows
feat(fvm): add FVM doctor and config management
```

**-> PUSH**

```
## Git Command Required — Phase 3 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 4 — Flutter Command Runner Plugin

**Goal:** Run all Flutter commands from the TUI.

| Step | What | Details |
|------|------|---------|
| 4.1 | Plugin shell | Command categories (left) + output area (right) |
| 4.2 | `flutter doctor` | Parsed output with status indicators |
| 4.3 | `flutter upgrade` | Upgrade with progress, auto-refresh header |
| 4.4 | `flutter devices` | Live device table, auto-refresh, device selection |
| 4.5 | `flutter run` | Run on device, real-time output, hot reload (r) / restart (R) / quit (q) key forwarding |
| 4.6 | `flutter build` | Build for platform (apk/ipa/web/windows/linux/macos), progress |
| 4.7 | `flutter test` | Parsed results (pass/fail/skip), filter by file |
| 4.8 | `flutter analyze` | Issue list with severity indicators |
| 4.9 | `flutter pub` | `pub get`, `pub upgrade`, `pub outdated` table |
| 4.10 | `flutter clean` | Clean with confirmation |
| 4.11 | `flutter create` | Quick create (bridges to project creator Phase 6) |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 4.1 | Widget + Manual | Plugin panel renders with command categories |
| 4.2 | Unit + Manual | `tests/plugins/test_flutter_commands.py` — output parsing; Manual: run `flutter doctor` |
| 4.3 | Manual | Run `flutter upgrade`, verify progress bar and header refresh |
| 4.4 | Manual | View devices list, verify auto-refresh |
| 4.5 | Manual | Run app on a device, press r for hot reload, R for restart, q to quit |
| 4.6 | Manual | Build APK/web, verify progress and success message |
| 4.7 | Manual | Run tests on a Flutter project, verify pass/fail display |
| 4.8 | Manual | Run analyze, verify issue list with severities |
| 4.9 | Manual | Run `pub get`, `pub outdated`, verify table display |
| 4.10 | Manual | Run clean, verify confirmation modal appears |
| 4.11 | Manual | Quick create bridges to project creator |

**Commits:**
```
feat(flutter): implement flutter command runner plugin
test(flutter): add flutter commands unit tests
feat(flutter): add doctor, upgrade, and devices commands
feat(flutter): add run command with hot reload key forwarding
feat(flutter): add build, test, and analyze commands
feat(flutter): add pub and clean commands
```

**-> PUSH (major milestone: full Flutter CLI in TUI + tests)**

```
## Git Command Required — Phase 4 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 5 — Git Control Plugin

**Goal:** Full git management from TUI.

| Step | What | Details |
|------|------|---------|
| 5.1 | Plugin shell | Branch info (top) + changes list (left) + diff viewer (right) |
| 5.2 | Status display | Staged, unstaged, untracked with icons and colors |
| 5.3 | Diff viewer | Side-by-side or unified, toggle keybinding, syntax highlighted |
| 5.4 | Stage/Unstage | File selection, bulk stage, per-hunk staging |
| 5.5 | Commit | Modal with message input, conventional commit prefix, amend option |
| 5.6 | Push/Pull | Push, pull (rebase option), fetch, force push with confirmation |
| 5.7 | Branch management | List, create, switch, delete, merge with conflict indicator |
| 5.8 | Log viewer | Commit history with graph, filterable |
| 5.9 | Stash | Stash, list, pop, apply, drop |
| 5.10 | File watching | fsnotify/polling hybrid, auto-refresh on changes |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 5.1 | Widget + Manual | Plugin panel renders branch info + split layout |
| 5.2 | Unit + Manual | `tests/plugins/test_git_control.py` — status parsing; Manual: shows real git status |
| 5.3 | Manual | View diff of a changed file, toggle side-by-side/unified |
| 5.4 | Manual | Stage a file, unstage it, bulk stage all |
| 5.5 | Manual | Open commit modal, type message, commit succeeds |
| 5.6 | Manual | Push to remote, pull with changes, force push shows confirmation |
| 5.7 | Manual | Create branch, switch, delete, merge |
| 5.8 | Manual | View commit log, filter by author |
| 5.9 | Manual | Stash changes, list stashes, pop a stash |
| 5.10 | Manual | Edit a file externally, verify auto-refresh in TUI |

**Commits:**
```
feat(git): implement git control plugin with status display
test(git): add git control unit tests
feat(git): add diff viewer with side-by-side and unified modes
feat(git): add stage, unstage, commit, and push flows
feat(git): add branch management and log viewer
feat(git): add stash support and file watching auto-refresh
```

**-> PUSH**

```
## Git Command Required — Phase 5 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 6 — Project Creator Plugin + Templates + Icons

**Goal:** Guided Flutter project creation with templates and state management.

| Step | What | Details |
|------|------|---------|
| 6.1 | Wizard screen | Multi-step: name -> org -> platforms -> template -> state mgmt -> features |
| 6.2 | Platform detection | Auto-detect Android SDK, Xcode, Chrome, Windows/Linux toolchain |
| 6.3 | Template registry | `clean_architecture`, `mvvm`, `simple`, `bloc`, `riverpod`, `getx`, `provider`, `mobx` |
| 6.4 | State management | Auto-add pubspec deps + boilerplate generation |
| 6.5 | Folder structure | Organized lib/, test/, assets/ per template |
| 6.6 | App icon setup | Icon image -> `flutter_launcher_icons` for all platforms |
| 6.7 | Splash screen | Optional: `flutter_native_splash` generation |
| 6.8 | Post-creation | `flutter pub get`, open in editor, next-steps guide |
| 6.9 | Template preview | Preview folder structure and sample code before creation |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 6.1 | Widget + Manual | Wizard renders, step navigation works (next/back) |
| 6.2 | Unit + Manual | `tests/plugins/test_project_creator.py` — detection logic; Manual: shows correct platforms |
| 6.3 | Unit | Template registry returns correct templates, metadata is complete |
| 6.4 | Unit + Manual | Correct deps added to pubspec; Manual: create a Bloc project, verify boilerplate |
| 6.5 | Unit + Manual | Folder structure matches template; Manual: inspect generated project |
| 6.6 | Manual | Provide an icon image, verify icons generated for all platforms |
| 6.7 | Manual | Enable splash screen, verify native splash generated |
| 6.8 | Manual | After creation: pub get runs, editor opens, next-steps guide shows |
| 6.9 | Manual | Preview a template before creating, verify folder tree display |

**Commits:**
```
feat(creator): implement project creation wizard screen
test(creator): add project creator unit tests
feat(creator): add platform detection and template registry
feat(creator): implement state management templates (bloc, riverpod, getx, provider, mobx)
feat(creator): add folder structure generation and template preview
feat(creator): add app icon and splash screen generation
feat(creator): add post-creation setup and editor launch
```

**-> PUSH (major milestone: project creation works + tests)**

```
## Git Command Required — Phase 6 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 7 — File Browser Plugin

**Goal:** Navigate project files from TUI.

| Step | What | Details |
|------|------|---------|
| 7.1 | Tree view | Collapsible directory tree with file icons |
| 7.2 | File preview | Syntax highlighted preview (right panel) |
| 7.3 | Quick open | Ctrl+O fuzzy file search |
| 7.4 | File operations | Create, rename, delete, copy, move with confirmation |
| 7.5 | Open in editor | Open in configured editor |
| 7.6 | Git integration | File git status inline in tree |
| 7.7 | Filter/search | Pattern filter, content search (grep) |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 7.1 | Widget + Manual | `tests/plugins/test_file_browser.py` — tree building; Manual: navigate a real project |
| 7.2 | Manual | Click a .dart file, verify syntax highlighted preview |
| 7.3 | Manual | Ctrl+O opens fuzzy search, type filename, Enter opens it |
| 7.4 | Manual | Create a file, rename it, delete it — confirmation modals appear |
| 7.5 | Manual | Open file in editor, verify editor launches |
| 7.6 | Manual | Modified files show git status icon in tree |
| 7.7 | Manual | Filter tree by "*.dart", search for "class" in files |

**Commits:**
```
feat(browser): implement file browser plugin with tree view
test(browser): add file browser unit tests
feat(browser): add file preview with syntax highlighting
feat(browser): add quick open, file operations, and editor integration
feat(browser): add git status indicators and content search
```

**-> PUSH**

```
## Git Command Required — Phase 7 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 8 — Workspace Manager Plugin

**Goal:** Multi-project management.

| Step | What | Details |
|------|------|---------|
| 8.1 | Project list | Flutter projects with status (last opened, versions) |
| 8.2 | Project switching | Switch active project, `reinit()` all plugins |
| 8.3 | Project discovery | Auto-scan for `pubspec.yaml` in common dirs |
| 8.4 | Per-project state | Remember active plugin, pane widths, files per project |
| 8.5 | Per-project theme | Optional theme override per project |
| 8.6 | Recent projects | Quick access list |
| 8.7 | Project health | Dashboard: doctor status, outdated deps, analyzer issues |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 8.1 | Widget + Manual | `tests/plugins/test_workspace.py` — project list rendering; Manual: view projects |
| 8.2 | Manual | Switch project, verify all plugins reload with new context, header updates |
| 8.3 | Manual | Auto-discovery finds Flutter projects in home directory |
| 8.4 | Manual | Switch project, change active plugin, switch back — state restored |
| 8.5 | Manual | Set per-project theme, verify it applies only to that project |
| 8.6 | Manual | Recent projects list shows correct order |
| 8.7 | Manual | Project health shows doctor/deps/analyzer status |

**Commits:**
```
feat(workspace): implement workspace manager with project list
test(workspace): add workspace manager unit tests
feat(workspace): add project switching with plugin reinit
feat(workspace): add project discovery and per-project state
feat(workspace): add recent projects and project health dashboard
```

**-> PUSH**

```
## Git Command Required — Phase 8 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 9 — CLI Adapter Plugin (Sidecar-like)

**Goal:** Integrate AI CLIs as embedded panels with full session management.

| Step | What | Details |
|------|------|---------|
| 9.1 | Adapter interface | `CLIAdapter`: `detect()`, `start_session()`, `send()`, `stream_output()`, `stop()`, `sessions()`, `messages()` |
| 9.2 | Auto-detection | Scan PATH for `claude`, `gemini`, `opencode` binaries |
| 9.3 | Claude adapter | Spawn process, pipe I/O, parse output |
| 9.4 | Gemini adapter | Same for Gemini CLI |
| 9.5 | OpenCode adapter | Same for OpenCode |
| 9.6 | CLI panel | Output (scrollable, ANSI) + input, tabbed adapter switching |
| 9.7 | Session management | Multiple concurrent sessions, switch, naming |
| 9.8 | Session persistence | Save/resume across restarts |
| 9.9 | Session history | Browse past sessions |
| 9.10 | Conversation viewer | Read-only message view with timestamps |
| 9.11 | Context auto-passing | Inject project path, Flutter/FVM/git info into sessions |
| 9.12 | Embedded terminal | General-purpose PTY pane for arbitrary commands |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 9.1 | Unit | `tests/adapters/test_detect.py` — adapter interface, detect method |
| 9.2 | Unit + Manual | Detection logic; Manual: verify detected CLIs match installed ones |
| 9.3 | Unit + Manual | `tests/adapters/test_claude.py` — spawn/pipe logic; Manual: start Claude session, send message |
| 9.4 | Unit + Manual | `tests/adapters/test_gemini.py`; Manual: start Gemini session |
| 9.5 | Unit + Manual | `tests/adapters/test_opencode.py`; Manual: start OpenCode session |
| 9.6 | Manual | CLI panel renders, type message, output streams, switch adapter tabs |
| 9.7 | Manual | Start 2 sessions, switch between them, verify independent state |
| 9.8 | Manual | Close app, reopen, verify sessions can be resumed |
| 9.9 | Manual | Browse past sessions, view conversation history |
| 9.10 | Manual | Open conversation viewer, verify messages with timestamps |
| 9.11 | Manual | Start CLI session, verify project context auto-injected |
| 9.12 | Manual | Open embedded terminal, run `ls`, `git status`, verify output |

**Commits:**
```
feat(adapters): implement CLI adapter interface and auto-detection
test(adapters): add adapter detection and interface tests
feat(adapters): add Claude Code, Gemini, and OpenCode adapters
test(adapters): add individual adapter tests
feat(tui): implement CLI panel with multi-session tabs
feat(adapters): add session persistence and history viewer
feat(adapters): add conversation viewer and context auto-passing
feat(tui): implement embedded terminal pane
```

**-> PUSH**

```
## Git Command Required — Phase 9 Push

You should be on: feature/v0.2.0-tui

Run:
    git push

Expected: commits pushed to origin/feature/v0.2.0-tui.
```

---

## Phase 10 — Polish & Release v0.2.0

**Goal:** Production quality.

| Step | What | Details |
|------|------|---------|
| 10.1 | Settings screen | Theme, keybindings, default adapter, editor, templates, animations |
| 10.2 | Error handling | Silent degradation, error modals, crash recovery |
| 10.3 | Intro animation | Startup ASCII art wipe-in, slide-in panels |
| 10.4 | Help system | `?` key contextual help, help modal per plugin |
| 10.5 | Tests | Unit (core, plugins, commands), integration (TUI), CI |
| 10.6 | Performance | Lazy plugin loading, async subprocess, debounced watching |
| 10.7 | Accessibility | Keyboard-only nav, high contrast theme |
| 10.8 | Docs | README rewrite, CHANGELOG, usage guide, GIF demos |
| 10.9 | Release | Version 0.2.0, setup.py, PyPI, git tag |

**Testing:**

| Step | Test Type | What to Test |
|------|-----------|--------------|
| 10.1 | Manual | Settings screen renders all categories, changes persist |
| 10.2 | Manual | Disable a plugin, verify it fails silently; crash recovery works |
| 10.3 | Manual | App startup shows animation, ASCII art wipe-in |
| 10.4 | Manual | Press `?` in any plugin, verify contextual help modal |
| 10.5 | Automated | Full test suite: `python -m pytest tests/ -v` — all pass |
| 10.6 | Manual | App starts fast (<2s), no lag switching plugins |
| 10.7 | Manual | Navigate entire app with keyboard only, no mouse required |
| 10.8 | Manual | README accurate, CHANGELOG complete, GIFs render |
| 10.9 | Manual | `pip install fluttercraft==0.2.0` works, `fluttercraft start` launches |

**Commits:**
```
feat(tui): implement settings screen and help system
feat(core): add error handling with silent degradation
feat(tui): add intro animation and accessibility
test: full test suite pass
docs: rewrite README, CHANGELOG, usage guide
chore: bump version to 0.2.0, tag release
```

**-> PUSH + TAG v0.2.0**

```
## Git Command Required — Phase 10 Final Push + Tag

You should be on: feature/v0.2.0-tui

Run these one at a time:

    git push

    git tag v0.2.0

    git push origin v0.2.0

Expected: tag v0.2.0 appears on remote. Then open a PR to merge feature/v0.2.0-tui → main.
```

---

## Dependencies

```python
# setup.py
install_requires=[
    "textual>=0.85.0",      # TUI framework
    "typer[all]",            # CLI entry point
    "rich",                  # Rich rendering (Textual uses internally)
    "rapidfuzz>=3.0.0",     # Fuzzy matching
    "pyfiglet",             # ASCII art
    "colorama",             # Windows color support
    "watchdog>=3.0.0",      # File system watching (git plugin, workspace)
]
```

## Git Strategy

```
main (stable v0.1.3)
 └── feature/v0.2.0-tui   ← ALL work here, branched from main
      ├── Push after each phase (see per-phase Git Command blocks above)
      ├── Merge to main at v0.2.0 via PR
      └── Tag: v0.2.0
```

**Agent git policy:**
- Agent NEVER runs git commands — only provides them for the user to copy-paste
- Agent states current + target branch before every git command block
- User runs the command, confirms result, then agent continues

## Feature Matrix

| Feature | Phase | Sidecar Equivalent |
|---------|-------|--------------------|
| Textual TUI shell | 1 | app/ |
| Event bus | 1 | event/ |
| Config + State | 1 | config/ + state/ |
| Draggable panes | 1 | Pane state |
| Mouse support | 1 | mouse/ |
| Theming (13 themes) | 1 | styles/ + themes/ |
| Plugin architecture | 2 | plugin/ |
| Declarative modals | 2 | modal/ |
| Command palette | 2 | palette/ |
| Keybinding registry | 2 | keymap/ |
| Feature flags | 2 | features/ |
| FVM manager | 3 | -- (FlutterCraft-specific) |
| Flutter commands | 4 | -- (FlutterCraft-specific) |
| Git control | 5 | plugins/gitstatus/ |
| Project creator | 6 | -- (FlutterCraft-specific) |
| File browser | 7 | plugins/filebrowser/ |
| Workspace manager | 8 | plugins/workspace/ |
| CLI adapters | 9 | adapter/ |
| Session management | 9 | adapter/ sessions |
| Conversation viewer | 9 | plugins/conversations/ |
| Embedded terminal | 9 | tty/ |
| Settings | 10 | Config UI |
