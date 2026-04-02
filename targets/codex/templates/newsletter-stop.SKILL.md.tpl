---
name: newsletter-stop
description: Remove the Codex-managed AI newsletter cron job. Use when the user wants scheduled newsletter delivery to stop.
---

# Newsletter Stop

## Commands

```bash
python3 __RUNTIME_ROOT__/scripts/manage_cron.py stop
python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

## Required behavior

1. Run the stop command.
2. Run the status command.
3. Report whether the Codex-managed cron entry was removed or was already absent.

