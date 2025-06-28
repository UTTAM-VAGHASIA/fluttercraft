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

**Examples:**
```bash
# Start the interactive CLI
fluttercraft start

# Inside the CLI, install FVM
fvm install
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

---

## 🚨 Error Codes

### Exit Codes

- `0`: Success
- `1`: General error

---

This API reference provides documentation for FlutterCraft commands currently implemented. As more features are added, this document will be updated. For more detailed information and usage examples, see the [Usage Guide](usage.md).