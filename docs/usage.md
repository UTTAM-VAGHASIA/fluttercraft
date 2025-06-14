# FlutterCraft CLI — Usage Guide

---

## 🚀 Getting Started

### 📦 Install Dependencies

First, ensure you have Python 3.10+ installed. Then clone the repo and install dependencies:

```bash
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft.git
cd fluttercraft
python -m venv venv
# On Linux/macOS:
source venv/bin/activate  
# On Windows:
.\venv\Scripts\Activate.ps1
pip install -e .
```

> This will install the package in development mode, allowing you to make changes to the code without reinstalling.

---

## 🧪 Verify the CLI

```bash
fluttercraft --help
```

This should display all available commands.

---

## 🛠 Current Commands 

### `fluttercraft start`

Starts the interactive FlutterCraft CLI with welcome ASCII art.

```bash
fluttercraft start
```

**Interactive Commands:**
* `help` or `h` - Display available commands
* `create` - Create a new Flutter project (placeholder for future implementation)
* `flutter install` - Install Flutter (placeholder for future implementation)
* `fvm setup` - Setup Flutter Version Manager (placeholder for future implementation)
* `exit`, `quit` or `q` - Exit the CLI

---

## 🧪 Planned Commands (Coming Soon)

### `fluttercraft create`

Interactive command to scaffold a full-featured Flutter app.

```bash
fluttercraft create
```

**Future Prompts:**
* App name & org ID
* Platform targets (Android, iOS, Web, etc.)
* Use FVM or not
* Flutter version (if FVM)
* Project destination path
* GitHub repo creation & settings
* Setup: app icons, backend, state management, flavors

---

### `fluttercraft flutter install`

Will check if Flutter is installed, installs it if not.

### `fluttercraft fvm setup`

Will install FVM (if not available) and configure desired Flutter version.

### `fluttercraft backend connect`

Will guide integration of Firebase or Supabase.

### `fluttercraft logo set`

Will handle app icon generation using an image.

### `fluttercraft publish prep`

Will guide user through platform-specific release setup (Android/iOS/Web/Desktop).

### `fluttercraft github push`

Will create GitHub repo, add LICENSE, README, push first commit.

---

## ⚠️ Troubleshooting

| Issue                        | Fix                                                                      |
| ---------------------------- | ------------------------------------------------------------------------ |
| `ModuleNotFoundError`        | Activate your virtual environment or run `pip install -e .`              |
| `UnicodeDecodeError`         | Check encoding of README.md or use explicit encoding in setup.py         |
| Missing dependencies         | Run `pip install typer pyfiglet colorama rich` if not automatically installed |

---

## 📘 Notes

* The current version features a functional interactive CLI framework
* Future versions will implement actual Flutter app creation and customization
* Works across Linux, macOS, and Windows
* Open-source, AGPL v3 licensed — contributions welcome!

---

## 🧠 Tip

You can always type:

```bash
fluttercraft --help
```

to view usage and options for any command.
