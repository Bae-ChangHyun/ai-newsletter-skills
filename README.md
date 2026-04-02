# AI Newsletter Skills

[한국어](./README.ko.md)

## Intro

AI Newsletter Skills is a unified shell-first newsletter workflow for Claude Code, Codex, GitHub Copilot CLI, and OpenAI-compatible APIs.

It installs one shared runtime under `~/.ai-newsletter`, keeps one shared state directory, and exposes one command set:

- `newsletter-onboard`
- `newsletter-status`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`

The onboarding flow asks once, validates the important inputs, installs the selected backend integration, and lets that backend generate `config.json`.

## Features

- One onboarding flow for all supported backends
- Shared runtime and shared `.data` state across backends
- Shell-first workflow instead of backend-specific command syntax
- Telegram delivery with verification during onboarding
- RSSHub-based Threads collection with connectivity checks
- Four-stage delivery recovery: `ingested`, `curated`, `send_failed`, `sent`
- Deterministic prefiltering before the editorial pass
- Cron-based scheduled delivery
- Language-aware onboarding, status output, and newsletter generation

## Workflow

1. Install the bootstrap launcher.
2. Run `newsletter-onboard`.
3. Choose a backend: `claude`, `codex`, `github_copilot`, or `openai`.
4. Answer the shared setup questions once.
5. Let the selected backend generate `config.json`.
6. Use `newsletter-status` to confirm the saved settings.
7. Use `newsletter-now` for a manual run.
8. Use `newsletter-start` to register the recurring cron job.

## Quick Start

The current unified flow lives on the `dev` branch.

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
newsletter-onboard
```

After onboarding:

```bash
newsletter-status
newsletter-now
newsletter-start
newsletter-stop
```

## Onboarding

`newsletter-onboard` uses a guided interactive wizard.

It collects and validates:

- `language`
- `backend`
- source platforms
- Reddit subreddits
- extra AI keywords to emphasize in curation
- Telegram settings
- RSSHub URL
- Threads handles
- schedule

Important behavior:

- Existing `config.json` values are loaded back into onboarding as defaults
- Telegram setup verifies the bot token and sends a verification code to the chat
- RSSHub is checked before Threads are enabled
- Threads handles are validated through RSSHub feeds
- Reddit subreddits are resolved against Reddit and normalized to canonical names
- The selected backend generates the final `config.json`

## Commands

### `newsletter-onboard`

Runs the unified setup wizard and installs the selected backend integration.

### `newsletter-status`

Shows:

- selected backend
- language
- enabled platforms
- saved subreddit list
- saved schedule
- Telegram status
- Threads and RSSHub settings
- current cron registration line

### `newsletter-now`

Runs one immediate newsletter cycle with the configured backend.

### `newsletter-start`

Registers one recurring cron entry for the configured backend.

### `newsletter-stop`

Removes the newsletter cron entry.

## Backends

### Claude Code

- Uses the installed `claude` CLI
- Uses `claude -p ... --dangerously-skip-permissions`
- Installs Claude-side newsletter skills during onboarding

### Codex

- Uses the installed `codex` CLI
- Uses `codex exec --dangerously-bypass-approvals-and-sandbox`
- Installs Codex-side newsletter skills during onboarding

### GitHub Copilot CLI

- Runs `copilot login` during onboarding when needed
- Uses the official device-login flow
- Uses the selected Copilot model to generate config and run the editorial pass

### OpenAI-compatible

- Prompts for `base_url`, `model`, and `api_key_env`
- Calls a generic `/chat/completions` endpoint

## Delivery Model

Items move through these states:

- `ingested`
- `curated`
- `send_failed`
- `sent`

Behavior:

- cheap exact dedupe and prefiltering happen before the editorial pass
- `send_failed` items are retried before brand-new candidates
- items are marked delivered only after successful Telegram send or successful terminal output

## Installation Details

### Bootstrap only

```bash
python3 install.py
```

Installs:

- `~/.ai-newsletter/bin/newsletter-onboard`
- `~/.ai-newsletter/bootstrap_onboard.py`

The first onboarding run installs the shared runtime automatically.

### Optional direct installers

```bash
python3 install.py --target common
python3 install.py --target codex
python3 install.py --target claude
```

These are mostly useful for development or direct integration testing.

## Repository Layout

- `shared/newsletter/`
  - shared runtime, collectors, prompts, delivery state logic
- `targets/common/templates/`
  - unified onboarding, dispatch, status, and standalone backend runners
- `targets/codex/templates/`
  - Codex integration templates
- `targets/claude/templates/`
  - Claude integration templates
- `scripts/`
  - installers and runtime setup helpers

## Development Notes

The unified onboarding and shell-first runtime are currently being developed on `dev`.

Use this branch for the latest integrated onboarding flow:

```bash
git clone https://github.com/Bae-ChangHyun/ai-newsletter-skills.git
cd ai-newsletter-skills
git checkout dev
python3 install.py
newsletter-onboard
```
