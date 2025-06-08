# FlutterCraft CLI — Usage Guide

---

## 🚀 Getting Started

### 📦 Install Dependencies

First, ensure you have Python 3.10+ installed. Then clone the repo and install dependencies:

```bash
git clone https://github.com/your-username/fluttercraft.git
cd fluttercraft
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

> Alternatively, use `poetry install` if you're using Poetry.

---

## 🧪 Verify the CLI

```bash
python -m fluttercraft --help
```

This should display all available commands.

---

## 🛠 Commands Overview

### `fluttercraft create`

Interactive command to scaffold a full-featured Flutter app.

```bash
fluttercraft create
```

**Prompts:**

* App name & org ID
* Platform targets (Android, iOS, Web, etc.)
* Use FVM or not
* Flutter version (if FVM)
* Project destination path
* GitHub repo creation & settings
* Setup: app icons, backend, state management, flavors

---

### `fluttercraft flutter install`

Checks if Flutter is installed, installs it if not.

```bash
fluttercraft flutter install
```

### `fluttercraft fvm setup`

Installs FVM (if not available) and configures desired Flutter version.

```bash
fluttercraft fvm setup
```

### `fluttercraft backend connect`

Guided integration of Firebase or Supabase.

```bash
fluttercraft backend connect
```

### `fluttercraft logo set`

Handles app icon generation using an image.

```bash
fluttercraft logo set
```

### `fluttercraft publish prep`

Guides user through platform-specific release setup (Android/iOS/Web/Desktop).

```bash
fluttercraft publish prep
```

### `fluttercraft github push`

Creates GitHub repo, adds LICENSE, README, pushes first commit.

```bash
fluttercraft github push
```

---

## ⚠️ Troubleshooting

| Issue                        | Fix                                                                      |
| ---------------------------- | ------------------------------------------------------------------------ |
| `ModuleNotFoundError`        | Activate your virtual environment or run `pip install -e .`              |
| `gh: command not found`      | Install GitHub CLI from [https://cli.github.com](https://cli.github.com) |
| Chocolatey issues on Windows | Run terminal as Administrator                                            |

---

## 📘 Notes

* Commands are modular — you can use `create` or individual commands
* Works across Linux, macOS, and Windows (with fallback instructions)
* Open-source, MIT licensed — contributions welcome!

---

## 🧠 Tip

You can always type:

```bash
fluttercraft <command> --help
```

to view usage and options for any command.
