# FlutterCraft CLI — Usage Guide

---

## 🚀 Getting Started

### 📦 Installation Options

#### From PyPI (Recommended)

```bash
pip install fluttercraft
```

#### From TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ fluttercraft
```

#### For Development

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

**Basic Interactive Commands:**
* `help` or `h` - Display available commands
* `clear` - Clear the terminal screen
* `exit`, `quit` or `q` - Exit the CLI

### FVM Management Commands

FlutterCraft provides a set of commands to manage Flutter versions through FVM (Flutter Version Manager).

#### `fvm install`

Installs Flutter Version Manager on your system.

```bash
fvm install
```

* On Windows, uses Chocolatey (will offer to install if not present)
* On macOS/Linux, uses curl to download and run the installation script
* Requires admin privileges on Windows

#### `fvm uninstall`

Uninstalls Flutter Version Manager from your system.

```bash
fvm uninstall
```

* Will ask if you want to remove all cached Flutter versions
* On Windows, uses Chocolatey
* On macOS/Linux, uses the FVM installer script with --uninstall flag

#### `fvm releases`

Lists all available Flutter SDK versions that can be installed through FVM.

```bash
# List all stable versions (default)
fvm releases

# List versions from a specific channel
fvm releases beta

# List versions with explicit channel flag
fvm releases --channel dev

# List versions with short channel flag
fvm releases -c all
```

Available channels: `stable` (default), `beta`, `dev`, `all`

#### `fvm list`

Lists all installed Flutter SDK versions managed by FVM on your system.

```bash
fvm list
```

* Shows cache directory location and size
* Displays details for each installed SDK
* Highlights which version is set as global/local
* Sorts versions by release date (newest first)

### Help System

FlutterCraft includes a comprehensive help system:

```bash
# Global help
help

# FVM-specific help
fvm help

# Command-specific help
fvm install help
fvm releases help
fvm list help
clear help

# Alternative syntax
fvm install --help
```

---

## 🧪 Planned Commands (Coming Soon)

### `fvm remove <version>`

Will uninstall a specific Flutter SDK version.

### `fvm setup <version>`

Will install and configure a specific Flutter version.

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

### `fluttercraft flutter install`

Will check if Flutter is installed, installs it if not.

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
| FVM not found                | Run `fvm install` to install Flutter Version Manager                     |
| Empty FVM output             | Restart terminal after FVM installation                                  |

---

## 📘 Notes

* The current version features a functional interactive CLI with FVM management capabilities
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

Or inside the interactive CLI:

```
help
```

to see all available commands.
