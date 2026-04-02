# AI Newsletter Skills

[한국어](./README.ko.md)

## Table of Contents

- [Intro](#intro)
- [Features](#features)
- [Skill List](#skill-list)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Repository Layout](#repository-layout)
- [Reinstall](#reinstall)

## Intro

AI Newsletter Skills is a single-repo project for running the same newsletter workflow in both Claude Code and Codex.

It keeps one shared Python runtime for collection, Telegram delivery, delivery tracking, and cron management, while generating platform-specific skill files for each target.

## Features

- Same end-user skill names in Claude Code and Codex
- Shared runtime with no duplicated collector logic
- Telegram delivery support
- RSSHub support for Threads collection
- Separate `seen` and `sent` state tracking
- Cron-based scheduled delivery
- Bypass-style non-interactive runners for both platforms

## Skill List

- `newsletter-onboard`
  - Configure platforms, Telegram, RSSHub, and schedule
- `newsletter-now`
  - Collect and send the newsletter immediately
- `newsletter-start`
  - Register the recurring cron job
- `newsletter-stop`
  - Remove the registered cron job
- `newsletter-status`
  - Show saved settings plus current cron registration state

## Quick Start

Install for the platform you want to use:

```bash
python3 scripts/install_codex.py
python3 scripts/install_claude.py
```

Then restart the relevant app or CLI session so the new skills are loaded.

Typical workflow:

```text
newsletter-onboard
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## Installation

### Codex

```bash
python3 scripts/install_codex.py
```

Installed paths:

- runtime: `~/.codex/skills/newsletter-runtime/`
- skills:
  - `~/.codex/skills/newsletter-onboard/`
  - `~/.codex/skills/newsletter-now/`
  - `~/.codex/skills/newsletter-start/`
  - `~/.codex/skills/newsletter-stop/`
  - `~/.codex/skills/newsletter-status/`

Runtime notes:

- Uses `codex exec --dangerously-bypass-approvals-and-sandbox`
- Best results after restarting Codex
- Reinstall preserves existing `.data` state such as config, delivery state, and logs

### Claude Code

```bash
python3 scripts/install_claude.py
```

Installed paths:

- runtime: `~/.claude/skills/newsletter-runtime/`
- skills:
  - `~/.claude/skills/newsletter-onboard/`
  - `~/.claude/skills/newsletter-now/`
  - `~/.claude/skills/newsletter-start/`
  - `~/.claude/skills/newsletter-stop/`
  - `~/.claude/skills/newsletter-status/`

Runtime notes:

- Uses `claude -p ... --dangerously-skip-permissions`
- Best results after restarting Claude Code
- Reinstall preserves existing `.data` state such as config, delivery state, and logs

## Usage

`newsletter-onboard` configures:

- source platforms
- Telegram bot token and chat id
- RSSHub URL for Threads
- recurring schedule

RSSHub behavior:

- default URL: `http://localhost:1200`
- health-checks `/healthz` first
- falls back to `/`
- disables `threads` automatically if RSSHub is not reachable

Scheduling behavior:

- `newsletter-start` installs one recurring cron entry
- the recurring schedule is anchored from `current time + 2 minutes`
- `newsletter-status` shows both saved config and the current cron line

Delivery behavior:

- items are collected into pending candidates
- items are only marked delivered after successful Telegram send or successful terminal output

## Repository Layout

- `shared/newsletter/`
  - shared Python runtime, collectors, prompts, delivery-state logic
- `targets/codex/templates/`
  - Codex skill templates and Codex runner template
- `targets/claude/templates/`
  - Claude skill templates, Claude runner template, Claude subagent template
- `scripts/`
  - installers for each platform

## Reinstall

Re-run the installers after changing this repository:

```bash
python3 scripts/install_codex.py
python3 scripts/install_claude.py
```

Existing runtime state in `.data` is preserved across reinstall.
