---
name: newsletter-status
description: Show the currently registered AI newsletter cron state for Codex.
---

# Newsletter Status

## Commands

```bash
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

## Required behavior

1. Read the saved config first.
2. Run the cron status command.
3. Summarize the current settings from config:
- selected platforms
- Telegram enabled or disabled
- configured schedule label plus interval or cron value
- AI keywords if configured
- Threads accounts and RSSHub URL if configured
4. Also report whether a recurring cron entry is currently registered.
