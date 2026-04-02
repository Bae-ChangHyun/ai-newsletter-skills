---
name: newsletter-onboard
description: Run the interactive AI newsletter onboarding flow. Use when the user wants to set up or change newsletter platforms, Telegram settings, or schedule.
---

# Newsletter Onboard

Run the onboarding flow directly. Do not substitute unrelated exploration.

## Command

```bash
python3 __RUNTIME_ROOT__/scripts/onboard.py
```

## Required behavior

1. Explain briefly that the script will ask interactive terminal questions.
2. Run the script directly.
3. After it exits, read the saved config:

```bash
cat __RUNTIME_ROOT__/.data/config.json
```

4. Summarize:
- selected platforms
- Telegram enabled or disabled
- chosen schedule

