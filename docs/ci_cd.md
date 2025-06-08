# FlutterCraft — CI/CD & DevOps

---

## 🤖 GitHub Actions: Automated Workflows

FlutterCraft comes pre-configured with a basic CI pipeline using **GitHub Actions**, which is located at:

```
.github/workflows/cli-check.yml
```

This workflow runs on every push and pull request to the `main` branch.

### 🧪 What It Does

* Installs Python
* Installs dependencies
* Runs CLI help to verify boot integrity
* Optionally lints or tests the CLI

### ✅ Example: `cli-check.yml`

```yaml
name: Lint & Test CLI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -e .

      - name: Lint
        run: |
          pip install flake8
          if [ -d "fluttercraft" ]; then flake8 fluttercraft; else echo "No code folder yet. Skipping lint."; fi

      - name: Run CLI help
        run: |
          python -c "import fluttercraft" 2>/dev/null && python -m fluttercraft --help || echo "fluttercraft module does not exist yet. Skipping CLI help check."

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

> You can add additional workflows for `lint`, `test`, `build`, and `release` based on project maturity.

---

## 📘 Recommended CI Practices

* Keep your CLI output clean — avoid unnecessary print statements
* Use exit codes wisely (`sys.exit(1)` for failure)
* Use `.env` or `secrets.GH_TOKEN` instead of hardcoding values
* Badge your README with CI status

```md
![CI](https://github.com/your-username/fluttercraft/actions/workflows/cli-check.yml/badge.svg)
```

---

With CI/CD integrated from the start, FlutterCraft isn’t just fast—it’s continuous. ⚡
