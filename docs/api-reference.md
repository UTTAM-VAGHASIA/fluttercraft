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

### `create`

Create a new production-ready Flutter app with full setup.

```bash
fluttercraft create [OPTIONS]
```

**Options:**
- `--name, -n TEXT`: App name (required in non-interactive mode)
- `--org, -o TEXT`: Organization ID in reverse domain notation
- `--platforms, -p TEXT`: Target platforms (comma-separated)
- `--fvm/--no-fvm`: Use FVM for Flutter version management [default: fvm]
- `--backend, -b TEXT`: Backend choice (firebase/supabase/none)
- `--github/--no-github`: Create GitHub repository [default: github]
- `--dest, -d TEXT`: Destination directory
- `--interactive/--no-interactive`: Interactive mode [default: interactive]

**Examples:**
```bash
# Interactive mode (default)
fluttercraft create

# Non-interactive with specific options
fluttercraft create --name my_app --org com.example --platforms android,ios,web

# Create with Firebase backend
fluttercraft create --name my_app --backend firebase

# Create without GitHub repo
fluttercraft create --name my_app --no-github
```

### `flutter install`

Install Flutter SDK on your system.

```bash
fluttercraft flutter install [OPTIONS]
```

**Options:**
- `--version, -v TEXT`: Specific Flutter version to install
- `--force, -f`: Force reinstallation even if Flutter exists

**Examples:**
```bash
# Install latest stable Flutter
fluttercraft flutter install

# Install specific version
fluttercraft flutter install --version 3.16.0

# Force reinstall
fluttercraft flutter install --force
```

### `flutter doctor`

Run Flutter doctor to check your development environment.

```bash
fluttercraft flutter doctor
```

**Examples:**
```bash
# Check Flutter environment
fluttercraft flutter doctor
```

### `flutter versions`

Show available Flutter versions and current installation info.

```bash
fluttercraft flutter versions
```

### `flutter upgrade`

Upgrade Flutter to the latest stable version.

```bash
fluttercraft flutter upgrade
```

---

## ⚙️ Configuration

### Global Configuration File

Location: `~/.fluttercraft/config.yaml`

```yaml
# Default organization ID
org_id: "com.example"

# Default platforms
platforms:
  - android
  - ios

# Default Flutter version
flutter_version: "3.16.0"

# Use FVM by default
use_fvm: true

# Default backend
backend: "none"

# Default state management
state_management: "bloc"

# Create GitHub repo by default
create_github_repo: true

# GitHub repository visibility
github_visibility: "public"

# Default license
license: "MIT"

# Generate app icons by default
generate_icons: true

# Logging level
log_level: "INFO"
```

### Project Configuration File

Location: `.fluttercraft.yaml` (in project root)

```yaml
# Project-specific settings
project:
  name: "my_flutter_app"
  org_id: "com.example.myapp"
  flutter_version: "3.16.0"
  
platforms:
  - android
  - ios
  - web

backend:
  type: "firebase"
  project_id: "my-firebase-project"

features:
  state_management: "bloc"
  theme: "material3"
  internationalization: true
  
github:
  repository: "https://github.com/username/my_flutter_app"
  visibility: "public"
```

### Environment Variables

FlutterCraft respects the following environment variables:

- `FLUTTERCRAFT_LOG_LEVEL`: Override default log level (DEBUG, INFO, WARNING, ERROR)
- `FLUTTERCRAFT_CONFIG_DIR`: Override default config directory
- `FLUTTERCRAFT_CACHE_DIR`: Override default cache directory
- `FLUTTER_ROOT`: Flutter SDK installation directory
- `FVM_HOME`: FVM installation directory

---

## 🎨 Template Variables

### Flutter Project Templates

Available variables for Flutter project templates:

```yaml
# Basic project info
app_name: "my_flutter_app"
app_description: "A new Flutter application"
org_id: "com.example.myapp"
flutter_version: "3.16.0"

# Platform configuration
platforms:
  - android
  - ios
  - web

# Feature flags
use_fvm: true
backend: "firebase"
state_management: "bloc"
theme: "material3"

# GitHub integration
github_repo_url: "https://github.com/username/my_flutter_app"
license: "MIT"

# Metadata
created_date: "2024-01-15"
created_by: "FlutterCraft"
cli_version: "0.1.0"
```

### GitHub Workflow Templates

Available variables for CI/CD templates:

