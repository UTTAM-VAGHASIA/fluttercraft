---
name: block-git-push
enabled: true
event: bash
pattern: git\s+push
action: block
---

🚫 **git push is blocked**

`git push` is not allowed unless the user explicitly asks for it.

**What to do instead:**
- Provide the push command in a `## Git Command Required` block for the user to run manually
- Wait for the user to confirm they want to push before providing the command

**From AGENTS.md:**
> Do NOT push to remote unless explicitly asked
> Agent NEVER runs git commands — only provides them for the user to run
