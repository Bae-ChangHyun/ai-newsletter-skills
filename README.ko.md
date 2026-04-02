# AI Newsletter Skills

[English](./README.md)

## Intro

AI Newsletter Skills는 Claude Code, Codex, GitHub Copilot CLI, OpenAI-compatible API를 하나의 셸 중심 뉴스레터 워크플로로 묶는 프로젝트입니다.

공통 runtime은 `~/.ai-newsletter` 아래에 설치되고, 상태 파일도 한 곳에서 공유됩니다. 실제 사용 명령은 아래 5개로 통일됩니다.

- `newsletter-onboard`
- `newsletter-status`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`

온보딩은 한 번만 진행하면 되고, 중요한 입력값을 검증한 뒤 선택한 backend 연동을 설치하고, 마지막에는 그 backend가 `config.json`을 생성합니다.

## Features

- 모든 backend에서 하나의 onboarding 흐름 사용
- 공통 runtime과 공통 `.data` 상태 공유
- backend별 명령 대신 셸 명령 하나로 통일된 사용 흐름
- 온보딩 중 Telegram 검증 지원
- RSSHub 기반 Threads 수집과 연결 확인
- `ingested`, `curated`, `send_failed`, `sent` 4단계 delivery recovery
- 편집 단계 전 deterministic prefiltering
- cron 기반 자동 실행
- language에 맞춘 onboarding, status, 뉴스레터 생성

## Workflow

1. bootstrap launcher를 설치합니다.
2. `newsletter-onboard`를 실행합니다.
3. `claude`, `codex`, `github_copilot`, `openai` 중 backend를 고릅니다.
4. 공통 질문에 한 번만 답합니다.
5. 선택한 backend가 `config.json`을 생성합니다.
6. `newsletter-status`로 저장된 설정을 확인합니다.
7. `newsletter-now`로 수동 1회 실행을 확인합니다.
8. `newsletter-start`로 반복 cron을 등록합니다.

## Quick Start

현재 통합 흐름은 `dev` 브랜치에 있습니다.

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
newsletter-onboard
```

온보딩 후에는:

```bash
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## Onboarding

`newsletter-onboard`는 단계형 interactive wizard를 실행합니다.

수집하고 검증하는 항목:

- `language`
- `backend`
- source platforms
- Reddit subreddits
- curation에서 더 강조할 extra AI keywords
- Telegram 설정
- RSSHub URL
- Threads handles
- schedule

중요 동작:

- 기존 `config.json`이 있으면 그 값을 기본값으로 다시 채움
- Telegram은 bot token 확인 후 chat으로 인증 코드를 보내서 검증함
- RSSHub 연결이 확인된 뒤에만 Threads를 활성화함
- Threads handle은 RSSHub feed로 실제 검증함
- Reddit subreddit은 Reddit 조회 결과를 기준으로 canonical 이름으로 정리함
- 최종 `config.json`은 선택한 backend가 생성함

## Commands

### `newsletter-onboard`

통합 설정 wizard를 실행하고, 선택한 backend 연동까지 설치합니다.

### `newsletter-status`

아래 내용을 보여줍니다.

- 선택된 backend
- language
- 활성화된 platforms
- 저장된 subreddit 목록
- 저장된 schedule
- Telegram 상태
- Threads / RSSHub 설정
- 현재 등록된 cron 줄

### `newsletter-now`

설정된 backend로 지금 바로 1회 뉴스레터 사이클을 실행합니다.

### `newsletter-start`

설정된 backend용 반복 cron 1줄을 등록합니다.

### `newsletter-stop`

뉴스레터 cron 엔트리를 제거합니다.

## Backends

### Claude Code

- 설치된 `claude` CLI를 사용함
- `claude -p ... --dangerously-skip-permissions` 사용
- onboarding 중 Claude용 newsletter skills 설치

### Codex

- 설치된 `codex` CLI를 사용함
- `codex exec --dangerously-bypass-approvals-and-sandbox` 사용
- onboarding 중 Codex용 newsletter skills 설치

### GitHub Copilot CLI

- 필요하면 onboarding 중 `copilot login` 실행
- 공식 device-login 흐름 사용
- 선택한 Copilot 모델로 config 생성과 편집 pass 수행

### OpenAI-compatible

- `base_url`, `model`, `api_key_env`를 직접 입력
- generic `/chat/completions` endpoint 호출

## Delivery Model

항목은 아래 상태를 거칩니다.

- `ingested`
- `curated`
- `send_failed`
- `sent`

동작 방식:

- 편집 단계 전에 exact dedupe와 prefiltering을 먼저 수행
- `send_failed` 항목은 새 후보보다 먼저 재시도
- Telegram 전송 또는 터미널 출력이 성공한 뒤에만 delivered 처리

## Installation Details

### Bootstrap만 설치

```bash
python3 install.py
```

설치되는 것:

- `~/.ai-newsletter/bin/newsletter-onboard`
- `~/.ai-newsletter/bootstrap_onboard.py`

첫 onboarding 실행 시 shared runtime이 자동 설치됩니다.

### Optional direct installers

```bash
python3 install.py --target common
python3 install.py --target codex
python3 install.py --target claude
```

이 경로는 주로 개발 중이거나 직접 integration 테스트할 때 유용합니다.

## Repository Layout

- `shared/newsletter/`
  - 공통 runtime, 수집기, 프롬프트, delivery state 로직
- `targets/common/templates/`
  - 통합 onboarding, dispatch, status, standalone backend runner
- `targets/codex/templates/`
  - Codex 연동 템플릿
- `targets/claude/templates/`
  - Claude 연동 템플릿
- `scripts/`
  - installer와 runtime setup helper

## Development Notes

통합 onboarding과 셸 중심 runtime은 현재 `dev` 브랜치에서 개발 중입니다.

최신 통합 흐름을 테스트하려면:

```bash
git clone https://github.com/Bae-ChangHyun/ai-newsletter-skills.git
cd ai-newsletter-skills
git checkout dev
python3 install.py
newsletter-onboard
```
