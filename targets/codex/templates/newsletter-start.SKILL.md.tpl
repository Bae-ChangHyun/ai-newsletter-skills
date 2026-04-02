---
name: newsletter-start
description: Register the AI newsletter cron job. Use when the user wants scheduled newsletter delivery to start.
---

# Newsletter Start

## Commands

```bash
cat __RUNTIME_ROOT__/.data/config.json
python3 __RUNTIME_ROOT__/scripts/manage_cron.py start
python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

## Required behavior

1. Confirm the config file exists.
2. Run the start command.
3. Run the status command.
4. Explain that the recurring cron itself is anchored from 2 minutes after the current time.
5. Report the installed recurring schedule.
