You are generating a newsletter runtime config JSON from onboarding answers.

Requirements:
- Return JSON only.
- Preserve the user's intent, but normalize the shape.
- The config must use this structure:
  {
    "language": "ko",
    "backend": {
      "type": "claude|codex|github_copilot|openai",
      "settings": {}
    },
    "platforms": ["hn", "reddit"],
    "subreddits": ["OpenAI"],
    "ai_keywords": ["agent"],
    "rsshub_url": "http://localhost:1200",
    "threads_accounts": ["claudeai"],
    "telegram": {
      "enabled": true,
      "bot_token": "123:abc",
      "chat_id": "123456"
    },
    "schedule": {
      "mode": "interval",
      "expression": "1h",
      "label": "1h"
    }
  }
- Omit optional keys when they are empty.
- Keep `backend.settings` exactly aligned with the selected backend:
  - `claude`: empty object
  - `codex`: empty object
  - `github_copilot`: include `model` and `auth_flow`
  - `openai`: include `base_url`, `model`, and `api_key_env`
- If Threads was disabled or RSSHub failed, omit `threads_accounts` and `rsshub_url`.
- Keep `telegram.enabled` even when Telegram is disabled.
- Keep the user's chosen language and schedule.
- Do not add explanations, markdown fences, or commentary.
