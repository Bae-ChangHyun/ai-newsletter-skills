#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROMPT_FILE="${RUNTIME_ROOT}/prompts/run_newsletter_claude.md"
LAST_MESSAGE_FILE="${RUNTIME_ROOT}/.data/last_run.txt"
RAW_ITEMS_FILE="${RUNTIME_ROOT}/.data/raw_items.json"
COLLECT_LOG_FILE="${RUNTIME_ROOT}/.data/collect.log"
DEBUG_LOG_FILE="${RUNTIME_ROOT}/.data/claude.debug.log"
CLAUDE_BIN="${CLAUDE_BIN:-}"
DELIVERY_MODE="${NEWSLETTER_DELIVERY_MODE:-collect-and-deliver}"

mkdir -p "${RUNTIME_ROOT}/.data"

timestamp() {
  TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST'
}

log_line() {
  printf '[%s] %s\n' "$(timestamp)" "$1"
}

if [[ -z "${CLAUDE_BIN}" ]]; then
  if command -v claude >/dev/null 2>&1; then
    CLAUDE_BIN="$(command -v claude)"
  else
    CLAUDE_BIN="__DEFAULT_CLAUDE_BIN__"
  fi
fi

log_line "RUN start backend=claude mode=${DELIVERY_MODE}"

if [[ "${DELIVERY_MODE}" != "deliver-only" ]]; then
  if python3 "${RUNTIME_ROOT}/scripts/run_all.py" --collect-only >/dev/null 2>"${COLLECT_LOG_FILE}"; then
    while IFS= read -r line; do
      [[ -n "${line}" ]] || continue
      log_line "${line}"
    done < "${COLLECT_LOG_FILE}"
  else
    rc=$?
    while IFS= read -r line; do
      [[ -n "${line}" ]] || continue
      log_line "${line}"
    done < "${COLLECT_LOG_FILE}"
    log_line "RUN failed step=collect exit=${rc}"
    exit "${rc}"
  fi
fi

if python3 "${RUNTIME_ROOT}/scripts/run_all.py" --from-state >"${RAW_ITEMS_FILE}" 2>"${COLLECT_LOG_FILE}"; then
  while IFS= read -r line; do
    [[ -n "${line}" ]] || continue
    log_line "${line}"
  done < "${COLLECT_LOG_FILE}"
else
  rc=$?
  while IFS= read -r line; do
    [[ -n "${line}" ]] || continue
    log_line "${line}"
  done < "${COLLECT_LOG_FILE}"
  log_line "RUN failed step=load_pending exit=${rc}"
  exit "${rc}"
fi

if [[ ! -s "${RAW_ITEMS_FILE}" ]]; then
  printf '{}\n' > "${RAW_ITEMS_FILE}"
fi

PROMPT_CONTENT="$(cat "${PROMPT_FILE}")"

if "${CLAUDE_BIN}" -p "${PROMPT_CONTENT}" --dangerously-skip-permissions >"${LAST_MESSAGE_FILE}" 2>"${DEBUG_LOG_FILE}"; then
  SUMMARY=""
  if [[ -f "${LAST_MESSAGE_FILE}" ]]; then
    SUMMARY="$(tail -n 1 "${LAST_MESSAGE_FILE}")"
  fi
  if [[ -n "${SUMMARY}" ]]; then
    log_line "${SUMMARY}"
  else
    log_line "RUN success backend=claude"
  fi
else
  rc=$?
  log_line "RUN failed step=editorial backend=claude exit=${rc} debug_log=${DEBUG_LOG_FILE}"
  exit "${rc}"
fi
