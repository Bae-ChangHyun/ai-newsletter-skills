#!/usr/bin/env python3
"""Show recent newsletter delivery history from runtime state and logs."""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone, timedelta


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
DELIVERY_LOG_FILE = os.path.join(DATA_DIR, "delivery.log")
LAST_MESSAGE_FILE = os.path.join(DATA_DIR, "last_run.txt")
KST = timezone(timedelta(hours=9))
SUMMARY_RE = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+SUMMARY\s+(?P<summary>.+?)\s*$")


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def is_korean(config: dict) -> bool:
    language = str(config.get("language", "ko")).strip().lower()
    return language.startswith("ko")


def format_timestamp(value) -> str:
    if not value:
        return "-"
    dt = datetime.fromtimestamp(float(value), KST)
    return dt.strftime("%Y-%m-%d %H:%M:%S KST")


def seen_file_platform(path: str) -> str:
    name = os.path.basename(path)
    if name.endswith("_seen.jsonl"):
        return name[: -len("_seen.jsonl")]
    return name


def load_delivered_entries(data_dir: str = DATA_DIR) -> list[dict]:
    entries: list[dict] = []
    for seen_file in sorted(glob.glob(os.path.join(data_dir, "*_seen.jsonl"))):
        platform = seen_file_platform(seen_file)
        try:
            with open(seen_file, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line:
                        continue
                    payload = json.loads(line)
                    delivered_at = payload.get("delivered_at")
                    if not delivered_at:
                        continue
                    entries.append(
                        {
                            "platform": platform,
                            "title": payload.get("title", ""),
                            "url": payload.get("url", ""),
                            "source": payload.get("source", platform),
                            "delivered_at": float(delivered_at),
                        }
                    )
        except FileNotFoundError:
            continue
    entries.sort(
        key=lambda item: (
            -(item.get("delivered_at") or 0),
            item.get("platform", ""),
            item.get("title", ""),
        )
    )
    return entries


def count_by_platform(entries: list[dict]) -> Counter:
    return Counter(item.get("platform", "unknown") for item in entries)


def read_last_summary(path: str = LAST_MESSAGE_FILE) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def read_recent_summaries(log_file: str = DELIVERY_LOG_FILE, limit: int = 5) -> list[dict]:
    matches: list[dict] = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                match = SUMMARY_RE.match(line)
                if not match:
                    continue
                matches.append(
                    {
                        "timestamp": match.group("timestamp"),
                        "summary": match.group("summary"),
                    }
                )
    except FileNotFoundError:
        return []
    return matches[-limit:]


def build_output(config: dict, delivered_entries: list[dict], last_summary: str, recent_summaries: list[dict], limit: int) -> str:
    korean = is_korean(config)
    backend = ((config.get("backend") or {}).get("type") or "-").strip() or "-"
    totals = count_by_platform(delivered_entries)
    lines: list[str] = []

    if korean:
        lines.append("뉴스레터 발송 이력")
        lines.append(f"- 백엔드: {backend}")
        lines.append(f"- 최근 요약: {last_summary or '-'}")
        lines.append(f"- 누적 발송 기사 수: {len(delivered_entries)}")
        if totals:
            lines.append("- 플랫폼별 누적 발송 수:")
            for platform, count in sorted(totals.items()):
                lines.append(f"  - {platform}: {count}")
        if delivered_entries:
            lines.append(f"- 최근 발송 기사 {min(limit, len(delivered_entries))}건:")
            for item in delivered_entries[:limit]:
                lines.append(
                    "  - "
                    f"{format_timestamp(item.get('delivered_at'))} "
                    f"[{item.get('platform')}] {item.get('title') or '(제목 없음)'}"
                )
                if item.get("url"):
                    lines.append(f"    {item['url']}")
        else:
            lines.append("- 최근 발송 기사: 없음")
        if recent_summaries:
            lines.append("- 최근 실행 요약:")
            for item in reversed(recent_summaries):
                lines.append(f"  - {item['timestamp']} :: {item['summary']}")
    else:
        lines.append("Newsletter delivery history")
        lines.append(f"- Backend: {backend}")
        lines.append(f"- Latest summary: {last_summary or '-'}")
        lines.append(f"- Total delivered items: {len(delivered_entries)}")
        if totals:
            lines.append("- Delivered totals by platform:")
            for platform, count in sorted(totals.items()):
                lines.append(f"  - {platform}: {count}")
        if delivered_entries:
            lines.append(f"- Recent delivered items ({min(limit, len(delivered_entries))}):")
            for item in delivered_entries[:limit]:
                lines.append(
                    "  - "
                    f"{format_timestamp(item.get('delivered_at'))} "
                    f"[{item.get('platform')}] {item.get('title') or '(untitled)'}"
                )
                if item.get("url"):
                    lines.append(f"    {item['url']}")
        else:
            lines.append("- Recent delivered items: none")
        if recent_summaries:
            lines.append("- Recent run summaries:")
            for item in reversed(recent_summaries):
                lines.append(f"  - {item['timestamp']} :: {item['summary']}")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show recent newsletter delivery history.")
    parser.add_argument("--limit", type=int, default=10, help="maximum number of delivered items to show")
    parser.add_argument("--summary-limit", type=int, default=5, help="maximum number of run summaries to show")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    delivered_entries = load_delivered_entries()
    last_summary = read_last_summary()
    recent_summaries = read_recent_summaries(limit=max(1, args.summary_limit))
    print(build_output(config, delivered_entries, last_summary, recent_summaries, max(1, args.limit)))


if __name__ == "__main__":
    main()
