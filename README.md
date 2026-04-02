# AI Newsletter Skills

[한국어](./README.ko.md)

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

AI Newsletter Skills is a single-repo project for running one newsletter workflow across Claude Code, Codex, GitHub Copilot CLI, and OpenAI-compatible APIs.

It installs one shared runtime under `~/.ai-newsletter`, keeps one shared state directory, and exposes one unified command set:

- `newsletter-onboard`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`
- `newsletter-status`

## Features

- One onboarding flow for every backend
- Shared runtime with no duplicated collector logic
- Shared delivery state across all backends
- Telegram delivery support
- RSSHub support for Threads collection
- Four-stage delivery tracking: `ingested`, `curated`, `send_failed`, `sent`
- Deterministic prefiltering before the editorial pass
- Cron-based scheduled delivery
- Unified command routing by configured backend
- Optional Codex and Claude Code app integration

## Quick Start

Current unified onboarding work is on the `dev` branch. Install the onboarding bootstrap without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
```

Then run:

```bash
newsletter-onboard
```

The first onboarding run downloads and installs the shared runtime automatically. During onboarding, the selected backend integration is installed as part of the setup. After onboarding, use:

```bash
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## No-Clone Install

The repository ships a standalone bootstrap installer at [install.py](./install.py).

It works in two modes:

- Local mode
  - run `python3 install.py` from a checked-out repo
- Bootstrap mode
  - pipe the script from GitHub raw without cloning the repo

Bootstrap examples:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 -
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target codex
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 - --target claude
```

For the current unified onboarding flow on the `dev` branch:

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
```

When run without a local checkout, the bootstrap installer downloads the GitHub tarball into a temporary directory and runs the existing installers from there.

## Installation

### Bootstrap Onboarding

```bash
python3 install.py
```

Installed paths:

- bootstrap launcher: `~/.ai-newsletter/bin/newsletter-onboard`
- bootstrap script: `~/.ai-newsletter/bootstrap_onboard.py`

Runtime notes:

- This installs only the onboarding launcher first
- The first `newsletter-onboard` run downloads and installs the shared runtime automatically
- The selected backend integration is installed during onboarding
- After that, `newsletter-now`, `newsletter-start`, `newsletter-stop`, and `newsletter-status` become available in `~/.ai-newsletter/bin` and `~/.local/bin`

### Common Runtime

```bash
python3 install.py --target common
# or
python3 scripts/install_common.py
```

Installed paths:

- runtime: `~/.ai-newsletter/runtime/`
- commands:
  - `~/.ai-newsletter/bin/newsletter-onboard`
  - `~/.ai-newsletter/bin/newsletter-now`
  - `~/.ai-newsletter/bin/newsletter-start`
  - `~/.ai-newsletter/bin/newsletter-stop`
  - `~/.ai-newsletter/bin/newsletter-status`

Runtime notes:

- Shared `.data` state is preserved across reinstall
- This runtime is enough for `github_copilot` and `openai`
- It is also the shared runtime used by `codex` and `claude`

### Codex Integration

```bash
python3 install.py --target codex
# or
python3 scripts/install_codex.py
```

Installed paths:

- unified runtime: `~/.ai-newsletter/runtime/`
- shell commands: `~/.ai-newsletter/bin/newsletter-*`
- Codex skills:
  - `~/.codex/skills/newsletter-now/`
  - `~/.codex/skills/newsletter-start/`
  - `~/.codex/skills/newsletter-stop/`
  - `~/.codex/skills/newsletter-status/`

Runtime notes:

- Uses the installed `codex` CLI
- Uses `codex exec --dangerously-bypass-approvals-and-sandbox`
- Best results after restarting Codex
- Reinstall preserves existing `.data` state such as config, delivery state, and logs

### Claude Code Integration

```bash
python3 install.py --target claude
# or
python3 scripts/install_claude.py
```

Installed paths:

- unified runtime: `~/.ai-newsletter/runtime/`
- shell commands: `~/.ai-newsletter/bin/newsletter-*`
- Claude skills:
  - `~/.claude/skills/newsletter-now/`
  - `~/.claude/skills/newsletter-start/`
  - `~/.claude/skills/newsletter-stop/`
  - `~/.claude/skills/newsletter-status/`

Runtime notes:

- Uses the installed `claude` CLI
- Uses `claude -p ... --dangerously-skip-permissions`
- Best results after restarting Claude Code
- Reinstall preserves existing `.data` state such as config, delivery state, and logs

## Usage

Use the unified commands from your shell:

```bash
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

`newsletter-onboard`:

- shows a welcome banner and step-by-step wizard
- asks for language first
- asks which backend should generate the runtime config
- asks about source platforms, Telegram, RSSHub, Threads handles, and schedule
- then sends those collected answers to the selected backend so that backend generates `config.json`

RSSHub behavior:

- default URL: `http://localhost:1200`
- health-checks `/healthz` first
- falls back to `/`
- if RSSHub is not reachable, onboarding asks whether to retry or disable Threads

Scheduling behavior:

- `newsletter-start` installs one recurring cron entry for the selected backend
- `newsletter-status` shows both saved config and the current cron line

Delivery behavior:

- items move through `ingested -> curated -> send_failed -> sent`
- `send_failed` items are retried before brand-new candidates
- exact URL/title dedupe and cheap noise filtering run before the editorial pass
- onboarding, status output, and translated newsletter titles follow the configured language
- items are only marked delivered after successful Telegram send or successful terminal output

## Backends

- `claude`
  - Uses the installed `claude` CLI to generate config and run the editorial pass
- `codex`
  - Uses the installed `codex` CLI to generate config and run the editorial pass
- `github_copilot`
  - Runs `copilot login` inside onboarding when you choose it
  - Uses the official device-login flow and then a selected Copilot model
- `openai`
  - Prompts for `base_url`, `model`, and `api_key_env`
  - Calls a generic OpenAI-compatible `/chat/completions` endpoint

## Current Dev Flow

The unified shell-first workflow currently lives on `dev`.

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
  - shared Python runtime, collectors, prompts, delivery-state logic
- `targets/common/templates/`
  - unified onboarding, dispatch, status, and standalone backend runners
- `targets/codex/templates/`
  - Codex skill templates and Codex runner template
- `targets/claude/templates/`
  - Claude skill templates, Claude runner template, Claude subagent template
- `scripts/`
  - installers for the shared runtime and optional app integrations

## Reinstall

Re-run the installers after changing this repository:

```bash
python3 install.py --target common
python3 scripts/install_codex.py
python3 scripts/install_claude.py
```

Existing runtime state in `.data` is preserved across reinstall.
