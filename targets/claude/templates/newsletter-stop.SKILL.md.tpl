---
name: newsletter-stop
description: "AI 뉴스레터 자동 수집을 중단한다. 시스템 crontab에서 newsletter 스케줄을 제거한다."
allowedTools:
  - "Bash(python3 *)"
---

# Newsletter Stop

## 절차

```bash
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
NEWSLETTER_RUNNER=__RUNTIME_ROOT__/scripts/run_with_claude.sh NEWSLETTER_MARKER='# claude-newsletter-runtime' python3 __RUNTIME_ROOT__/scripts/manage_cron.py stop
NEWSLETTER_RUNNER=__RUNTIME_ROOT__/scripts/run_with_claude.sh NEWSLETTER_MARKER='# claude-newsletter-runtime' python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

응답은 가능하면 `config.language`를 따른다.
