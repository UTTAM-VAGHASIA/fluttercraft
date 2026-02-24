# 📋 FlutterCraft — Remaining Tasks
> Last updated: February 24, 2026
> Stack: Python + Typer + Rich CLI
> Status: Phase 1 ✅ + Phase 2 ✅ | Phase 3–5 ❌

---

## 🔴 Phase 3 — Enhanced FVM Management (Current)
> **This is where development left off.**

- [ ] `fvm remove <version>` — remove an installed FVM Flutter version
- [ ] `fvm use <version>` / `fvm setup` — set the active Flutter version for a project
- [ ] Flutter detection — check if Flutter is installed independently of FVM
- [ ] Flutter installation via FVM — `fvm install <version>` with progress display
- [ ] Flutter version switching — switch between globally installed Flutter versions

---

## 🔴 Phase 4 — Project Creation Wizard
*Effort: ~15–20 hours*

- [ ] `fluttercraft create` command — launch interactive project wizard
- [ ] Prompt for: project name, package name, org name, platform targets
- [ ] Template selection (blank, clean architecture, feature-first, BLoC starter)
- [ ] Scaffold the selected Flutter project with folder structure
- [ ] Auto-configure `pubspec.yaml` with common packages based on template

---

## 🔴 Phase 5 — Integration Features
*Effort: ~15–20 hours*

- [ ] Firebase integration — run `flutterfire configure` and set up `firebase_options.dart`
- [ ] Supabase integration — add Supabase client and env setup
- [ ] GitHub repo creation — create and push a new repo via GitHub API
- [ ] App icon generation — take a source image and generate all icon sizes (via `flutter_launcher_icons`)
- [ ] Splash screen generation (via `flutter_native_splash`)

---

## 🟡 Technical Debt / Quality

- [ ] Write test suite (unit tests for commands + utils)
- [ ] Add configuration file system (`.fluttercraft.yaml` per project or global)
- [ ] Improve error messages and user guidance for failed commands
- [ ] Publish to PyPI (`pip install fluttercraft`)

---

## ✅ Already Done (reference)
- CLI entry point + interactive shell (`start` command)
- Welcome ASCII art display
- Comprehensive help system
- `clear` command
- FVM detection + installation + uninstallation
- FVM releases listing with channel filtering (`stable`, `beta`, `dev`)
- FVM installed versions listing
- Cross-platform compatibility
- Full documentation (`docs/`)

---

## 📌 Notes
- Run locally: `python -m fluttercraft` or `fluttercraft` (after `pip install -e .`)
- FVM commands wrap the `fvm` binary on the system PATH
- Phase 3 is blocked only by implementation time — no design decisions needed
