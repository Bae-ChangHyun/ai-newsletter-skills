---
name: newsletter-now
description: "AI 뉴스를 지금 바로 수집한다. 새 뉴스 후보를 수집하고 분류하여 Telegram 또는 터미널로 전달한다."
allowedTools:
  - "Agent"
  - "Bash(cat *)"
---

# Newsletter Now

실제 수집/분류/전송 작업은 서브에이전트에게 위임한다.

## 실행

Agent 도구로 `news-collector` 서브에이전트를 실행한다:

- `subagent_type`: `news-collector`
- `prompt`: `RUNTIME_ROOT=__RUNTIME_ROOT__ 경로의 runtime에서 뉴스를 수집하고 전달하라.`
- `description`: `AI 뉴스 수집`

반환은 한 줄 요약만 전달한다.

