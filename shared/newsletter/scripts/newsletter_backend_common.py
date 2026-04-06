#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone, timedelta


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")
RUN_ALL = os.path.join(SCRIPT_DIR, "run_all.py")
SEND_TELEGRAM = os.path.join(SCRIPT_DIR, "send_telegram.py")
MARK_CURATED = os.path.join(SCRIPT_DIR, "mark_curated.py")
MARK_FAILED = os.path.join(SCRIPT_DIR, "mark_send_failed.py")
MARK_DELIVERED = os.path.join(SCRIPT_DIR, "mark_delivered.py")
LAST_MESSAGE_FILE = os.path.join(RUNTIME_ROOT, ".data", "last_run.txt")
KST = timezone(timedelta(hours=9))


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_prompt(prompt_file: str) -> str:
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def no_news_message(language: str) -> str:
    return "새 뉴스 없음" if language == "ko" else "No new newsletter items"


def log_line(message: str) -> None:
    timestamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{timestamp}] {message}")


def selected_entry_count(selected: dict) -> int:
    return sum(len(entries) for entries in selected.values() if isinstance(entries, list))


def strip_json_response(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def extract_text_content(content) -> str:
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content or "")


def validate_editor_result(payload: dict, provider_name: str) -> dict:
    if not isinstance(payload, dict):
        raise RuntimeError(f"{provider_name} response must be a JSON object")
    summary = payload.get("summary")
    messages = payload.get("messages")
    selected = payload.get("selected")
    if summary is not None and not isinstance(summary, str):
        raise RuntimeError("Editor result.summary must be a string")
    if messages is not None and not isinstance(messages, list):
        raise RuntimeError("Editor result.messages must be a list")
    if selected is not None and not isinstance(selected, dict):
        raise RuntimeError("Editor result.selected must be an object")
    return payload


def run_collect() -> dict:
    result = subprocess.run(["python3", RUN_ALL, "--from-state"], text=True, capture_output=True, check=False)
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    return json.loads(stdout)


def collect_if_needed() -> None:
    if os.environ.get("NEWSLETTER_DELIVERY_MODE") == "deliver-only":
        return
    subprocess.run(["python3", RUN_ALL, "--collect-only"], text=True, check=True)


def mark(script: str, selected: dict) -> None:
    result = subprocess.run(
        ["python3", script],
        input=json.dumps(selected, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=details)


def send_messages(config: dict, messages: list[dict]) -> bool:
    telegram = config.get("telegram", {})
    if not telegram.get("enabled"):
        for item in messages:
            print(item.get("text", "").strip())
            print()
        return True

    for item in messages:
        result = subprocess.run(
            ["python3", SEND_TELEGRAM],
            input=item.get("text", "").strip(),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=details)
    return True


def write_last_message(summary: str) -> None:
    os.makedirs(os.path.dirname(LAST_MESSAGE_FILE), exist_ok=True)
    with open(LAST_MESSAGE_FILE, "w", encoding="utf-8") as f:
        f.write(summary.strip() + "\n")


def run_backend(backend_name: str, prompt_file: str, editorial_call) -> int:
    config = load_config()
    language = config.get("language", "ko")
    mode = os.environ.get("NEWSLETTER_DELIVERY_MODE", "collect-and-deliver")
    log_line(f"RUN start backend={backend_name} mode={mode}")
    collect_if_needed()
    candidates = run_collect()
    if not candidates:
        summary = no_news_message(language)
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 0

    result = editorial_call(config, candidates, read_prompt(prompt_file))
    summary = result.get("summary") or no_news_message(language)
    selected = result.get("selected") or {}
    messages = result.get("messages") or []

    if not selected or not messages:
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 0

    mark(MARK_CURATED, selected)
    entry_count = selected_entry_count(selected)
    log_line(f"STATE curated entries={entry_count}")
    try:
        send_messages(config, messages)
        log_line(f"DELIVERY telegram messages={len(messages)} status=ok")
    except subprocess.CalledProcessError:
        mark(MARK_FAILED, selected)
        log_line(f"STATE send_failed entries={entry_count}")
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 1

    mark(MARK_DELIVERED, selected)
    log_line(f"STATE delivered entries={entry_count}")
    write_last_message(summary)
    log_line(f"SUMMARY {summary}")
    return 0
