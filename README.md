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

- 📦 Flutter + FVM setup
- 🧭 Guided Flutter create wizard
- 🎨 Icon automation
- 🔥 Firebase / Supabase integration
- 🛠️ Platform publishing (Android, iOS, Web, Desktop)
- 📁 GitHub repo creation (public/private)
- 📚 Auto-generated project documentation

---

## 🤖 CLI Status

The interactive CLI is under active development. Here's a look at what's working and what's coming next.

### ✅ Current Features

- **Interactive Shell**: Start the CLI with `fluttercraft start`.
- **Environment Check**: Automatically detects existing Flutter and FVM installations.
- **FVM Management**:
  - `fvm install`: Install the Flutter Version Manager.
  - `fvm uninstall`: Remove the Flutter Version Manager.
- **Basic Commands**: `help`, `clear`, and `exit` are available.

### 🚀 Upcoming Features

- **Project Creation**: `create` command to generate new Flutter projects with a wizard.
- **Enhanced FVM Control**:
  - `fvm releases`: List all the released flutter versions.
  - `fvm list`: List all installed Flutter SDK versions.
  - `fvm remove <version>`: Uninstall a specific Flutter SDK version.
  - `fvm setup <version>`: To install and setup a flutter version.
- **Backend Integration**: Connect to Firebase or Supabase projects.
- **GitHub Automation**: Create and push to a new repository on GitHub.
- **App Icon Generation**: Automatically generate app icons for all platforms.

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
