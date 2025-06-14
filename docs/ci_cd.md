# FlutterCraft — CI/CD & DevOps

---

## 🤖 GitHub Actions: Automated Workflows

FlutterCraft comes pre-configured with a basic CI pipeline using **GitHub Actions**, which is located at:

```
.github/workflows/cli-check.yml
```

This workflow runs on every push and pull request to the `main` branch.

### 🧪 What It Does

* Sets up Python 3.10
* Installs dependencies and the package in development mode
* Lints the code with flake8
* Verifies the CLI help command works
* Tests the version flag

### ✅ Current Workflow: `cli-check.yml`

```yaml
# .github/workflows/cli-check.yml
name: Lint & Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install typer[all] pyfiglet colorama rich
          pip install -e .

      - name: Lint
        run: |
          pip install flake8
          flake8 fluttercraft

      - name: Run CLI help
        run: |
          fluttercraft --help

      - name: Test version flag
        run: |
          fluttercraft --version || echo "Version flag not implemented yet."
```

---

## 🚀 Future CI/CD Enhancements

These will be added as optional CLI scaffolding later:

### 🔐 Secure Secrets Management

* Firebase/Supabase service credentials
* GitHub Tokens (for `gh` CLI)

### 📦 Build & Deploy Options

* Web app deploy to Firebase Hosting / GitHub Pages
* Build macOS/Windows/Linux installers (DMG, MSIX)
* iOS TestFlight / Android Internal Testing release hooks

### 🛠️ Pipeline Generators (Coming Soon)

```bash
fluttercraft ci generate github       # adds multiple GitHub Actions workflows
fluttercraft ci generate firebase     # adds firebase hosting & deploy config
fluttercraft ci generate flavors      # sets up env-specific builds
```

---

## 📁 Folder Reference

```
.github/
└── workflows/
    └── cli-check.yml     # CI for CLI validation
```

> As the project grows, additional workflows like `test` and `release` can be added.

---

## 📘 Recommended CI Practices

* Keep CLI output clean — avoid unnecessary print statements
* Use exit codes properly (`sys.exit(1)` for failure)
* Use environment variables for sensitive information
* Badge your README with CI status

```md
![Build](https://github.com/UTTAM-VAGHASIA/fluttercraft/actions/workflows/cli-check.yml/badge.svg)
```

---

This CI/CD configuration will be expanded as more features are implemented.
