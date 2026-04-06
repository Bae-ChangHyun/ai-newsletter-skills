# Project Working Rules

## Reinstall Test Flow

- When making code changes that affect installation, onboarding, runtime setup, backend switching, or command exposure, always leave the user's local environment in a clean retest state.
- Keep the user's saved config file if it exists:
  - `~/.ai-newsletter/runtime/.data/config.json`
- Before handing work back after a commit/push for installer, onboarding, or runtime changes, delete the rest of the runtime state so the user can do a final clean retest:
  - `~/.ai-newsletter/runtime/.data/*` except `config.json`
  - this includes seen files, auth/token files, logs, and `last_run.txt`
- Remove the rest of the installed newsletter artifacts before handing testing back to the user:
  - `~/.ai-newsletter` runtime files other than the preserved `config.json`
  - `~/.local/bin/newsletter-*`
  - `~/.claude/skills/newsletter-*`
  - `~/.codex/skills/newsletter-*`
  - newsletter-related cron entries
- After cleanup, give the user only the reinstall / retest command(s) they should run next.
- Prefer a pinned commit-hash install URL over a branch URL when raw GitHub caching could cause stale installer behavior.

## User Handoff

- After installer or onboarding fixes, explicitly tell the user whether they should run:
  - `rehash`
  - `newsletter-onboard`
  - `newsletter-start`
  - or a pinned `curl | python` installer command
- Do not assume the user's previous installed runtime is still valid after installer changes.

## GitHub Copilot Multipliers

- GitHub Copilot model multipliers shown in onboarding must be sourced from GitHub Docs, not inferred from the Copilot `/models` API.
- Source of truth:
  - `https://docs.github.com/en/copilot/concepts/billing/copilot-requests`
- When updating Copilot onboarding, model labels, or supported-model handling:
  - Re-check the "Model multipliers" table in that docs page and refresh the in-repo multiplier mapping to match it.
  - Keep the onboarding label compact as `x0`, `x0.33`, `x1`, `x3`, etc.
  - Keep a visible reference to the GitHub Docs page in the onboarding flow so users can verify current pricing themselves.
- `openclaw/openclaw` does not currently expose or maintain this multiplier table in its GitHub Copilot provider, so do not use `openclaw` as the source of truth for pricing labels.
