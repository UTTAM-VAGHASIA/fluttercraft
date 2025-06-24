# FlutterCraft — API Reference

---

## 🎯 Command Line Interface

### Main Command

```bash
fluttercraft [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--version, -v`: Show version and exit
- `--help`: Show help message and exit

---

## 📋 Commands

### `start`

**Description:** Starts the FlutterCraft interactive CLI with welcome ASCII art.

**Usage:**
```bash
fluttercraft start
```

**Interactive Commands:**

#### Basic Commands
- `help` or `h` - Show available commands
- `clear` - Clear the terminal screen
- `exit`, `quit` or `q` - Exit the CLI

#### FVM Commands
- `fvm install` - Install Flutter Version Manager on your system
- `fvm uninstall` - Uninstall Flutter Version Manager from your system
- `fvm releases` - List all available Flutter SDK versions for installation
  - `fvm releases [channel]` - List versions filtered by channel (stable, beta, dev, all)
  - `fvm releases --channel [channel]` - List versions with explicit channel flag
  - `fvm releases -c [channel]` - List versions with short channel flag
- `fvm list` - List all installed Flutter SDK versions managed by FVM

#### Help System
- `help` - Show global help
- `fvm help` - Show FVM-specific help
- `command help` - Show help for a specific command (e.g., `fvm install help`)
- `command --help` - Alternative syntax for command help

**Examples:**
```bash
# Start the interactive CLI
fluttercraft start

# Inside the CLI, install FVM
fvm install

# List available Flutter versions
fvm releases

# List available Flutter versions from beta channel
fvm releases beta

# List installed Flutter versions
fvm list

# Get help on a specific command
fvm releases help
```

---

## 🔧 Command Details

### FVM Commands

#### `fvm install`

Installs Flutter Version Manager (FVM) on your system.

- **On Windows**: Uses Chocolatey package manager (will offer to install if not present)
- **On macOS/Linux**: Uses curl to download and run the installation script
- **Requirements**: Admin privileges may be required on Windows

#### `fvm uninstall`

Uninstalls Flutter Version Manager (FVM) from your system.

- **Interactive**: Will ask if you want to remove all cached Flutter versions
- **On Windows**: Uses Chocolatey package manager
- **On macOS/Linux**: Uses the FVM installer script with --uninstall flag

#### `fvm releases`

Lists all available Flutter SDK versions that can be installed through FVM.

- **Parameters**:
  - `channel`: Filter versions by release channel (stable, beta, dev, all)
- **Output**: Displays version numbers, release dates, and channels in a formatted table
- **Default**: Shows stable channel versions if no channel specified

#### `fvm list`

Lists all installed Flutter SDK versions managed by FVM on your system.

- **Output**: Displays cache directory location, size, and details for each installed SDK
- **Indicators**: Shows which version is set as global and/or local for the current project
- **Sorting**: Versions are sorted by release date (newest first)

---

## 🚨 Error Codes

### Exit Codes

- `0`: Success
- `1`: General error

---

This API reference provides documentation for FlutterCraft commands currently implemented. As more features are added, this document will be updated. For more detailed information and usage examples, see the [Usage Guide](usage.md).
