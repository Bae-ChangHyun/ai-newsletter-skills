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
LOG_FILE = os.path.join(RUNTIME_ROOT, ".data", "cron.log")
DEFAULT_MARKER = "# newsletter-runtime"
INTERVAL_RE = re.compile(r"^\s*(\d+)\s*([mhd])\s*$")

LEGACY_PATTERNS = (
    "run_with_codex.sh",
    "run_with_claude.sh",
    "newsletter_now.py",
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
    for candidate in ("run_with_codex.sh", "run_with_claude.sh"):
        path = os.path.join(SCRIPT_DIR, candidate)
        if os.path.exists(path):
            return path
    return os.path.join(SCRIPT_DIR, "run_with_codex.sh")


def resolve_marker() -> str:
    return os.environ.get("NEWSLETTER_MARKER", DEFAULT_MARKER)


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


def is_newsletter_line(line: str, marker: str, runner: str) -> bool:
    if marker in line or runner in line:
        return True
    return any(pattern in line for pattern in LEGACY_PATTERNS)


def filter_newsletter_lines(lines, marker: str, runner: str):
    return [line for line in lines if not is_newsletter_line(line, marker, runner)]


def anchored_schedule_from_interval(expression: str, now: datetime) -> tuple[str, str]:
    target = now + timedelta(minutes=2)
    match = INTERVAL_RE.match(expression)
    if not match:
        raise ValueError(f"지원하지 않는 interval 형식: {expression}")

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "m":
        if 60 % value != 0:
            raise ValueError(f"지원하지 않는 분 interval: {expression}. 60의 약수를 사용하거나 cron을 입력하세요.")
        minutes = sorted({(target.minute + value * step) % 60 for step in range(60 // value)})
        cron = f"{','.join(str(minute) for minute in minutes)} * * * *"
        desc = f"매 {value}분, 분 {', '.join(f'{minute:02d}' for minute in minutes)} 기준"
        return cron, desc

    if unit == "h":
        if 24 % value != 0:
            raise ValueError(f"지원하지 않는 시간 interval: {expression}. 24의 약수를 사용하거나 cron을 입력하세요.")
        hours = sorted({(target.hour + value * step) % 24 for step in range(24 // value)})
        cron = f"{target.minute} {','.join(str(hour) for hour in hours)} * * *"
        desc = f"매 {value}시간, {target.minute:02d}분 / 시각 {', '.join(f'{hour:02d}' for hour in hours)} 기준"
        return cron, desc

    if unit == "d":
        if value != 1:
            raise ValueError(f"지원하지 않는 day interval: {expression}. 1d 또는 cron을 사용하세요.")
        cron = f"{target.minute} {target.hour} * * *"
        desc = f"매일 {target.hour:02d}:{target.minute:02d} 기준"
        return cron, desc

    raise ValueError(f"지원하지 않는 interval 단위: {unit}")


def resolve_schedule(schedule: dict, now: datetime) -> tuple[str, str]:
    if schedule.get("mode") == "interval" and schedule.get("expression"):
        return anchored_schedule_from_interval(schedule["expression"], now)
    if schedule.get("cron"):
        return schedule["cron"], f"사용자 지정 cron 유지: {schedule['cron']}"
    raise ValueError("유효한 schedule 설정이 없습니다")


def build_entry(cron_schedule: str, runner: str, marker: str) -> str:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    return f"{cron_schedule} {runner} >> {LOG_FILE} 2>&1 {marker}"


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

    try:
        resolved_cron, resolved_desc = resolve_schedule(schedule, datetime.now())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    runner = resolve_runner()
    marker = resolve_marker()
    lines = filter_newsletter_lines(read_crontab(), marker, runner)
    lines.append(build_entry(resolved_cron, runner, marker))
    write_crontab(lines)

    print(f"뉴스레터가 cron에 등록되었습니다: {label}")
    if schedule.get("mode") == "interval":
        print("반복 기준 시각: 현재 시각 기준 2분 뒤")
    print(f"적용 cron: {resolved_cron}")
    print(f"설명: {resolved_desc}")
    print(f"로그 파일: {LOG_FILE}")
    return 0


def stop():
    runner = resolve_runner()
    marker = resolve_marker()
    current = read_crontab()
    filtered = filter_newsletter_lines(current, marker, runner)
    if filtered == current:
        print("등록된 뉴스레터 스케줄이 없습니다.")
        return 0

    write_crontab(filtered)
    print("뉴스레터 자동 수집이 중단되었습니다.")
    return 0


def status():
    runner = resolve_runner()
    marker = resolve_marker()
    current = [line for line in read_crontab() if is_newsletter_line(line, marker, runner)]
    if not current:
        print("등록된 뉴스레터 스케줄이 없습니다.")
        return 0
    for line in current:
        print(line)
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
