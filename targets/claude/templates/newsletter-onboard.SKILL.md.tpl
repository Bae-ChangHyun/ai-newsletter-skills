---
name: newsletter-onboard
description: "AI 뉴스레터 초기 설정. 플랫폼, Telegram, 수집 주기를 설정한다. 사용자가 onboarding, 설정 변경, 텔레그램 연동, 주기 변경을 원하면 이 스킬을 사용한다."
allowedTools:
  - "AskUserQuestion"
  - "Bash(curl -s *)"
  - "Bash(mkdir -p *)"
  - "Bash(cat *)"
  - "Read"
  - "Write"
---

# Newsletter Onboard

config를 생성/업데이트한다. 저장 위치는 `__RUNTIME_ROOT__/.data/config.json`이다.

## 1단계: 기존 설정 로드

```bash
cat __RUNTIME_ROOT__/.data/config.json 2>/dev/null
```

## 2단계: 플랫폼 선택

기존 `ai-news-onboard` 흐름과 동일하게 AskUserQuestion으로 글로벌/국내 플랫폼을 나눠 묻고 `platforms` 배열을 만든다.

글로벌 옵션:
- HN (Hacker News) -> `hn`
- Reddit -> `reddit`
- TLDR -> `tldr`
- Threads (RSSHub 필요) -> `threads`

국내 옵션:
- GeekNews (news.hada.io) -> `geeknews`
- Velopers (velopers.kr) -> `velopers`
- DevDay (devday.kr) -> `devday`

## 3단계: 플랫폼별 상세 설정

- Reddit 선택 시 서브레딧 목록을 묻는다.
- Threads 선택 시 RSSHub URL을 묻는다. 기본값은 `http://localhost:1200`이다.
- RSSHub 연결 테스트를 먼저 한다. 우선 `/healthz`, 실패하면 기본 URL 자체를 확인한다.
- 연결이 안 되면 RSSHub 설치/실행 방법을 안내하고 `threads`를 제외한다.

기본 Reddit 서브레딧:
Anthropic, ArtificialInteligence, ClaudeAI, GithubCopilot, LocalLLaMA, ollama, OpenAI, openclaw, opensource, Qwen_AI, Vllm

기본 Threads 계정:
choi.openai, claudeai, programmingzombie, feelfree_ai

연결 실패 시 안내 예시:
- `docker run -d --name rsshub -p 1200:1200 diygod/rsshub`

## 4단계: Telegram 설정

AskUserQuestion으로 Telegram 사용 여부를 묻는다.

사용 시:
- Bot token 입력
- chat_id 입력
- 아래 테스트 메시지로 검증

```bash
curl -s -X POST "https://api.telegram.org/bot{TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "{CHAT_ID}", "text": "✅ 뉴스레터 설정 테스트 성공!"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('OK' if data.get('ok') else 'FAILED')
"
```

## 5단계: 수집 주기

AskUserQuestion으로 아래 중 하나를 선택한다:
- 30분마다 -> `*/30 * * * *`
- 1시간마다 -> `0 * * * *`
- 2시간마다 -> `0 */2 * * *`
- 매일 -> `0 0 * * *`

## 6단계: 저장

```bash
mkdir -p __RUNTIME_ROOT__/.data
```

설정 파일을 저장하고 요약한다.
