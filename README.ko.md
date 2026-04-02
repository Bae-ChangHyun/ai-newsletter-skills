<h1 align="center">AI Newsletter Skills</h1>

<p align="center">
  Claude Code, Codex, GitHub Copilot, OpenAI-compatible backend를 하나로 묶는 통합 AI 뉴스레터 자동화 프로젝트
</p>

<p align="center">
  <a href="./README.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-D97706?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Codex-111827?style=for-the-badge&logo=openai&logoColor=white" alt="Codex" />
  <img src="https://img.shields.io/badge/GitHub%20Copilot-0F172A?style=for-the-badge&logo=githubcopilot&logoColor=white" alt="GitHub Copilot" />
  <img src="https://img.shields.io/badge/OpenAI%20Compatible-2563EB?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI-compatible" />
</p>

## About

AI Newsletter Skills는 여러 소스에서 AI 관련 뉴스를 가져오고, 눈에 띄는 중복과 노이즈를 걸러낸 뒤, 하나의 흐름으로 정리해서 전달하는 오픈소스 프로젝트입니다.

Hacker News, Reddit, Threads, GeekNews 같은 소스를 하루 종일 직접 확인하지 않고도, 바쁜 사람이 빠르게 훑어볼 수 있는 AI 뉴스레터 시스템을 목표로 합니다.

- `newsletter-onboard`
- `newsletter-status`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`

## Features

- Claude Code, Codex, GitHub Copilot, OpenAI-compatible backend를 하나의 설정 흐름으로 지원
- 온보딩, 상태 확인, 수동 실행, 자동 실행을 하나의 셸 명령 체계로 통일
- 온보딩 중 Telegram 검증 지원
- RSSHub 기반 Threads 연결 확인 지원
- 기존 설정값을 다시 불러오는 재실행 가능한 온보딩
- cron 기반의 로컬 자동 뉴스레터 실행

## Quick Start

최신 통합 흐름은 현재 `dev` 브랜치에 있습니다.

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
newsletter-onboard
```

만약 `newsletter-onboard`가 PATH에 안 잡히면 아래 경로로 실행하면 됩니다.

```bash
~/.ai-newsletter/bin/newsletter-onboard
```

온보딩 후에는:

```bash
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## Onboarding

`newsletter-onboard`는 단계형 wizard를 실행하고 아래 항목을 묻습니다.

- `language`
- `backend`
- source platforms
- Reddit subreddits
- curation에서 더 강조할 extra AI keywords
- Telegram 설정
- RSSHub URL
- Threads handles
- schedule

다시 실행하면 기존 `config.json` 값을 기본값으로 다시 채워줍니다.

<details>
<summary><strong>Telegram 설정</strong></summary>

온보딩 중에:

- bot token을 Telegram `getMe`로 확인하고
- 선택한 chat으로 인증 코드를 보내고
- 입력한 코드가 맞아야 다음 단계로 넘어갑니다

팁:

- 봇 생성: `@BotFather`
- chat id 확인: `@get_id_bot` 같은 헬퍼 봇

</details>

<details>
<summary><strong>RSSHub / Threads 설정</strong></summary>

온보딩 중에:

- 먼저 RSSHub 연결을 `/healthz`와 base URL로 확인하고
- 그다음 Threads handle을 RSSHub feed로 실제 검증합니다
- RSSHub가 안 되면 재입력하거나 Threads를 끄고 계속할 수 있습니다

기본 RSSHub URL:

```text
http://localhost:1200
```

로컬 실행 예시:

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

</details>

## Commands

| Command | 설명 |
| --- | --- |
| `newsletter-onboard` | 통합 설정 wizard를 실행하고 선택한 backend 연동까지 설치합니다 |
| `newsletter-status` | 저장된 backend, language, source, 전달 설정, 현재 cron 줄을 보여줍니다 |
| `newsletter-now` | 설정된 backend로 지금 바로 1회 뉴스레터 사이클을 실행합니다 |
| `newsletter-start` | 설정된 backend용 반복 cron 1줄을 등록합니다 |
| `newsletter-stop` | 뉴스레터 cron 엔트리를 제거합니다 |

## Backends

<details>
<summary><strong>Claude Code</strong></summary>

- 설치된 `claude` CLI를 사용합니다
- `claude -p ... --dangerously-skip-permissions`를 사용합니다
- 온보딩 중 Claude용 newsletter skills를 설치합니다

</details>

<details>
<summary><strong>Codex</strong></summary>

- 설치된 `codex` CLI를 사용합니다
- `codex exec --dangerously-bypass-approvals-and-sandbox`를 사용합니다
- 온보딩 중 Codex용 newsletter skills를 설치합니다

</details>

<details>
<summary><strong>GitHub Copilot CLI</strong></summary>

- 필요하면 온보딩 중 `copilot login`을 실행합니다
- 공식 device-login 흐름을 사용합니다
- 선택한 Copilot 모델로 config 생성과 편집 실행을 처리합니다

</details>

<details>
<summary><strong>OpenAI-compatible</strong></summary>

- `base_url`, `model`, `api_key_env`를 직접 입력합니다
- generic `/chat/completions` endpoint를 호출합니다

</details>

## Notes

- 온보딩을 다시 실행하면 기존 config 값이 기본값으로 재사용됩니다
- 실제 저장 상태를 보려면 `newsletter-status`가 가장 빠릅니다
- cron을 켜기 전에는 `newsletter-now`로 먼저 1회 테스트하는 게 안전합니다
- 현재 통합 흐름은 `dev` 브랜치 기준입니다
