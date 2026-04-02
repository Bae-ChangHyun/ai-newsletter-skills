# AI Newsletter Skills

[한국어](./README.ko.md)

<p align="center">
  <img src="https://img.shields.io/badge/branch-dev-0f172a?style=for-the-badge" alt="dev branch" />
  <img src="https://img.shields.io/badge/runtime-shared-2563eb?style=for-the-badge" alt="shared runtime" />
  <img src="https://img.shields.io/badge/workflow-shell--first-059669?style=for-the-badge" alt="shell first workflow" />
  <img src="https://img.shields.io/badge/backends-claude%20%7C%20codex%20%7C%20copilot%20%7C%20openai-7c3aed?style=for-the-badge" alt="supported backends" />
</p>

## About

AI Newsletter Skills is a unified newsletter workflow for Claude Code, Codex, GitHub Copilot CLI, and OpenAI-compatible APIs.

It installs one shared runtime under `~/.ai-newsletter`, keeps one shared state directory, and gives you one command set:

- `newsletter-onboard`
- `newsletter-status`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`

The setup flow asks once, validates the important inputs, installs the selected backend integration, and lets that backend generate `config.json`.

## Features

- One onboarding flow for every supported backend
- One shared runtime and one shared state directory
- Telegram delivery with verification during onboarding
- RSSHub-based Threads support with connectivity checks
- Language-aware onboarding, status output, and newsletter generation
- Recurring delivery through a single cron-based shell workflow

## Quick Start

The unified flow currently lives on the `dev` branch.

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

`newsletter-onboard` runs a guided wizard and asks for:

- `language`
- `backend`
- source platforms
- Reddit subreddits
- extra AI keywords to emphasize in curation
- Telegram settings
- RSSHub URL
- Threads handles
- schedule

It also reloads existing `config.json` values as defaults when you run onboarding again.

<details>
<summary><strong>Telegram setup</strong></summary>

During onboarding:

- the bot token is checked with Telegram `getMe`
- a verification code is sent to the selected chat
- onboarding proceeds only when the entered code matches

Tips:

- Create the bot with `@BotFather`
- Get the target chat id with a helper such as `@get_id_bot`

</details>

<details>
<summary><strong>RSSHub and Threads setup</strong></summary>

During onboarding:

- RSSHub is checked first, using `/healthz` and then the base URL
- Threads handles are validated through RSSHub feeds
- if RSSHub is unavailable, onboarding lets you retry or disable Threads

Default RSSHub URL:

```text
http://localhost:1200
```

Example local run:

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

</details>

## Commands

| Command | What it does |
| --- | --- |
| `newsletter-onboard` | Runs the unified setup wizard and installs the selected backend integration |
| `newsletter-status` | Shows the saved backend, language, sources, delivery settings, and current cron line |
| `newsletter-now` | Runs one immediate newsletter cycle with the configured backend |
| `newsletter-start` | Registers one recurring cron entry for the configured backend |
| `newsletter-stop` | Removes the newsletter cron entry |

## Backends

<details>
<summary><strong>Claude Code</strong></summary>

- Uses the installed `claude` CLI
- Uses `claude -p ... --dangerously-skip-permissions`
- Installs Claude-side newsletter skills during onboarding

</details>

<details>
<summary><strong>Codex</strong></summary>

- Uses the installed `codex` CLI
- Uses `codex exec --dangerously-bypass-approvals-and-sandbox`
- Installs Codex-side newsletter skills during onboarding

</details>

<details>
<summary><strong>GitHub Copilot CLI</strong></summary>

- Runs `copilot login` during onboarding when needed
- Uses the official device-login flow
- Uses the selected Copilot model for config generation and editorial runs

</details>

<details>
<summary><strong>OpenAI-compatible</strong></summary>

- Prompts for `base_url`, `model`, and `api_key_env`
- Calls a generic `/chat/completions` endpoint

</details>

## Notes

- Existing config values are reused when onboarding is run again
- `newsletter-status` is the fastest way to confirm what is actually saved
- `newsletter-now` is the safest way to smoke-test delivery before enabling cron
- The current integrated branch for this unified flow is `dev`
