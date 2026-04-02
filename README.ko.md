# AI Newsletter Skills

[English](./README.md)

## Table of Contents

- [Intro](#intro)
- [Features](#features)
- [Skill List](#skill-list)
- [Quick Start](#quick-start)
- [No-Clone Install](#no-clone-install)
- [Installation](#installation)
- [Usage](#usage)
- [Repository Layout](#repository-layout)
- [Reinstall](#reinstall)

## Intro

AI Newsletter Skills는 Claude Code와 Codex에서 같은 뉴스레터 워크플로우를 사용할 수 있게 만드는 단일 저장소입니다.

수집기, Telegram 전송, delivery tracking, cron 관리는 하나의 공용 Python runtime으로 공유하고, 각 플랫폼에는 전용 skill 파일만 생성합니다.

## Features

- Claude Code와 Codex에서 동일한 스킬 이름 사용
- 수집 로직 중복 없는 공용 runtime
- Telegram 전송 지원
- Threads 수집용 RSSHub 지원
- `ingested`, `curated`, `send_failed`, `sent` 4단계 상태 관리
- Claude/Codex 큐레이션 전에 deterministic 1차 필터 적용
- cron 기반 자동 실행
- 양쪽 모두 비대화형 runner 지원
- AI 키워드 필터와 Threads 계정명을 사용자 입력으로 설정

## Skill List

- `newsletter-onboard`
  - 플랫폼, Telegram, RSSHub, 주기 설정
- `newsletter-now`
  - 즉시 뉴스레터 수집 및 전송
- `newsletter-start`
  - 반복 cron 등록
- `newsletter-stop`
  - 등록된 cron 제거
- `newsletter-status`
  - 현재 저장된 설정과 실제 cron 등록 상태 확인

## Quick Start

clone 없이 바로 설치할 수 있습니다:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target all
```

플랫폼 하나만 설치하려면:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target codex
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target claude
```

설치 후에는 해당 앱 또는 CLI 세션을 다시 시작해야 새 스킬이 반영됩니다.

일반적인 사용 순서:

```text
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
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target all
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target codex
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target claude
```

로컬 checkout 없이 실행되면, 설치 스크립트가 GitHub tarball을 임시 디렉터리로 내려받아 기존 platform installer를 실행합니다.

## Installation

### Codex

```bash
python3 install.py --target codex
# 또는
python3 scripts/install_codex.py
```

설치 경로:

- runtime: `~/.codex/skills/newsletter-runtime/`
- skills:
  - `~/.codex/skills/newsletter-onboard/`
  - `~/.codex/skills/newsletter-now/`
  - `~/.codex/skills/newsletter-start/`
  - `~/.codex/skills/newsletter-stop/`
  - `~/.codex/skills/newsletter-status/`

동작 메모:

- `codex exec --dangerously-bypass-approvals-and-sandbox` 사용
- 설치 후 Codex 재시작 권장
- 재설치해도 `.data` 안의 설정, delivery state, 로그는 유지됨

### Claude Code

```bash
python3 install.py --target claude
# 또는
python3 scripts/install_claude.py
```

설치 경로:

- runtime: `~/.claude/skills/newsletter-runtime/`
- skills:
  - `~/.claude/skills/newsletter-onboard/`
  - `~/.claude/skills/newsletter-now/`
  - `~/.claude/skills/newsletter-start/`
  - `~/.claude/skills/newsletter-stop/`
  - `~/.claude/skills/newsletter-status/`

동작 메모:

- `claude -p ... --dangerously-skip-permissions` 사용
- 설치 후 Claude Code 재시작 권장
- 재설치해도 `.data` 안의 설정, delivery state, 로그는 유지됨

## Usage

`newsletter-onboard`에서 설정하는 항목:

- 수집 플랫폼
- 선택적 AI 키워드 필터
- Telegram bot token / chat id
- Threads용 RSSHub URL
- `@` 없는 Threads 계정명
- 반복 실행 주기

RSSHub 동작:

- 기본 URL: `http://localhost:1200`
- 먼저 `/healthz` 확인
- 실패 시 `/`도 한 번 더 확인
- 연결이 안 되면 `threads`를 자동으로 비활성화

스케줄 동작:

- `newsletter-start`는 사용자가 입력한 cron 한 줄만 등록
- `newsletter-status`는 저장된 설정과 현재 cron 줄을 함께 보여줌

전송 동작:

- 항목은 `ingested -> curated -> send_failed -> sent` 흐름으로 이동
- `send_failed` 항목은 새 후보보다 먼저 재시도
- exact URL/title dedupe와 저비용 노이즈 필터를 먼저 적용
- Telegram 전송 또는 터미널 출력이 성공한 뒤에만 delivered 처리

## Repository Layout

- `shared/newsletter/`
  - 공용 Python runtime, collectors, prompts, delivery-state logic
- `targets/codex/templates/`
  - Codex skill 템플릿과 Codex runner 템플릿
- `targets/claude/templates/`
  - Claude skill 템플릿, Claude runner 템플릿, Claude subagent 템플릿
- `scripts/`
  - 플랫폼별 설치 스크립트

## Reinstall

이 저장소를 수정한 뒤에는 설치 스크립트를 다시 실행하면 됩니다:

```bash
python3 install.py --target all
python3 scripts/install_codex.py
python3 scripts/install_claude.py
```

기존 runtime의 `.data` 상태는 재설치 과정에서 보존됩니다.
