---
name: block-git-commands
enabled: true
event: bash
action: block
pattern: ^\s*git\s+
---

🚫 **Git command blocked**

Per `plan.md` policy: **Agent NEVER runs git commands.**

Only provide the git command for the user to copy-paste. Do not execute it yourself.

**What to do instead:**
- Write out the exact git command(s) in a code block
- State the current and target branch clearly
- Wait for the user to run the command and confirm the result
