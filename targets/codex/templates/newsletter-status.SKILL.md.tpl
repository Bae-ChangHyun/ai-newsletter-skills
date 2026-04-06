---
name: newsletter-status
description: Compatibility alias for newsletter-doctor.
---

# Newsletter Status

This compatibility alias delegates to `newsletter-doctor`.

## Commands

```bash
python3 __RUNTIME_ROOT__/scripts/newsletter_doctor.py --alias-mode status
```

## Required behavior

1. Run the diagnostics alias command.
2. Respond in `config.language` if present.
