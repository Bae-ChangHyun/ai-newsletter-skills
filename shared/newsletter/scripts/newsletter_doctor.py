#!/usr/bin/env python3
"""Newsletter diagnostics: includes previous status output plus targeted checks."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib import error, request


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(RUNTIME_ROOT, ".data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LAST_MESSAGE_FILE = os.path.join(DATA_DIR, "last_run.txt")
MANAGE_CRON = os.path.join(SCRIPT_DIR, "manage_cron.py")
COPILOT_GITHUB_TOKEN_FILE = os.path.join(DATA_DIR, "credentials", "github_copilot_github_token.json")
COPILOT_API_TOKEN_FILE = os.path.join(DATA_DIR, "credentials", "github_copilot_api_token.json")


def load_config() -> dict | None:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def is_korean(config: dict | None) -> bool:
    language = str((config or {}).get("language", "ko")).strip().lower()
    return language.startswith("ko")


def read_last_summary() -> str:
    try:
        with open(LAST_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def cron_status_text() -> str:
    result = subprocess.run(["python3", MANAGE_CRON, "status"], text=True, capture_output=True, check=False)
    return (result.stdout or result.stderr or "").strip() or "unknown"


def maybe_http_ok(url: str, timeout: int = 5) -> tuple[bool, str]:
    req = request.Request(url, headers={"User-Agent": "ai-newsletter-doctor/1.0"})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400, f"HTTP {resp.status}"
    except error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


def backend_checks(config: dict) -> list[tuple[str, str]]:
    backend = ((config.get("backend") or {}).get("type") or "").strip()
    settings = (config.get("backend") or {}).get("settings") or {}
    checks: list[tuple[str, str]] = []

    if backend == "codex":
        checks.append(("Codex CLI", "ok" if shutil.which("codex") else "missing"))
    elif backend == "claude":
        checks.append(("Claude CLI", "ok" if shutil.which("claude") else "missing"))
    elif backend == "openai":
        env_name = settings.get("api_key_env", "OPENAI_API_KEY")
        checks.append(("OpenAI base_url", settings.get("base_url") or "missing"))
        checks.append(("OpenAI model", settings.get("model") or "missing"))
        checks.append((f"OpenAI env {env_name}", "set" if os.environ.get(env_name) else "missing"))
    elif backend == "github_copilot":
        checks.append(("GitHub token cache", "ok" if os.path.exists(COPILOT_GITHUB_TOKEN_FILE) else "missing"))
        checks.append(("Copilot API token cache", "ok" if os.path.exists(COPILOT_API_TOKEN_FILE) else "missing"))
        checks.append(("Copilot model", settings.get("model") or "missing"))
    else:
        checks.append(("Backend", backend or "missing"))

    return checks


def integration_checks(config: dict) -> list[tuple[str, str]]:
    checks: list[tuple[str, str]] = []
    telegram = config.get("telegram") or {}
    if telegram.get("enabled"):
        checks.append(("Telegram bot token", "ok" if telegram.get("bot_token") else "missing"))
        checks.append(("Telegram chat id", "ok" if telegram.get("chat_id") else "missing"))
    else:
        checks.append(("Telegram", "disabled"))

    threads_accounts = config.get("threads_accounts") or []
    rsshub_url = config.get("rsshub_url")
    if threads_accounts:
        if rsshub_url:
            ok, detail = maybe_http_ok(rsshub_url.rstrip("/") + "/healthz")
            checks.append(("RSSHub", f"ok ({detail})" if ok else f"unreachable ({detail})"))
        else:
            checks.append(("RSSHub", "missing"))
        checks.append(("Threads accounts", ", ".join(threads_accounts)))
    return checks


def build_report(config: dict | None, *, alias_mode: str = "doctor") -> str:
    if not config:
        return "저장된 설정이 없습니다. 먼저 newsletter-onboard 를 실행하세요." if alias_mode != "status" else "No config saved yet."

    korean = is_korean(config)
    backend = ((config.get("backend") or {}).get("type") or "-").strip() or "-"
    backend_settings = (config.get("backend") or {}).get("settings") or {}
    schedule = config.get("schedule", {})
    schedule_label = schedule.get("label") or schedule.get("expression") or schedule.get("cron", "-")
    platforms = ", ".join(config.get("platforms", [])) or "-"
    subreddits = ", ".join(config.get("subreddits", [])) or "-"
    cron_text = cron_status_text()
    last_summary = read_last_summary() or "-"

    lines: list[str] = []
    if korean:
        lines.append("뉴스레터 Doctor")
        lines.append(f"- 백엔드: {backend}")
        if backend_settings:
            lines.append(f"- 백엔드 설정: {json.dumps(backend_settings, ensure_ascii=False)}")
        lines.append(f"- 언어: {config.get('language', 'ko')}")
        lines.append(f"- 플랫폼: {platforms}")
        lines.append(f"- 서브레딧: {subreddits}")
        lines.append(f"- 스케줄: {schedule_label}")
        lines.append(f"- 전달 방식: {'Telegram' if (config.get('telegram') or {}).get('enabled') else 'Terminal only'}")
        lines.append(f"- 최근 요약: {last_summary}")
        lines.append("- 진단:")
        for label, value in backend_checks(config) + integration_checks(config):
            lines.append(f"  - {label}: {value}")
        lines.append("- Cron 상태:")
        lines.append(cron_text)
    else:
        lines.append("Newsletter doctor")
        lines.append(f"- Backend: {backend}")
        if backend_settings:
            lines.append(f"- Backend settings: {json.dumps(backend_settings, ensure_ascii=False)}")
        lines.append(f"- Language: {config.get('language', 'ko')}")
        lines.append(f"- Platforms: {platforms}")
        lines.append(f"- Subreddits: {subreddits}")
        lines.append(f"- Schedule: {schedule_label}")
        lines.append(f"- Delivery: {'Telegram' if (config.get('telegram') or {}).get('enabled') else 'Terminal only'}")
        lines.append(f"- Latest summary: {last_summary}")
        lines.append("- Diagnostics:")
        for label, value in backend_checks(config) + integration_checks(config):
            lines.append(f"  - {label}: {value}")
        lines.append("- Cron status:")
        lines.append(cron_text)
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run newsletter diagnostics.")
    parser.add_argument("--alias-mode", choices=("doctor", "status"), default="doctor")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(build_report(load_config(), alias_mode=args.alias_mode))


if __name__ == "__main__":
    main()
