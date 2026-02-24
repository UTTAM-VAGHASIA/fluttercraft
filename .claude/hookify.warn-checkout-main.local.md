---
name: warn-checkout-main
enabled: true
event: bash
pattern: git\s+(checkout|switch)\s+main\b
action: warn
---

⚠️ **Switching to main branch**

You are about to switch to `main`. All v0.2.0 work must stay on `feature/v0.2.0-tui`.

**Check before proceeding:**
- Are you sure this is intentional and user-requested?
- Is the user on the correct branch (`feature/v0.2.0-tui`)?

**From AGENTS.md:**
> Do NOT modify `main` branch directly — work on `feature/v0.2.0-tui`
> Agent NEVER runs git commands — only provides them for the user to run
