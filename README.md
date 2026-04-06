<div align="center">

# AI Newsletter Skills

**Curated AI news, delivered automatically — powered by the AI agent of your choice.**

Pull from 7 supported sources. Remove noise with AI. Receive a digest on Telegram or preview locally — all from one CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Bae-ChangHyun/ai-newsletter-skills?style=flat-square&color=f9c74f)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/stargazers)
[![Issues](https://img.shields.io/github/issues/Bae-ChangHyun/ai-newsletter-skills?style=flat-square&color=ef476f)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/issues)
<br>
[![Claude Code](https://img.shields.io/badge/Claude%20Code-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/code)
[![Codex](https://img.shields.io/badge/Codex-111827?style=flat-square&logo=openai&logoColor=white)](https://openai.com/codex)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-0F172A?style=flat-square&logo=githubcopilot&logoColor=white)](https://github.com/features/copilot)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI%20Compatible-2563EB?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/)

[한국어](./README.ko.md)

</div>

---

## Table of Contents

- [Why This Project](#-why-this-project)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
- [Onboarding Wizard](#-onboarding-wizard)
- [AI Engines](#-ai-engines)
- [News Sources](#-news-sources)
- [License](#-license)

---

## Why This Project

Keeping up with AI is a full-time job.

Every day there are new papers, tools, GitHub repos, and community threads across Hacker News, Reddit, Threads, and a dozen niche forums. Manually checking all of them takes time most developers do not have.

**AI Newsletter Skills automates the entire pipeline:**

- Collect from 7 supported sources on a schedule
- Use your preferred AI engine to filter noise and summarize what matters
- Deliver a clean digest to Telegram or the terminal — no third-party service, no subscription

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      News Sources (7)                       │
│  Hacker News · Reddit · Threads · GeekNews                  │
│  DevDay · TLDR · Velopers                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │  collect
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Collectors (Python)                       │
│       Fetch → Deduplicate → Normalize                       │
└──────────────────────┬──────────────────────────────────────┘
                       │  raw items
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Engine (your choice)                    │
│   Claude Code  │  Codex  │  GitHub Copilot  │  OpenAI API   │
│   Filter noise · Score relevance · Write digest             │
└──────────────────────┬──────────────────────────────────────┘
                       │  curated digest
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Delivery                        │
│         Bot API → Your chat or group channel                │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

- **One-command install** — a single `curl | python3` line sets everything up
- **Interactive onboarding wizard** — guided setup with live validation and re-runnable config
- **4 AI engines** — Claude Code, Codex, GitHub Copilot, and any OpenAI-compatible endpoint
- **7 supported news sources** — Hacker News, Reddit, Threads (via RSSHub), GeekNews, DevDay, TLDR, Velopers
- **Telegram delivery** — bot token verification and chat ID confirmation during onboarding
- **Terminal-only preview mode** — skip Telegram and print the digest locally when desired
- **RSSHub integration** — health-checked Threads collection with graceful fallback
- **Cron-based scheduling** — one recurring entry, registered and removed with a single command
- **Config preservation** — re-running onboarding reloads previous values as defaults
- **5 shell commands** — one word for each operation: onboard, status, now, start, stop

---

## Quick Start

**Requirements**

- `python3`
- `node` and `npm`
- `crontab` / cron
- One AI backend you plan to use (`codex`, `claude`, GitHub Copilot, or an OpenAI-compatible API key)

**Step 1 — Install**

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 -
```

**Step 2 — Run the wizard**

```bash
newsletter-onboard
```

> If `newsletter-onboard` is not on your `PATH`:
> ```bash
> ~/.ai-newsletter/bin/newsletter-onboard
> ```

**Step 3 — Verify and run**

```bash
newsletter-status   # confirm what was saved
newsletter-now      # send one digest immediately
newsletter-start    # enable the recurring cron schedule
```

That's it. Your Telegram will receive curated AI news on the schedule you set, or `newsletter-now` will print the digest locally if you choose terminal-only delivery.

---

## Commands

| Command | Description |
| --- | --- |
| `newsletter-onboard` | Run the guided setup wizard and install the selected AI engine integration |
| `newsletter-status` | Show AI engine, language, sources, delivery mode, and active cron lines |
| `newsletter-now` | Run one immediate newsletter cycle with the configured AI engine |
| `newsletter-start` | Register one recurring cron entry for the configured AI engine |
| `newsletter-stop` | Remove the newsletter cron entry |

---

## Onboarding Wizard

`newsletter-onboard` walks through every setting interactively:

| Prompt | What it configures |
| --- | --- |
| Language | Digest output language |
| AI Engine | Which AI agent runs the editorial step |
| Sources | Which platforms to pull from |
| Subreddits | Reddit communities to monitor |
| Delivery mode | Telegram delivery or terminal-only preview |
| Telegram bot token | Delivery endpoint (live-verified via `getMe`) |
| Telegram chat ID | Target chat or group |
| RSSHub URL | Base URL for Threads collection |
| Threads handles | Accounts to follow via RSSHub |
| Schedule | Cron expression for recurring delivery |

Running `newsletter-onboard` again reloads existing `config.json` values as defaults — nothing is lost unless you change it.

<details>
<summary><strong>Telegram setup details</strong></summary>

During onboarding:

- The bot token is checked with the Telegram `getMe` API
- A verification code is sent to the selected chat
- Onboarding proceeds only when the entered code matches

Tips:

- Create the bot with `@BotFather` on Telegram
- Get the target chat ID with a helper such as `@get_id_bot`

</details>

<details>
<summary><strong>RSSHub and Threads setup</strong></summary>

During onboarding:

- RSSHub is health-checked using `/healthz`, then the base URL
- Threads handles are validated through live RSSHub feeds
- If RSSHub is unavailable, onboarding lets you retry or disable Threads collection

Default RSSHub URL:

```
http://localhost:1200
```

Run RSSHub locally with Docker:

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

</details>

---

## AI Engines

<details>
<summary><strong>Claude Code</strong></summary>

- Requires the `claude` CLI installed and authenticated
- Runs `claude -p ... --dangerously-skip-permissions` for headless execution
- Installs Claude-side newsletter skill templates during onboarding

</details>

<details>
<summary><strong>Codex</strong></summary>

- Requires the `codex` CLI installed and authenticated
- Runs `codex exec --dangerously-bypass-approvals-and-sandbox`
- Installs Codex-side skill templates during onboarding

</details>

<details>
<summary><strong>GitHub Copilot</strong></summary>

- Uses the official GitHub device-login OAuth flow during onboarding
- Opens a browser verification page and waits for approval
- Uses the selected Copilot model for config generation and editorial runs

</details>

<details>
<summary><strong>OpenAI-compatible</strong></summary>

- Prompts for `base_url`, `model`, and `api_key_env` during onboarding
- Calls a standard `/chat/completions` endpoint
- Works with any provider that is API-compatible with OpenAI (Groq, Together, local Ollama, etc.)

</details>

---

## News Sources

| Source | Coverage |
| --- | --- |
| Hacker News | Top AI and tech submissions |
| Reddit | Configurable subreddits (e.g. r/MachineLearning, r/LocalLLaMA) |
| Threads | Accounts via RSSHub feed |
| GeekNews | Korean tech community posts |
| DevDay | Developer-focused AI announcements |
| TLDR | Curated tech newsletter |
| Velopers | Korean developer community |

---

## License

Distributed under the [MIT License](LICENSE).

---

<div align="center">

Built with care by [Bae-ChangHyun](https://github.com/Bae-ChangHyun) and contributors.

If this project saves you time, consider giving it a star.

[![GitHub Stars](https://img.shields.io/github/stars/Bae-ChangHyun/ai-newsletter-skills?style=social)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/stargazers)

</div>