```yaml
# Flutter configuration
flutter_version: "3.16.0"
use_fvm: true

# Platform builds
platforms:
  - android
  - ios
  - web
  - windows
  - macos
  - linux

# Testing configuration
run_tests: true
coverage_enabled: true
code_analysis: true

# Deployment configuration
deploy_web: true
deploy_android: false
deploy_ios: false
```

---

## 🔧 Utility Functions

### Validation Functions

```python
from fluttercraft.utils.validation import (
    validate_app_name,
    validate_org_id,
    validate_flutter_version,
    validate_platforms,
    validate_backend_choice,
    sanitize_app_name
)

# Validate app name
is_valid, error = validate_app_name("my_app")

# Sanitize app name
clean_name = sanitize_app_name("My App!")  # Returns "my_app"
```

### Shell Utilities

```python
from fluttercraft.utils.shell import (
    run_command,
    check_command_exists,
    get_command_output
)

# Run a command
result = run_command("flutter --version")
print(f"Success: {result.success}")
print(f"Output: {result.stdout}")

# Check if command exists
if check_command_exists("flutter"):
    print("Flutter is available")

# Get command output
version = get_command_output("flutter --version")
```

### File I/O Utilities

```python
from fluttercraft.utils.io import (
    copy_template,
    render_template_string,
    ensure_directory
)

# Copy and render template
copy_template(
    "templates/flutter/README.md.j2",
    "output/README.md",
    {"app_name": "my_app"}
)

# Render template string
result = render_template_string(
    "Hello {{ name }}!",
    {"name": "World"}
)
```

---

## 🚨 Error Codes

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid command line arguments
- `3`: Environment validation failed
- `4`: Project creation failed
- `5`: Template rendering failed
- `6`: External command failed

### Error Messages

Common error messages and their meanings:

#### `flutter_not_found`
```
Flutter SDK not found. Please install Flutter first.
```
**Solution**: Install Flutter using `fluttercraft flutter install`

#### `invalid_app_name`
```
Invalid app name. Use lowercase letters, numbers, and underscores only.
```
**Solution**: Use a valid app name or let FlutterCraft sanitize it

#### `directory_exists`
```
Directory already exists. Choose a different name or location.
```
**Solution**: Use a different project name or destination directory

#### `git_not_found`
```
Git not found. Please install Git first.
```
**Solution**: Install Git from https://git-scm.com/

#### `gh_not_found`
```
GitHub CLI not found. Install from https://cli.github.com
```
**Solution**: Install GitHub CLI for repository creation features

---

## 📊 Performance Benchmarks

### Target Performance Metrics

- **Command Response Time**: < 2 seconds for all operations
- **Project Scaffolding**: < 30 seconds for complete setup
- **Memory Usage**: < 100MB during operation
- **Disk Space**: < 50MB for CLI installation

### Monitoring Commands

```bash
# Check CLI performance
time fluttercraft create --help

# Monitor memory usage
python -m memory_profiler -m fluttercraft create --help

# Profile CLI execution
python -m cProfile -m fluttercraft create --help
```

---

## 🔗 Integration APIs

### GitHub Integration

FlutterCraft integrates with GitHub through the GitHub CLI (`gh`):

```bash
# Required for GitHub features
gh auth login

# Repository creation
gh repo create my-app --public --clone

# Push initial commit
gh repo push
```

### Firebase Integration

Firebase integration requires the Firebase CLI:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize project
firebase init
```

### Supabase Integration

Supabase integration uses the Supabase CLI:

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Initialize project
supabase init
```

---

## 📚 SDK Reference

### Core Classes

#### `FlutterCraftCore`

Main orchestration class for FlutterCraft operations.

```python
from fluttercraft.core import FlutterCraftCore, ProjectConfig

core = FlutterCraftCore()

# Check prerequisites
checks = core.check_prerequisites()

# Create project
config = ProjectConfig(name="my_app", org_id="com.example")
success = core.create_flutter_project(config)
```

#### `ProjectConfig`

Configuration dataclass for project creation.

```python
from fluttercraft.core import ProjectConfig

config = ProjectConfig(
    name="my_app",
    org_id="com.example",
    platforms=["android", "ios"],
    flutter_version="3.16.0",
    use_fvm=True,
    backend="firebase",
    create_github_repo=True
)
```

---

This API reference provides comprehensive documentation for all FlutterCraft commands, configuration options, and integration points. For more detailed examples and tutorials, see the [Usage Guide](usage.md) and [Examples](examples/).
