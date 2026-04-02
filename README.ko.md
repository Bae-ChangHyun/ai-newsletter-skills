# AI Newsletter Skills

[English](./README.md)

## Table of Contents

- [Intro](#intro)
- [Features](#features)
- [Quick Start](#quick-start)
- [No-Clone Install](#no-clone-install)
- [Installation](#installation)
- [Usage](#usage)
- [Backends](#backends)
- [Repository Layout](#repository-layout)
- [Reinstall](#reinstall)

## Intro

AI Newsletter Skills는 Claude Code, Codex, GitHub Copilot CLI, OpenAI-compatible API에서 하나의 뉴스레터 워크플로를 실행하기 위한 단일 저장소 프로젝트입니다.

공통 runtime은 `~/.ai-newsletter` 아래에 설치되고, 상태 파일도 한 곳에서 공유됩니다. 실제 사용 명령은 아래 5개로 통일됩니다.

- `newsletter-onboard`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`
- `newsletter-status`

## Features

- 모든 backend에서 하나의 onboarding 흐름 사용
- 공통 runtime으로 수집 로직 중복 제거
- 모든 backend가 같은 상태 파일과 delivery state 공유
- Telegram 전송 지원
- Threads 수집용 RSSHub 지원
- `ingested`, `curated`, `send_failed`, `sent` 4단계 상태 관리
- 편집 단계 전 deterministic prefiltering
- cron 기반 자동 실행
- 설정된 backend에 따라 내부 분기되는 통합 command 모델
- Codex / Claude Code 앱 연동은 선택적으로 추가 설치 가능

## Quick Start

현재 통합 onboarding 작업은 `dev` 브랜치에 있습니다. clone 없이 onboarding bootstrap만 먼저 설치:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
```

그 다음:

```bash
newsletter-onboard
```

첫 `newsletter-onboard` 실행 때 shared runtime이 자동으로 내려받아 설치됩니다. onboarding 중에 선택한 backend 연동도 같이 설치됩니다. 이후에는:

```bash
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## No-Clone Install

이 저장소에는 독립 실행형 설치 스크립트인 [install.py](./install.py)가 들어 있습니다.

동작 방식은 두 가지입니다:

- Local mode
  - repo를 checkout 한 상태에서 `python3 install.py` 실행
- Bootstrap mode
  - GitHub raw에서 바로 받아 `clone 없이` 설치

Bootstrap 예시:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 -
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target codex
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target claude
```

현재 `dev` 브랜치의 통합 onboarding 흐름은 아래처럼 설치합니다:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
```

로컬 checkout 없이 실행되면, 설치 스크립트가 GitHub tarball을 임시 디렉터리로 내려받아 기존 installer를 실행합니다.

## Installation

### Bootstrap Onboarding

```bash
python3 install.py
```

설치 경로:

- bootstrap launcher: `~/.ai-newsletter/bin/newsletter-onboard`
- bootstrap script: `~/.ai-newsletter/bootstrap_onboard.py`

동작 메모:

- 처음에는 onboarding launcher만 설치함
- 첫 `newsletter-onboard` 실행 시 shared runtime을 자동으로 내려받아 설치함
- onboarding 중 선택한 backend 연동도 같이 설치함
- 설치가 끝나면 `newsletter-now`, `newsletter-start`, `newsletter-stop`, `newsletter-status`도 `~/.ai-newsletter/bin`과 `~/.local/bin` 아래에 생김

### Common Runtime

```bash
python3 install.py --target common
# 또는
python3 scripts/install_common.py
```

설치 경로:

- runtime: `~/.ai-newsletter/runtime/`
- commands:
  - `~/.ai-newsletter/bin/newsletter-onboard`
  - `~/.ai-newsletter/bin/newsletter-now`
  - `~/.ai-newsletter/bin/newsletter-start`
  - `~/.ai-newsletter/bin/newsletter-stop`
  - `~/.ai-newsletter/bin/newsletter-status`

동작 메모:

- `.data` 상태는 재설치 시에도 유지됨
- `github_copilot`와 `openai` backend는 이 공통 runtime만 설치해도 사용 가능
- `codex`와 `claude`도 같은 runtime을 공유해서 사용함

### Codex Integration

```bash
python3 install.py --target codex
# 또는
python3 scripts/install_codex.py
```

설치 경로:

- unified runtime: `~/.ai-newsletter/runtime/`
- shell commands: `~/.ai-newsletter/bin/newsletter-*`
- Codex skills:
  - `~/.codex/skills/newsletter-now/`
  - `~/.codex/skills/newsletter-start/`
  - `~/.codex/skills/newsletter-stop/`
  - `~/.codex/skills/newsletter-status/`

동작 메모:

- 설치된 `codex` CLI를 사용함
- `codex exec --dangerously-bypass-approvals-and-sandbox` 사용
- 설치 후 Codex 재시작 권장
- 재설치해도 `.data` 안의 설정, delivery state, 로그는 유지됨

### Claude Code Integration

```bash
python3 install.py --target claude
# 또는
python3 scripts/install_claude.py
```

설치 경로:

- unified runtime: `~/.ai-newsletter/runtime/`
- shell commands: `~/.ai-newsletter/bin/newsletter-*`
- Claude skills:
  - `~/.claude/skills/newsletter-now/`
  - `~/.claude/skills/newsletter-start/`
  - `~/.claude/skills/newsletter-stop/`
  - `~/.claude/skills/newsletter-status/`

동작 메모:

- 설치된 `claude` CLI를 사용함
- `claude -p ... --dangerously-skip-permissions` 사용
- 설치 후 Claude Code 재시작 권장
- 재설치해도 `.data` 안의 설정, delivery state, 로그는 유지됨

## Usage

셸에서 아래 통합 명령을 사용합니다:

```bash
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

`newsletter-onboard`는:

- 시작 배너와 단계별 wizard를 보여주고
- 언어를 가장 먼저 선택한 뒤
- 어떤 backend가 config를 생성할지 선택하고
- 플랫폼, Telegram, RSSHub, Threads 계정, 스케줄을 순서대로 묻고
- 마지막에는 선택한 backend에게 답변을 넘겨 `config.json`을 생성하게 합니다

RSSHub 동작:

- 기본 URL: `http://localhost:1200`
- 먼저 `/healthz` 확인
- 실패 시 `/`도 한 번 더 확인
- 연결이 안 되면 `RSSHub URL 다시 입력` 또는 `Threads 비활성화 후 계속`을 선택하게 함

스케줄 동작:

- `newsletter-start`는 선택된 backend에 맞는 runner를 반복 cron 1줄로 등록
- `newsletter-status`는 저장된 설정과 현재 cron 등록 상태를 함께 보여줌

전송 동작:

- 항목은 `ingested -> curated -> send_failed -> sent` 흐름으로 이동
- `send_failed` 항목은 새 후보보다 먼저 재시도
- exact URL/title dedupe와 저비용 노이즈 필터를 먼저 적용
- 온보딩, status 출력, 뉴스레터 제목 번역은 설정한 language를 따름
- Telegram 전송 또는 터미널 출력이 성공한 뒤에만 delivered 처리

## Backends

- `claude`
  - 설치된 `claude` CLI가 config 생성과 편집 pass를 담당
- `codex`
  - 설치된 `codex` CLI가 config 생성과 편집 pass를 담당
- `github_copilot`
  - onboarding 중 `copilot login`을 실행할 수 있음
  - 공식 device-login 흐름으로 인증 후 선택한 Copilot 모델 사용
- `openai`
  - `base_url`, `model`, `api_key_env`를 직접 입력
  - generic OpenAI-compatible `/chat/completions` endpoint 호출

## Current Dev Flow

현재 통합 셸 중심 워크플로는 `dev` 브랜치에 있습니다.

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## Repository Layout

- `shared/newsletter/`
  - 공통 Python runtime, 수집기, 프롬프트, delivery-state 로직
- `targets/common/templates/`
  - 통합 onboarding, dispatch, status, standalone backend runner
- `targets/codex/templates/`
  - Codex skill 템플릿과 Codex runner 템플릿
- `targets/claude/templates/`
  - Claude skill 템플릿, Claude runner 템플릿, Claude subagent 템플릿
- `scripts/`
  - 공통 runtime 및 앱 연동용 설치 스크립트

## Reinstall

이 저장소를 수정한 뒤에는 설치 스크립트를 다시 실행하면 됩니다:

```bash
python3 install.py --target common
python3 scripts/install_codex.py
python3 scripts/install_claude.py
```

기존 runtime의 `.data` 상태는 재설치 과정에서 보존됩니다.
