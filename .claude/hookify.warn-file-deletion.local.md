---
name: warn-file-deletion
enabled: true
event: bash
pattern: \brm\s+
action: warn
---

⚠️ **File deletion command detected**

A `rm` command is about to run. File deletion requires explicit user confirmation.

**Before proceeding, verify:**
- Has the user explicitly asked to delete this file?
- Is this file part of the project source (not a temp file)?
- Could this delete work that hasn't been committed yet?

**From AGENTS.md:**
> Verify Destructive Ops — Confirm before delete, overwrite, or reset
> Never delete files without confirmation
