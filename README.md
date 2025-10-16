# FlutterCraft 🛠️🚀

**Automate your Flutter app setup like a pro.**  
From folder structure to backend integration, from icons to GitHub repo setup — FlutterCraft does it all, in one CLI command.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Build](https://github.com/UTTAM-VAGHASIA/fluttercraft/actions/workflows/cli-check.yml/badge.svg)
![Stars](https://img.shields.io/github/stars/UTTAM-VAGHASIA/fluttercraft)
[![PyPI version](https://badge.fury.io/py/fluttercraft.svg)](https://badge.fury.io/py/fluttercraft)
[![PyPI Downloads](https://static.pepy.tech/badge/fluttercraft)](https://pepy.tech/project/fluttercraft)

---

## ✨ Features

- 🎨 **Beautiful CLI Interface** - Modern, Gemini-inspired design with ASCII art
- 📦 **Flutter Version Management** - Upgrade Flutter with real-time progress tracking
- 🔄 **FVM Integration** - Install, manage, and switch between Flutter SDK versions
- ⚡ **Animated Loading Indicators** - Visual feedback during command execution
- 📊 **Smart Version Tracking** - See available updates at a glance
- 🛠️ **Comprehensive Help System** - Built-in help for all commands
- ⌨️ **Auto-completion** - Tab completion with live command suggestions
- 🎯 **Error Handling** - Clear, actionable error messages with debugging info

---

## 🤖 CLI Status

The interactive CLI features a **beautiful, modern interface**! 🎨

### ✨ Beautiful Gemini-Style Interface

- **🎨 ANSI Shadow ASCII Art**: Modern, bold FlutterCraft branding
- **📦 Bordered Input Box**: Professional Frame-based input with automatic borders
- **📋 Permanent Completion Menu**: Dedicated area below input that updates live as you type
- **⌨️ Interactive Navigation**: 
  - ↑/↓ arrows to navigate completions with visual highlighting
  - Tab to fill input without submitting
  - Enter to select from menu or submit command
- **⚡ Slash Commands**: Modern command syntax (`/quit`, `/clear`, `/help`)
- **🔄 Dynamic Updates**: Header automatically updates when Flutter version changes
- **📍 Smart Footer**: Shows current path and git branch/status
- **🎯 Live Completions**: Menu updates instantly as you type, showing command descriptions

### ✅ Current Features (v0.1.2)

#### NOTE: The current CLI is only supported on windows. Support for macOS and Linux will be added in the future.

#### 🚀 Flutter Commands
- **`flutter upgrade`** - Upgrade Flutter to the latest version
  - Support for `--force`, `--verify-only`, `--continue`, `--verbose`
  - Real-time output with animated loading spinner
  - Automatic version tracking after upgrade
  - Built-in help with `flutter upgrade --help`

#### 🔄 FVM Management
- **`fvm install`** - Install Flutter Version Manager
- **`fvm uninstall`** - Remove Flutter Version Manager
- **`fvm releases [channel]`** - List available Flutter SDK versions
  - Channels: `stable`, `beta`, `dev`, or `all`
- **`fvm list`** - Show all installed Flutter SDK versions

#### ⚡ Slash Commands
- **`/quit`** - Exit FlutterCraft CLI
- **`/clear`** - Clear screen while preserving header
- **`/help`** - Show comprehensive command help
- **`/about`** - Display CLI information and version

#### 🎨 UI Features
- **Animated Loading Indicators** - Braille spinner during command execution
- **Smart Version Display** - Shows update availability: `3.32.6 (→ 3.35.6 available)` or `3.35.6 ✓`
- **Error Panels** - Persistent error display with red borders and exit codes
- **Command History** - Navigate with arrow keys, auto-suggest from history
- **Auto-completion** - Tab completion with live command suggestions

### 🚀 Upcoming Features

- **Cross-Platform Support**: The current CLI is only supported on windows.
- **Beautiful Themes**: The user will be able to select from different themes.
- **More Flutter Commands**: `flutter doctor`, `flutter --version`, and more
- **Project Creation**: `create` command to generate new Flutter projects with a wizard
- **Enhanced FVM Control**:
  - `fvm remove <version>`: Uninstall a specific Flutter SDK version
  - `fvm setup <version>`: Install and setup a Flutter version
  - `fvm use <version>`: Switch between installed Flutter versions
- **Backend Integration**: Connect to Firebase or Supabase projects
- **GitHub Automation**: Create and push to a new repository on GitHub
- **App Icon Generation**: Automatically generate app icons for all platforms

---

## 📥 Installation

### From PyPI (Recommended)

```bash
pip install fluttercraft
```

### From TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ fluttercraft
```

### Start FlutterCraft

After installation, run:

```bash
fluttercraft start
```

---

## ⚡ Development Setup

If you want to contribute or modify the code:

```bash
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft.git
cd fluttercraft
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows
# source venv/bin/activate   # On macOS/Linux
pip install -e .
fluttercraft start
```

---

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute and local setup.

---

## 📜 License

[AGPL v3](LICENSE)

---

## 🛡 Security

If you discover a security vulnerability, please check [SECURITY.md](SECURITY.md) for how to report it.

---

## 🌍 Join the Dev Tribe

Star this repo to support the project, and feel free to fork it, improve it, or just vibe with it. ❤️
