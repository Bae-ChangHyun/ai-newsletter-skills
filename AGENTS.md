# Project Working Rules

## Reinstall Test Flow

- When making code changes that affect installation, onboarding, runtime setup, backend switching, or command exposure, always leave the user's local environment in a clean retest state.
- Keep the user's saved config file if it exists:
  - `~/.ai-newsletter/runtime/.data/config.json`
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
