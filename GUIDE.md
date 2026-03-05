# FlutterCraft — User Guide

> **Version:** 0.2.0
> **Framework:** Textual TUI (Python)

---

## Table of Contents

1. [Installation](#installation)
2. [Starting FlutterCraft](#starting-fluttercraft)
3. [Interface Overview](#interface-overview)
4. [Navigation](#navigation)
5. [Plugin Reference](#plugin-reference)
   - [1 — FVM Manager](#1--fvm-manager)
   - [2 — Flutter Commands](#2--flutter-commands)
   - [3 — Git Control](#3--git-control)
   - [4 — Project Creator](#4--project-creator)
   - [5 — File Browser](#5--file-browser)
   - [6 — Workspace Manager](#6--workspace-manager)
   - [7 — CLI Adapters](#7--cli-adapters)
6. [Slash Commands](#slash-commands)
7. [Settings](#settings)
8. [Themes](#themes)
9. [Keyboard Reference](#keyboard-reference)
10. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.10+
- Flutter SDK installed (or use FVM Manager to install it)
- Git (for Git Control plugin)

### Install from PyPI

```bash
pip install fluttercraft
```

### Install in development mode

```bash
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft
cd fluttercraft
pip install -e .
```

---

## Starting FlutterCraft

```bash
fluttercraft start
```

You will see a brief splash screen, then the main dashboard loads.

---

## Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  Header — FlutterCraft  v0.2.0              Theme | Time │
├──────────┬──┬──────────────────────────────────────────┤
│          │  │                                            │
│ Sidebar  │  │           Content Area                    │
│          │  │   (Plugin panel or Welcome screen)         │
│ 1 FVM    │  │                                            │
│ 2 Flutter│  │                                            │
│ 3 Git    │  │                                            │
│ 4 Project│  │                                            │
│ 5 Files  │  │                                            │
│ 6 Space  │  ├────────────────────────────────────────────┤
│ 7 CLI    │  │           Output Panel                     │
├──────────┴──┴────────────────────────────────────────────┤
│  Command Input:  > _                                      │
├─────────────────────────────────────────────────────────┤
│  Footer — context hints                                   │
└─────────────────────────────────────────────────────────┘
```

| Area | Description |
|------|-------------|
| **Sidebar** | Lists all 7 plugins. Click or press `1`–`7` to activate. |
| **Content Area** | Shows the active plugin UI, or the Welcome screen. |
| **Output Panel** | Read-only log of commands, results, and info messages. |
| **Command Input** | Type commands here — plugin commands or built-in slash commands. |
| **Resize handles** | Drag the vertical bar (sidebar width) or horizontal bar (output height). |

---

## Navigation

| Key | Action |
|-----|--------|
| `1`–`7` | Open plugin by number |
| `0` or `Esc` | Return to Welcome screen |
| `Ctrl+P` | Open command palette (fuzzy search all commands) |
| `Ctrl+T` | Open theme picker |
| `Ctrl+,` | Open settings |
| `?` | Open keyboard help overlay |
| `Ctrl+Q` | Quit FlutterCraft |
| `Ctrl+Right/Left` | Resize sidebar |
| `Ctrl+Up/Down` | Resize output panel |

> **Tip:** You can also type `1`–`7` directly in the command input to switch plugins.

---

## Plugin Reference

### 1 — FVM Manager

Manage Flutter versions using [FVM](https://fvm.app).

**Commands (type in the command input while plugin 1 is active):**

| Command | Description |
|---------|-------------|
| `fvm install` | Install a Flutter version (interactive list) |
| `fvm use <version>` | Set global Flutter version |
| `fvm list` | Show installed versions |
| `fvm releases` | Browse all available Flutter releases |
| `fvm remove <version>` | Remove an installed version |
| `fvm doctor` | Check FVM and Flutter health |
| `fvm config` | Show current FVM configuration |

**Prerequisite:** FVM must be installed. If not: `dart pub global activate fvm`

---

### 2 — Flutter Commands

Run Flutter SDK commands against your project.

**Commands:**

| Command | Description |
|---------|-------------|
| `flutter doctor` | Check Flutter installation |
| `flutter run` | Run app (prompts for device) |
| `flutter build apk` | Build Android APK |
| `flutter build ios` | Build iOS app |
| `flutter build web` | Build web app |
| `flutter test` | Run test suite |
| `flutter analyze` | Static analysis |
| `flutter pub get` | Fetch dependencies |
| `flutter pub upgrade` | Upgrade dependencies |
| `flutter clean` | Clean build artifacts |
| `flutter upgrade` | Upgrade Flutter SDK |
| `flutter devices` | List connected devices |
| `flutter create <name>` | Create a new Flutter app |

---

### 3 — Git Control

Full Git workflow inside FlutterCraft.

**Keyboard shortcuts (when plugin 3 is active):**

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate file list |
| `s` | Stage file |
| `u` | Unstage file |
| `a` | Stage all files |
| `c` | Commit (opens message modal) |
| `p` | Push to remote |
| `P` | Pull from remote |
| `f` | Fetch |
| `b` | Branch list |
| `n` | Create new branch |
| `l` | View commit log |
| `z` | Stash push |
| `Z` | Stash pop |
| `r` | Refresh status |

**Commands (via command input):**

```
git branch <name>       Create branch
git switch <name>       Switch branch
git delete <name>       Delete branch
git stash list          List stashes
```

---

### 4 — Project Creator

Create new Flutter projects with a multi-step wizard.

**Steps:**

1. **Name** — enter project name (snake_case)
2. **Organisation** — enter reverse domain (e.g. `com.example`)
3. **Platforms** — select target platforms (Space to toggle, Enter to confirm)
4. **Template** — choose state management pattern
5. **Features** — optional extras (launcher icons, splash screen)
6. **Review** — confirm and create

**Templates available:**

| Template | State Management |
|----------|-----------------|
| `simple` | setState only |
| `bloc` | flutter_bloc |
| `riverpod` | flutter_riverpod |
| `provider` | provider |
| `getx` | get |
| `mobx` | mobx |
| `mvvm` | MVVM architecture |
| `clean_arch` | Clean Architecture |

**Keys during wizard:**

| Key | Action |
|-----|--------|
| `n` or `→` | Next step |
| `b` or `←` | Previous step |
| `Enter` | Select / confirm |
| `Space` | Toggle option |
| `P` | Preview template (folder tree + deps) |

---

### 5 — File Browser

Navigate and manage your project files.

**Keys:**

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move cursor |
| `Enter` or `→` | Open file / expand directory |
| `←` | Collapse directory |
| `Space` | Preview file (syntax highlighted) |
| `Ctrl+O` | Quick open (fuzzy search) |
| `n` | New file |
| `N` | New directory |
| `d` | Delete file/directory |
| `r` | Rename |
| `e` | Open in system editor (`$EDITOR`) |
| `s` | Search content in files |
| `f` | Filter by pattern |
| `R` | Refresh tree |
| `h` | Toggle hidden files |

**Git status** indicators appear next to modified/new/deleted files automatically.

---

### 6 — Workspace Manager

Manage multiple Flutter projects and switch between them.

**Commands:**

| Command | Description |
|---------|-------------|
| `add <path>` | Add a Flutter project to workspace |
| `switch <name>` | Activate a project (updates File Browser + Git) |
| `scan` | Auto-discover Flutter projects in home directory |
| `health` | Check pubspec, Flutter SDK, FVM for active project |

**Keys (when workspace list is focused):**

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate project list |
| `Enter` | Switch to selected project |

**When you switch a project:**
- File Browser automatically navigates to that project's root
- Git Control reloads its status for the new project
- Project context is saved so it restores next time you open FlutterCraft

**Storage:** `~/.fluttercraft/workspace.json`

---

### 7 — CLI Adapters

Chat with AI CLI tools (Claude Code, Gemini CLI, OpenCode) without leaving FlutterCraft.

**Supported tools:**

| Tool | Install command |
|------|----------------|
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| Gemini CLI | `npm install -g @google/gemini-cli` |
| OpenCode | See [opencode.ai](https://opencode.ai) |

FlutterCraft auto-detects which tools are on your PATH. Missing tools are shown as greyed-out tabs.

**Keys / actions:**

| Key | Action |
|-----|--------|
| Click tab | Switch adapter (Claude / Gemini / OpenCode) |
| Type + `Enter` | Send message |
| `Ctrl+N` | Start new session |
| `Ctrl+H` | Toggle session history panel |
| `Ctrl+L` | Clear output |

**Commands (via command input):**

```
ask <message>         Send a message to the active adapter
switch claude         Switch to Claude Code
switch gemini         Switch to Gemini CLI
switch opencode       Switch to OpenCode
new                   Start new session
history               Toggle history panel
clear                 Clear output
```

**Project context auto-injection:** When you have an active workspace project, FlutterCraft automatically includes the project name, Flutter version, and git branch in each session so the AI has context.

**Session persistence:** All sessions are saved to `~/.fluttercraft/cli_sessions.json` and restored on next launch.

---

## Slash Commands

Type these in the command input (starting with `/`):

| Command | Action |
|---------|--------|
| `/help` | Open keyboard help overlay |
| `/clear` | Clear the output panel |
| `/theme` | Open theme picker |
| `/settings` | Open settings modal |
| `/quit` | Quit FlutterCraft |

---

## Settings

Open with `Ctrl+,` or type `/settings`.

| Setting | Description |
|---------|-------------|
| Notifications | Toggle toast notifications |
| Command Palette | Toggle `Ctrl+P` command palette |
| Theme | Shortcut to open theme picker |

---

## Themes

FlutterCraft ships with **13 built-in themes** (7 dark, 6 light).

Open the theme picker with `Ctrl+T` or type `/theme`. Use `↑`/`↓` to preview live, `Enter` to confirm, `Escape` to restore original.

| Theme | Style |
|-------|-------|
| Tokyo Night | Dark — blue/purple |
| Tokyo Night Storm | Dark — deeper blue |
| Dracula | Dark — purple/pink |
| One Dark Pro | Dark — grey/blue |
| Monokai Pro | Dark — warm |
| Gruvbox Dark | Dark — earthy |
| Nord | Dark — arctic blue |
| GitHub Light | Light — clean white |
| Solarized Light | Light — warm |
| … and more | |

---

## Keyboard Reference

Press `?` at any time to open the full in-app keyboard reference overlay.

---

## Troubleshooting

### App won't start

```bash
# Check for import errors
python3 -c "from fluttercraft.app import FlutterCraftApp"

# Install dependencies
pip install -e .
```

### Error log

All unhandled errors are written to:
```
~/.fluttercraft/error.log
```
Check this file first when something behaves unexpectedly.

### ANSI escape sequences in output

This is fixed in v0.2.0. If you see `^[[...` characters, make sure you are on the latest version.

### FVM not found

```bash
dart pub global activate fvm
# Add to PATH: export PATH="$PATH:$HOME/.pub-cache/bin"
```

### AI CLI adapter not detected

Make sure the binary is on your PATH:
```bash
which claude    # or: which gemini / which opencode
```

### Workspace shows "No projects"

Use `scan` in the Workspace plugin to auto-discover projects, or `add <absolute-path>` to add one manually.

### File Browser shows wrong project

Switch projects in the Workspace plugin (plugin 6) — it automatically updates the File Browser.

---

## Data Storage

All FlutterCraft data is stored in `~/.fluttercraft/`:

| File | Contents |
|------|---------|
| `workspace.json` | Project list + last-active project |
| `cli_sessions.json` | CLI adapter conversation history |
| `config.json` | App configuration + feature flags |
| `theme.json` | Active theme preference |
| `error.log` | Runtime error log |
