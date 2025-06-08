# FlutterCraft — Contributing Guide

---

Thank you for your interest in contributing to **FlutterCraft**! 🛠️
Whether you're fixing a bug, adding a feature, or improving documentation—you're helping developers ship faster.

---

## 💡 Ways to Contribute

* 🐛 Report bugs or suggest features via GitHub Issues
* 🧰 Improve CLI UX, automation, or commands
* 📄 Write or enhance documentation
* 🔧 Add test coverage for commands and utilities
* 📦 Publish templates or config snippets

---

## 🧭 Getting Started

### 1. **Fork the Repo**

```bash
git clone https://github.com/your-username/fluttercraft.git
cd fluttercraft
git remote add upstream https://github.com/UTTAM-VAGHASIA/fluttercraft.git
```

### 2. **Setup Your Environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. **Run the CLI**

```bash
python -m fluttercraft --help
```

---

## 🔀 Branching & Commits

* Use feature branches: `feature/<name>` or `fix/<name>`
* Use semantic commits:

  * `feat:` for new features
  * `fix:` for bug fixes
  * `docs:` for documentation
  * `refactor:` for internal improvements

```bash
git checkout -b feature/create-wizard
```

---

## ✅ Pull Request Checklist

Before you submit a PR:

* [ ] Does the CLI still work? (`python -m fluttercraft --help`)
* [ ] Are new modules added to the right folder?
* [ ] Did you add/modify related tests?
* [ ] Did you lint your code? (basic `flake8` or `black` style)
* [ ] Is the PR description clear and descriptive?

---

## 🧪 Running Tests

```bash
pytest tests/
```

Add your tests in `tests/` with descriptive function names.

---

## 🛡️ Code of Conduct

Please follow our [Code of Conduct](https://github.com/UTTAM-VAGHASIA/fluttercraft/blob/main/CODE_OF_CONDUCT.md) in all interactions. Be kind, respectful, and helpful.

---

## ❤️ Thanks for Building with Us!

Every contribution is valuable—big or small. Together we're creating a tool that empowers developers across the globe.

Let's craft magic, one command at a time. ✨
