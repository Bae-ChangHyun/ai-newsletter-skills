<h1 align="center">AI Newsletter Skills</h1>

<p align="center">
  Unified AI newsletter automation for Claude Code, Codex, GitHub Copilot, and OpenAI-compatible backends.
</p>

<p align="center">
  <a href="./README.ko.md">한국어</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-D97706?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Codex-111827?style=for-the-badge&logo=openai&logoColor=white" alt="Codex" />
  <img src="https://img.shields.io/badge/GitHub%20Copilot-0F172A?style=for-the-badge&logo=githubcopilot&logoColor=white" alt="GitHub Copilot" />
  <img src="https://img.shields.io/badge/OpenAI%20Compatible-2563EB?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI-compatible" />
</p>

## About

AI Newsletter Skills is an open-source project that pulls AI news from multiple sources, removes obvious noise and duplicates, and delivers a curated digest through one unified workflow.

- `newsletter-onboard`
- `newsletter-status`
- `newsletter-now`
- `newsletter-start`
- `newsletter-stop`

It is designed for people who want one practical system for staying on top of fast-moving AI updates without manually checking Hacker News, Reddit, Threads, GeekNews, and similar feeds all day.

## Features

- One setup flow for Claude Code, Codex, GitHub Copilot, and OpenAI-compatible backends
- One shell command set for onboarding, status checks, manual runs, and scheduling
- Telegram verification during onboarding and RSSHub checks for Threads collection
- Re-runnable onboarding with existing config prefilled as defaults
- Local scheduled delivery with a single recurring cron workflow

## Quick Start

The latest unified flow currently lives on the `dev` branch.

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/dev/install.py | python3 -
newsletter-onboard
```

If `newsletter-onboard` is not on your `PATH`, run:

```bash
~/.ai-newsletter/bin/newsletter-onboard
```

After onboarding, use:

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
