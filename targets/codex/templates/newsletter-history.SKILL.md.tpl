---
name: newsletter-history
description: Show recent delivered newsletter history, including latest summaries and delivered items.
---

# Newsletter History

## Commands

```bash
python3 __RUNTIME_ROOT__/scripts/newsletter_history.py
```

## Required behavior

1. Show the recent delivery history.
2. Prefer `config.language` if present.
3. Summarize latest delivery history without changing runtime state.
