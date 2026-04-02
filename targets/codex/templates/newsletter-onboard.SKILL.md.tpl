---
name: newsletter-onboard
description: Run the interactive AI newsletter onboarding flow. Use when the user wants to set up or change newsletter platforms, Telegram settings, or schedule.
---

# Newsletter Onboard

Handle onboarding directly in the conversation. Do not call a separate onboarding script.

## Required behavior

1. Ask for `language` first and use that language for the entire onboarding conversation.
- save it as a short code such as `ko` or `en`
- if the user is unsure, default to `ko`
2. Ask concise questions to collect:
- platforms
- optional Reddit subreddits
- optional extra AI keywords
- Telegram enabled/disabled
- Telegram bot token and chat id if enabled
- Threads enabled/disabled
- RSSHub URL if Threads is enabled
  - default: `http://localhost:1200`
- Threads handles if Threads is enabled
  - user must enter exact handles without `@`
- schedule
  - interval examples: `30m`, `1h`, `2h`, `1d`
  - or a 5-field cron string
3. If Threads is enabled, verify RSSHub connectivity before saving:
- try `__RUNTIME_ROOT__/scripts` adjacent runtime config with:
```bash
python3 - <<'PY'
import sys, urllib.request
base = sys.argv[1].rstrip('/')
for url in (base + '/healthz', base):
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            if 200 <= resp.status < 400:
                print(url)
                raise SystemExit(0)
    except Exception:
        pass
raise SystemExit(1)
PY "RSSHUB_URL"
```
- if the check fails, explain that RSSHub must be running first and disable `threads`
4. Write `__RUNTIME_ROOT__/.data/config.json` directly.
5. After saving, read the file back:

```bash
mkdir -p __RUNTIME_ROOT__/.data
cat __RUNTIME_ROOT__/.data/config.json
```
6. Summarize in the configured language:
- selected platforms
- AI keywords if configured
- Telegram enabled or disabled
- Threads handles and RSSHub URL if configured
- chosen schedule

## Config shape

Write JSON in this shape, omitting unused optional keys:

```json
{
  "language": "ko",
  "platforms": ["hn", "reddit", "tldr"],
  "subreddits": ["OpenAI", "LocalLLaMA"],
  "ai_keywords": ["agent", "open source"],
  "rsshub_url": "http://localhost:1200",
  "threads_accounts": ["claudeai", "openai"],
  "telegram": {
    "enabled": true,
    "bot_token": "123:abc",
    "chat_id": "123456"
  },
  "schedule": {
    "mode": "interval",
    "expression": "1h",
    "label": "every hour"
  }
}
```
