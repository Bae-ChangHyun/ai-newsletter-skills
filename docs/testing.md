# Testing

## Fast checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q install.py scripts shared/newsletter/scripts
```

## Backend smoke test

Smoke tests reuse fixed collected fixture items and still execute the real AI backend for:

- selection
- deduplication judgment
- categorization
- message composition
- delivery-state transitions

Run:

```bash
python3 scripts/smoke_backends.py --backend all --mode terminal --skip-missing
```

Notes:

- Fixture size is intentionally small to keep runtime down.
- `claude`, `codex`, `github_copilot`, and `openai` are run one backend at a time.
- Backends are skipped when local credentials or required env vars are missing.
- Use `--mode telegram` for final live verification.
- Use `--keep-temp` when debugging a failed backend.
- Use `--timeout <seconds>` to cap slow backend runs.

## Cron smoke test

To verify that cron registration, execution, and automatic cleanup work with a real backend:

```bash
python3 scripts/smoke_cron.py --backend all --skip-missing --timeout 150
```

Behavior:

- builds a temporary runtime with fixture pending items
- writes a cron schedule for the next minute (or the minute after if too close to rollover)
- registers the cron job
- waits for execution
- verifies delivered state updates
- removes the cron entry automatically

This path intentionally skips the collector cron and immediate collect step so the smoke run stays fixture-based and does not fetch live sources.

### OpenAI smoke env

```bash
export SMOKE_OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export SMOKE_OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_API_KEY="..."
```

### Telegram live smoke env

```bash
export SMOKE_TELEGRAM_BOT_TOKEN="..."
export SMOKE_TELEGRAM_CHAT_ID="..."
```
