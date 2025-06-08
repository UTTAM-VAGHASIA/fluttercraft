# FlutterCraft — Internal Architecture Guide

---

## 🧠 Overview

FlutterCraft is a modular, Python-based CLI tool built using [Typer](https://typer.tiangolo.com/), designed to automate full-stack Flutter app scaffolding. It cleanly separates core logic, CLI commands, utilities, templates, and documentation, allowing for intuitive scaling and open-source collaboration.

---

## 🗂️ Project Structure Breakdown

```
fluttercraft/
├── fluttercraft/            # Python package for the CLI tool
│   ├── __main__.py          # Entry point: `python -m fluttercraft`
│   ├── core.py              # Central coordination logic
│   ├── commands/            # Individual CLI commands
│   ├── utils/               # Shell + path helpers, validation
│   ├── config/              # Central constants and config
│
├── templates/              # Jinja2 templates for scaffolding
├── docs/                   # Markdown documentation
├── tests/                  # Pytest-based unit/integration tests
├── .github/                # GitHub Actions & OSS configs
├── pyproject.toml          # Dependency and entrypoint config
```

---

## 🔌 Module Responsibilities

### `__main__.py`

* Entry CLI hook using Typer
* Registers all commands from `commands/`

### `core.py`

* Core orchestration for multi-step flows (like `create`)
* Responsible for shared execution logic

### `commands/`

* Each file is a self-contained CLI feature:

  * `create.py`: Full interactive setup (MVP anchor)
  * `flutter.py`: Flutter installation logic
  * `fvm.py`: FVM detection and management
  * `backend.py`: Firebase/Supabase setup
  * `logo.py`: Icon generation
  * `publish.py`: Deployment config
  * `github.py`: GitHub repo creation and push

### `utils/`

* `io.py`: File handling, project path helpers
* `shell.py`: Cross-platform subprocess runners
* `validation.py`: Input verification (e.g., app name format)
* `osinfo.py`: Detect OS for platform-specific logic

### `config/`

* `defaults.py`: CLI defaults, versioning info
* `paths.py`: Base path constants and derived paths

---

## 🧩 Template Engine (Jinja2)

Jinja templates live under `templates/`. These are used to generate:

* Flutter project structures
* README and doc files
* CI/CD workflows
* Flavor environment configs

They allow dynamic rendering based on user input from CLI prompts.

---

## 📦 Dependency Management

FlutterCraft uses either `pip` with `pyproject.toml` or `poetry` for managing:

* Python dependencies (`typer`, `questionary`, `jinja2`, etc.)
* Entry point for CLI (`[tool.poetry.scripts]` or `[project.scripts]`)

---

## 🔄 Execution Flow Diagram (for `fluttercraft create`)

```text
User invokes `fluttercraft create`
    ↓
Prompt: App name, platforms, use FVM?
    ↓
  └─▶ If FVM: Check & install → set version
    ↓
Prompt: Destination folder
    ↓
Prompt: Create GitHub repo?
    ↓
  └─▶ If yes: Init, configure, push
    ↓
Run `flutter create`
    ↓
Prompt: Icons? Backend? State mgmt?
    ↓
Run setup tools + generate docs
```

---

## 🔐 Security Considerations

* No credentials stored
* GitHub repo creation uses `gh` CLI (token handled by user)
* Firebase/Supabase setup is local-only

---

## 🧪 Testing Strategy

* Use `pytest`
* Command-line behavior tested via subprocess mocks
* Utilities tested as standalone functions

---

## 📈 Designed for Growth

* Add new CLI commands by dropping files into `commands/`
* Templates modular and customizable
* Config-driven for future plugin ecosystem

FlutterCraft’s architecture is built to scale with the ambition of your ideas—and the reality of your deadlines.
