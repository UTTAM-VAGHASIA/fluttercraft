# FlutterCraft CLI Redesign Documentation

## Overview

The FlutterCraft CLI has been completely redesigned with a beautiful, modern interface inspired by Claude Code and Gemini CLI. The new interface features slash commands, multiline input support, auto-completion, and dynamic header updates.

## Key Features

### 1. Beautiful Interface
- **ASCII Art Header**: Eye-catching FlutterCraft branding with bordered panel
- **Color-Coded Output**: Rich formatting with colors for better readability
- **Bottom Toolbar**: Helpful hints displayed at the bottom of the terminal
- **Auto-Completion**: Smart command suggestions as you type

### 2. Slash Commands
All system commands now use the `/` prefix for clarity:

- `/quit`, `/exit`, `/q` - Exit the CLI
- `/clear` - Clear screen while preserving header
- `/help` - Display help information

### 3. Dynamic Header Updates
The header automatically updates when:
- **Flutter version changes**: Running `flutter upgrade` updates the version in the header
- **FVM installation changes**: Installing/uninstalling FVM updates the header
- **Version information**: Shows current vs. latest version with helpful messages

### 4. Command History
- **Preserved History**: Command history is maintained even after header refreshes
- **Smart Clearing**: `/clear` command preserves header but clears history
- **History Navigation**: Use arrow keys to navigate through previous commands
- **Auto-Suggest**: Previous commands are suggested as you type

### 5. Enhanced Error Handling
- **Graceful Ctrl+C**: Doesn't exit, just cancels current input
- **Ctrl+D Support**: Quick exit using Ctrl+D
- **Clear Error Messages**: Helpful error messages with suggestions

## Command Reference

### Slash Commands

#### `/quit`, `/exit`, `/q`
Exit the FlutterCraft CLI gracefully.

```
fluttercraft> /quit
Thank you for using FlutterCraft! Goodbye! 👋
```

#### `/clear`
Clear the screen and command history while preserving the header with current version information.

```
fluttercraft> /clear
```

**Behavior**:
- Clears all previous command output
- Preserves the header with current Flutter/FVM versions
- Resets command history

#### `/help`
Display comprehensive help information about available commands.

```
fluttercraft> /help
```

### FVM Commands

#### `fvm`
Display FVM help information.

```
fluttercraft> fvm
```

#### `fvm install`
Install Flutter Version Manager on your system.

```
fluttercraft> fvm install
```

**Windows**: Uses Chocolatey (will offer to install if not present)
**macOS/Linux**: Uses curl to download installation script

#### `fvm uninstall`
Uninstall Flutter Version Manager from your system.

```
fluttercraft> fvm uninstall
```

#### `fvm releases [channel]`
List available Flutter SDK versions.

```
fluttercraft> fvm releases
fluttercraft> fvm releases stable
fluttercraft> fvm releases beta
fluttercraft> fvm releases --channel=dev
```

**Channels**: `stable`, `beta`, `dev`, `all`

#### `fvm list`
List all installed Flutter SDK versions managed by FVM.

```
fluttercraft> fvm list
```

### Flutter Commands

#### `flutter upgrade`
Upgrade Flutter to the latest version. **The header will automatically update** with the new version.

```
fluttercraft> flutter upgrade
Executing Flutter upgrade...
✓ Flutter upgraded successfully!
Updating header with new Flutter version...
```

**Before upgrade**:
```
Flutter version: 3.32.6 (Latest version available: 3.35.6)
```

**After upgrade**:
```
Flutter version: 3.35.6 (Your Flutter version is already up to date)
```

#### `flutter --version`
Display current Flutter version information.

```
fluttercraft> flutter --version
```

### Help Commands

#### `<command> --help`
Get help for any specific command.

```
fluttercraft> fvm install --help
fluttercraft> fvm releases --help
```

## Header Behavior

