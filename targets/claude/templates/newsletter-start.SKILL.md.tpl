---
name: newsletter-start
description: "AI 뉴스레터 자동 수집을 시작한다. config의 주기 설정에 따라 시스템 crontab에 등록한다."
allowedTools:
  - "Bash(cat *)"
  - "Bash(python3 *)"
  - "Read"
---

# Newsletter Start

## 실행

```bash
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
NEWSLETTER_RUNNER=__RUNTIME_ROOT__/scripts/run_with_claude.sh NEWSLETTER_MARKER='# claude-newsletter-runtime' python3 __RUNTIME_ROOT__/scripts/manage_cron.py start
NEWSLETTER_RUNNER=__RUNTIME_ROOT__/scripts/run_with_claude.sh NEWSLETTER_MARKER='# claude-newsletter-runtime' python3 __RUNTIME_ROOT__/scripts/manage_cron.py status
```

반복 스케줄은 config에 저장된 cron 표현식을 그대로 등록한다.
