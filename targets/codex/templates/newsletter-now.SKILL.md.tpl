---
name: newsletter-now
description: Run the AI newsletter immediately through the Codex editorial pass. Use when the user wants the newsletter generated now.
---

# Newsletter Now

Run the non-interactive runner directly.

## Command

```bash
__RUNTIME_ROOT__/scripts/run_with_codex.sh
```

The runner uses `codex exec --dangerously-bypass-approvals-and-sandbox`.

## Required behavior

1. Run the runner directly.
2. Return the one-line summary from the run.

