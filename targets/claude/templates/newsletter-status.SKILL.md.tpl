---
name: newsletter-status
description: "현재 등록된 AI 뉴스레터 cron 상태를 확인한다."
allowedTools:
  - "Bash(cat *)"
  - "Bash(python3 *)"
---

# Newsletter Status

```bash
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
NEWSLETTER_RUNNER=__RUNTIME_ROOT__/scripts/run_with_claude.sh NEWSLETTER_MARKER='# claude-newsletter-runtime' python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

config에 저장된 플랫폼, Telegram 사용 여부, 주기 설정, AI 키워드, Threads 계정과 RSSHub URL, 현재 cron 등록 상태를 함께 요약한다.
