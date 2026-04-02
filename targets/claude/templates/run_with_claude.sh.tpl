#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-}"

if [[ -z "${CLAUDE_BIN}" ]]; then
  if command -v claude >/dev/null 2>&1; then
    CLAUDE_BIN="$(command -v claude)"
  else
    CLAUDE_BIN="__DEFAULT_CLAUDE_BIN__"
  fi
fi

cd "${HOME}"

exec "${CLAUDE_BIN}" -p "Use the newsletter-now skill from the installed skills and run the AI newsletter now. Return only the one-line summary." --dangerously-skip-permissions
