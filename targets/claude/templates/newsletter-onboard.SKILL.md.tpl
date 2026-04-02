---
name: newsletter-onboard
description: "AI 뉴스레터 초기 설정. 플랫폼, Telegram, 수집 주기를 설정한다. 사용자가 onboarding, 설정 변경, 텔레그램 연동, 주기 변경을 원하면 이 스킬을 사용한다."
allowedTools:
  - "AskUserQuestion"
  - "Bash(python3 *)"
  - "Bash(cat *)"
  - "Bash(mkdir -p *)"
  - "Read"
  - "Write"
---

# Newsletter Onboard

온보딩은 이 스킬이 직접 처리한다. 별도 onboarding 스크립트는 사용하지 않는다.

## 절차

1. AskUserQuestion 또는 대화형 질문으로 아래를 수집한다.
- 플랫폼
- Reddit 서브레딧
- 추가 AI 키워드
- Telegram 사용 여부
- Telegram bot token / chat id
- Threads 사용 여부
- RSSHub URL
  - 기본값: `http://localhost:1200`
- Threads 계정명
  - `@` 없이 정확한 계정명을 직접 입력
  - 기본 Threads 계정은 없음
- 주기
  - interval 예: `30m`, `1h`, `2h`, `1d`
  - 또는 5필드 cron 표현식 직접 입력

2. Threads를 켠 경우 RSSHub 연결을 먼저 검증한다.

```bash
python3 - <<'PY' "RSSHUB_URL"
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
PY
```

연결 실패 시:
- RSSHub를 먼저 실행하라고 안내
- `threads`는 config에서 제외

3. 설정 파일을 직접 저장한다.

```bash
mkdir -p __RUNTIME_ROOT__/.data
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
```

설정 파일 저장 위치:
- `__RUNTIME_ROOT__/.data/config.json`

저장 형식:

```json
{
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
    "label": "1시간마다"
  }
}
```

사용하지 않는 optional key는 생략한다.

4. 저장 후 파일을 다시 읽고 요약한다.