### Initial Display
When you start FlutterCraft, the header shows:
```
╭─────────────────────────── Welcome to FlutterCraft 🛠️🚀 ───────────────────────────╮
│ [ASCII ART]                                                                        │
│                                                                                    │
│ Automate your Flutter app setup like a pro.                                       │
│ From folder structure to backend integration, from icons to GitHub repo setup —   │
│ FlutterCraft does it all.                                                         │
╰───────────────────────────────────────────── v0.1.2 ─────────────────────────╯
FlutterCraft CLI started!
Platform: Windows
Shell: C:\WINDOWS\system32\cmd.exe
Python version: 3.13.7
Flutter version: 3.32.6 (Latest version available: 3.35.6)
FVM version: 3.2.1
Enter commands or type '/quit' to exit
```

### After Flutter Upgrade
The header automatically refreshes to show:
```
Flutter version: 3.35.6 (Your Flutter version is already up to date)
```

### After /clear Command
- Header is redisplayed with current version information
- All command history is cleared
- System information remains accurate

## Auto-Completion

The CLI provides intelligent auto-completion for:
- Slash commands (`/quit`, `/clear`, `/help`)
- FVM commands (`fvm install`, `fvm releases stable`)
- Flutter commands (`flutter upgrade`, `flutter --version`)

**Usage**:
- Start typing and press `Tab` to see suggestions
- Use arrow keys to select from suggestions
- Press `Enter` to accept a suggestion

## Keyboard Shortcuts

- **↑/↓ Arrow Keys**: Navigate command history
- **Tab**: Trigger auto-completion
- **Ctrl+C**: Cancel current input (doesn't exit)
- **Ctrl+D**: Exit FlutterCraft
- **Ctrl+L**: Clear screen (alternative to `/clear`)

## Error Handling

### Unknown Commands
```
fluttercraft> unknown-command
Unknown command: unknown-command
Type '/help' or 'help' to see available commands
```

### Failed Operations
```
fluttercraft> flutter upgrade
Executing Flutter upgrade...
✗ Flutter upgrade failed!
```

### Graceful Interruption
```
fluttercraft> [Ctrl+C]
Use '/quit' or '/exit' to exit FlutterCraft
```

## Technical Implementation

### Architecture
- **prompt_toolkit**: Powers the beautiful prompt with auto-completion
- **rich**: Provides rich text formatting and panels
- **pyfiglet**: Generates ASCII art
- **Command Handler**: Centralized command processing
- **Beautiful Display**: Manages header and history display

### Files Changed
1. `setup.py` - Added `prompt_toolkit` and `pygments` dependencies
2. `commands/start.py` - Completely rewritten with new interface
3. `utils/beautiful_display.py` - New display utilities
4. `utils/beautiful_prompt.py` - New prompt system
5. `commands/command_handler.py` - New command processing system

### Backward Compatibility
- Old command syntax still works (e.g., `help`, `quit`)
- Slash commands are preferred but optional
- All existing FVM and Flutter commands remain functional

## Migration Guide

### For Users
No migration needed! The new interface is backward compatible. You can:
- Continue using old commands (`quit`, `help`, `clear`)
- Start using new slash commands (`/quit`, `/help`, `/clear`)
- Mix both styles as you prefer

### For Developers
If you're extending FlutterCraft:
1. Add new commands to `command_handler.py`
2. Update auto-completion list in `beautiful_prompt.py`
3. Add help text to `beautiful_display.py`

## Future Enhancements

Planned improvements:
- [ ] Multiline input for complex commands
- [ ] Command aliases
- [ ] Custom themes
- [ ] Plugin system for custom commands
- [ ] Configuration file support
- [ ] Session persistence

## Troubleshooting

### Auto-completion not working
Ensure `prompt_toolkit>=3.0.0` is installed:
```bash
pip install prompt_toolkit>=3.0.0
```

### Colors not displaying
Ensure `rich` is installed and your terminal supports colors:
```bash
pip install rich
```

### Header not updating after Flutter upgrade
This is a known issue if Flutter upgrade fails silently. Try:
```
fluttercraft> flutter --version
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/UTTAM-VAGHASIA/fluttercraft/issues
- Documentation: https://github.com/UTTAM-VAGHASIA/fluttercraft/docs
