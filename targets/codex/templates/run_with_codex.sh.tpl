#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROMPT_FILE="${RUNTIME_ROOT}/prompts/run_newsletter.md"
LAST_MESSAGE_FILE="${RUNTIME_ROOT}/.data/last_run.txt"
CODEX_BIN="${CODEX_BIN:-}"

mkdir -p "${RUNTIME_ROOT}/.data"

if [[ -z "${CODEX_BIN}" ]]; then
  if command -v codex >/dev/null 2>&1; then
    CODEX_BIN="$(command -v codex)"
  else
    CODEX_BIN="__DEFAULT_CODEX_BIN__"
  fi
fi

exec "${CODEX_BIN}" exec \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -C "__DEFAULT_WORKDIR__" \
  -o "${LAST_MESSAGE_FILE}" \
  - < "${PROMPT_FILE}"

