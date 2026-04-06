#!/usr/bin/env python3
"""Manage crontab entries for the newsletter runner."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")
DELIVERY_LOG_FILE = os.path.join(RUNTIME_ROOT, ".data", "delivery.log")
COLLECT_LOG_FILE = os.path.join(RUNTIME_ROOT, ".data", "collect.log")
DEFAULT_MARKER = "# newsletter-runtime"
COLLECTOR_MARKER = "# newsletter-collector-runtime"
KNOWN_DELIVERY_MARKERS = {
    DEFAULT_MARKER,
    "# claude-newsletter-runtime",
    "# codex-newsletter-runtime",
    "# openai-newsletter-runtime",
    "# github-copilot-newsletter-runtime",
}
INTERVAL_RE = re.compile(r"^\s*(\d+)\s*([mhd])\s*$")

LEGACY_DELIVERY_PATTERNS = (
    "run_with_codex.sh",
    "run_with_claude.sh",
    "run_with_openai.py",
    "run_with_copilot.py",
    "newsletter_now.py",
    "newsletter_dispatch.py",
    "ai-news-newsletter",
    "codex-ai-newsletter",
)


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def resolve_runner() -> str:
    env_runner = os.environ.get("NEWSLETTER_RUNNER")
    if env_runner:
        return env_runner
    for candidate in (
        "run_with_copilot.py",
        "run_with_openai.py",
        "run_with_codex.sh",
        "run_with_claude.sh",
    ):
        path = os.path.join(SCRIPT_DIR, candidate)
        if os.path.exists(path):
            return path
    return os.path.join(SCRIPT_DIR, "run_with_codex.sh")


def resolve_marker() -> str:
    return os.environ.get("NEWSLETTER_MARKER", DEFAULT_MARKER)


def resolve_collector_marker() -> str:
    return os.environ.get("NEWSLETTER_COLLECTOR_MARKER", COLLECTOR_MARKER)


def smoke_skip_collector() -> bool:
    return os.environ.get("NEWSLETTER_SMOKE_SKIP_COLLECTOR", "").strip() in {"1", "true", "yes", "on"}


def smoke_skip_immediate_collect() -> bool:
    return os.environ.get("NEWSLETTER_SMOKE_SKIP_IMMEDIATE_COLLECT", "").strip() in {"1", "true", "yes", "on"}


def collect_script_path() -> str:
    return os.path.join(SCRIPT_DIR, "run_collect_cycle.py")


def read_crontab():
    result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def write_crontab(lines):
    text = "\n".join(lines).rstrip()
    if text:
        text += "\n"
    subprocess.run(["crontab", "-"], input=text, text=True, check=True)


def parse_interval_expression(expression: str) -> tuple[int, str] | None:
    match = INTERVAL_RE.match(expression or "")
    if not match:
        return None
    return int(match.group(1)), match.group(2)


def validate_interval_expression(expression: str) -> tuple[bool, str | None]:
    parsed = parse_interval_expression(expression)
    if not parsed:
        return False, "Use an interval like 30m, 1h, 6h, 12h, 24h/1d or a 5-field cron."

    value, unit = parsed
    if value <= 0:
        return False, "Interval must be greater than zero."

    if unit == "m":
        if 60 % value != 0:
            return False, f"Unsupported minute interval: {expression}. Use a divisor of 60 or a 5-field cron."
        return True, None

    if unit == "h":
        if value == 24:
            return True, None
        if value > 24 or 24 % value != 0:
            return False, f"Unsupported hour interval: {expression}. Use a divisor of 24, 24h/1d, or a 5-field cron."
        return True, None

    if unit == "d":
        if value != 1:
            return False, f"Unsupported day interval: {expression}. Use 1d or a 5-field cron."
        return True, None

    return False, f"Unsupported interval unit: {unit}"


def anchored_schedule_from_interval(expression: str, now: datetime, offset_minutes: int = 5) -> tuple[str, str]:
    target = now + timedelta(minutes=offset_minutes)
    parsed = parse_interval_expression(expression)
    if not parsed:
        raise ValueError(f"지원하지 않는 interval 형식: {expression}")

    supported, message = validate_interval_expression(expression)
    if not supported:
        raise ValueError(message or f"지원하지 않는 interval 형식: {expression}")

    value, unit = parsed

    if unit == "m":
        minutes = sorted({(target.minute + value * step) % 60 for step in range(60 // value)})
        cron = f"{','.join(str(minute) for minute in minutes)} * * * *"
        desc = f"매 {value}분, 분 {', '.join(f'{minute:02d}' for minute in minutes)} 기준"
        return cron, desc

    if unit == "h":
        if value == 24:
            cron = f"{target.minute} {target.hour} * * *"
            desc = f"매일 {target.hour:02d}:{target.minute:02d} 기준"
            return cron, desc
        hours = sorted({(target.hour + value * step) % 24 for step in range(24 // value)})
        cron = f"{target.minute} {','.join(str(hour) for hour in hours)} * * *"
        desc = f"매 {value}시간, {target.minute:02d}분 / 시각 {', '.join(f'{hour:02d}' for hour in hours)} 기준"
        return cron, desc

    if unit == "d":
        cron = f"{target.minute} {target.hour} * * *"
        desc = f"매일 {target.hour:02d}:{target.minute:02d} 기준"
        return cron, desc

    raise ValueError(f"지원하지 않는 interval 단위: {unit}")


def resolve_schedule(schedule: dict, now: datetime) -> tuple[str, str]:
    if schedule.get("mode") == "interval" and schedule.get("expression"):
        return anchored_schedule_from_interval(schedule["expression"], now, offset_minutes=5)
    if schedule.get("cron"):
        return schedule["cron"], f"사용자 지정 cron 유지: {schedule['cron']}"
    raise ValueError("유효한 schedule 설정이 없습니다")


def resolve_collector_schedule(schedule: dict, now: datetime) -> tuple[str, str]:
    if schedule.get("mode") == "interval" and schedule.get("expression"):
        cron, desc = anchored_schedule_from_interval(schedule["expression"], now, offset_minutes=0)
        return cron, f"전송 주기를 따르는 선행 수집: {desc}"
    minute = now.minute
    return f"{minute} * * * *", f"사용자 지정 cron 보조 수집: 매시간 {minute:02d}분"


def build_delivery_entry(cron_schedule: str, runner: str, marker: str) -> str:
    os.makedirs(os.path.dirname(DELIVERY_LOG_FILE), exist_ok=True)
    return (
        f"{cron_schedule} NEWSLETTER_DELIVERY_MODE=deliver-only {runner} "
        f">> {DELIVERY_LOG_FILE} 2>&1 {marker}"
    )


def build_collector_entry(cron_schedule: str) -> str:
    os.makedirs(os.path.dirname(COLLECT_LOG_FILE), exist_ok=True)
    marker = resolve_collector_marker()
    return f"{cron_schedule} python3 {collect_script_path()} >> {COLLECT_LOG_FILE} 2>&1 {marker}"


def run_immediate_collect() -> bool:
    os.makedirs(os.path.dirname(COLLECT_LOG_FILE), exist_ok=True)
    with open(COLLECT_LOG_FILE, "a", encoding="utf-8") as log_file:
        result = subprocess.run(
            ["python3", collect_script_path()],
            stdout=log_file,
            stderr=log_file,
            text=True,
            check=False,
        )
    return result.returncode == 0


def classify_newsletter_line(line: str, runner: str | None = None) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    collector_script = collect_script_path()
    runtime_root_match = RUNTIME_ROOT in stripped
    marker_match = any(marker in stripped for marker in KNOWN_DELIVERY_MARKERS | {resolve_collector_marker()})

    if collector_script in stripped:
        return "collector"
    if resolve_collector_marker() in stripped and runtime_root_match:
        return "collector"
    if runner and runner in stripped:
        return "delivery"
    if marker_match and runtime_root_match:
        return "collector" if resolve_collector_marker() in stripped else "delivery"
    if runtime_root_match and any(pattern in stripped for pattern in LEGACY_DELIVERY_PATTERNS):
        return "delivery"
    return None


def filter_newsletter_lines(lines, runner: str):
    return [line for line in lines if classify_newsletter_line(line, runner) is None]


def start():
    config = load_config()
    if not config:
        print("설정 파일이 없습니다. 먼저 뉴스레터 설정을 실행하세요.", file=sys.stderr)
        return 1

    schedule = config.get("schedule", {})
    label = schedule.get("label") or schedule.get("expression") or schedule.get("cron", "미설정")
    if not schedule:
        print("schedule 값이 없습니다. 설정을 다시 저장하세요.", file=sys.stderr)
        return 1

    now = datetime.now()
    try:
        resolved_cron, resolved_desc = resolve_schedule(schedule, now)
        collector_cron, collector_desc = resolve_collector_schedule(schedule, now)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    runner = resolve_runner()
    marker = resolve_marker()
    lines = filter_newsletter_lines(read_crontab(), runner)
    if not smoke_skip_collector():
        lines.append(build_collector_entry(collector_cron))
    lines.append(build_delivery_entry(resolved_cron, runner, marker))
    write_crontab(lines)
    immediate_collect_ok = True if smoke_skip_immediate_collect() else run_immediate_collect()

    print(f"뉴스레터 cron이 등록되었습니다: {label}")
    if smoke_skip_collector():
        print("수집 cron: smoke-skip")
        print("수집 설명: smoke test skipped collector registration")
    else:
        print(f"수집 cron: {collector_cron}")
        print(f"수집 설명: {collector_desc}")
    print(f"전송 cron: {resolved_cron}")
    print(f"전송 설명: {resolved_desc}")
    print(f"수집 로그: {COLLECT_LOG_FILE}")
    print(f"전송 로그: {DELIVERY_LOG_FILE}")
    if not immediate_collect_ok:
        print("경고: 즉시 수집 1회 실행은 실패했습니다. 로그를 확인하세요.", file=sys.stderr)
    return 0


def stop():
    runner = resolve_runner()
    current = read_crontab()
    filtered = filter_newsletter_lines(current, runner)
    if filtered == current:
        print("등록된 뉴스레터 스케줄이 없습니다.")
        return 0

    write_crontab(filtered)
    print("뉴스레터 자동 수집이 중단되었습니다.")
    return 0


def status():
    runner = resolve_runner()
    current = read_crontab()
    found = False
    for line in current:
        classification = classify_newsletter_line(line, runner)
        if classification is None:
            continue
        found = True
        print(f"{classification}: {line}")
    if not found:
        print("등록된 뉴스레터 스케줄이 없습니다.")
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "stop", "status"}:
        print("Usage: manage_cron.py [start|stop|status]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    if command == "start":
        sys.exit(start())
    if command == "stop":
        sys.exit(stop())
    sys.exit(status())


if __name__ == "__main__":
    main()
