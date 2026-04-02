#!/usr/bin/env python3
"""Collect, categorize, format, and optionally send the Codex newsletter."""

import argparse
import datetime as dt
import json
import os
import sys
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import run_all
from send_telegram import escape_mdv2, load_bot_token, send_message

KST = dt.timezone(dt.timedelta(hours=9))
PLATFORM_LABELS = {
    "hn": "HN",
    "reddit": "Reddit",
    "geeknews": "GeekNews",
    "tldr": "TLDR",
    "threads": "Threads",
    "velopers": "Velopers",
    "devday": "DevDay",
}

CATEGORY_RULES = OrderedDict(
    [
        (
            "🔬 모델 & 리서치",
            [
                "model",
                "models",
                "llm",
                "gpt",
                "claude",
                "gemini",
                "qwen",
                "llama",
                "research",
                "paper",
                "arxiv",
                "benchmark",
                "inference",
                "training",
                "quant",
                "reasoning",
                "multimodal",
            ],
        ),
        (
            "🛠️ 도구 & 오픈소스",
            [
                "tool",
                "tools",
                "open source",
                "open-source",
                "sdk",
                "framework",
                "library",
                "cli",
                "agent",
                "mcp",
                "repo",
                "github",
                "release",
                "launch",
                "api",
                "plugin",
                "copilot",
                "cursor",
                "windsurf",
                "ollama",
                "vllm",
            ],
        ),
        (
            "🔒 보안",
            [
                "security",
                "secure",
                "privacy",
                "leak",
                "breach",
                "vulnerability",
                "exploit",
                "attack",
                "injection",
                "jailbreak",
                "safety",
            ],
        ),
        (
            "📊 업계 동향",
            [
                "funding",
                "acquisition",
                "acquire",
                "investment",
                "raises",
                "valuation",
                "partnership",
                "hiring",
                "ceo",
                "company",
                "startup",
                "enterprise",
                "revenue",
            ],
        ),
        (
            "💻 개발 실무",
            [
                "guide",
                "tutorial",
                "how to",
                "engineering",
                "developer",
                "dev",
                "workflow",
                "architecture",
                "migration",
                "production",
                "build",
                "deploy",
                "case study",
                "postmortem",
            ],
        ),
    ]
)


def load_config():
    config = run_all.load_config()
    config.setdefault("telegram", {"enabled": False})
    return config


def collect_items(config):
    platforms = config.get("platforms", run_all.DEFAULT_PLATFORMS)
    seen_urls = set()
    platform_items = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(run_all.run_collector, platform, config): platform
            for platform in platforms
        }
        for future in as_completed(futures):
            platform = futures[future]
            try:
                items = future.result()
            except Exception as exc:
                print(f"# ERROR: {platform} failed: {exc}", file=sys.stderr)
                continue

            filtered = run_all.filter_items(items, platform)
            deduped = []
            for item in filtered:
                if item["url"] in seen_urls:
                    continue
                seen_urls.add(item["url"])
                deduped.append(
                    {
                        "title": item["title"],
                        "url": item["url"],
                        "source": item.get("source", PLATFORM_LABELS.get(platform, platform)),
                        "platform": platform,
                        "score": item.get("score", 0),
                    }
                )
            if deduped:
                platform_items[platform] = deduped

    return platform_items


def categorize_item(item):
    text = f"{item['title']} {item['url']}".lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return None


def categorize_items(platform_items):
    grouped = OrderedDict((category, defaultdict(list)) for category in CATEGORY_RULES)
    uncategorized = 0

    for platform, items in platform_items.items():
        for item in items:
            category = categorize_item(item)
            if not category:
                uncategorized += 1
                continue
            grouped[category][platform].append(item)

    cleaned = OrderedDict()
    for category, by_platform in grouped.items():
        if by_platform:
            cleaned[category] = by_platform
    return cleaned, uncategorized


def build_message_chunks(header, category, platform_items, with_header):
    title = header if with_header else ""
    body_lines = [category, "━━━━━━━━━━━━━━━"]
    for platform, items in platform_items.items():
        body_lines.append(f"▸ {PLATFORM_LABELS.get(platform, platform)}")
        for item in items:
            body_lines.append(f"[{item['title']}]({item['url']})")
        body_lines.append("")

    body = "\n".join(body_lines).strip()
    message = f"{title}\n\n{body}".strip()
    if len(message) <= 3500:
        return [message]

    chunks = []
    current_lines = [title] if title else []
    for line in body_lines:
        tentative = "\n".join(current_lines + [line]).strip()
        if len(tentative) > 3500 and current_lines:
            chunks.append("\n".join(current_lines).strip())
            current_lines = [category, "━━━━━━━━━━━━━━━"] if line.startswith("▸ ") else []
        current_lines.append(line)
    if current_lines:
        chunks.append("\n".join(current_lines).strip())
    return [chunk for chunk in chunks if chunk]


def send_to_telegram(config, header, categorized):
    telegram = config.get("telegram", {})
    if not telegram.get("enabled"):
        return False

    chat_id = telegram.get("chat_id")
    token = load_bot_token()
    if not token or not chat_id:
        print("# Telegram config incomplete; skipped send", file=sys.stderr)
        return False

    first = True
    for category, platform_items in categorized.items():
        chunks = build_message_chunks(header, category, platform_items, with_header=first)
        for chunk in chunks:
            if not send_message(token, chat_id, escape_mdv2(chunk)):
                raise RuntimeError("Telegram 전송 실패")
            first = False
    return True


def render_report(header, categorized):
    lines = [header, ""]
    for category, platform_items in categorized.items():
        lines.append(category)
        lines.append("━━━━━━━━━━━━━━━")
        for platform, items in platform_items.items():
            lines.append(f"[{PLATFORM_LABELS.get(platform, platform)}]")
            for item in items:
                lines.append(f"[{item['title']}]({item['url']})")
            lines.append("")
    return "\n".join(lines).strip()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()
    platform_items = collect_items(config)
    if not platform_items:
        print("새 뉴스 없음")
        return 0

    categorized, uncategorized = categorize_items(platform_items)
    if not categorized:
        print("새 뉴스는 수집됐지만 분류 기준에 맞는 항목이 없습니다.")
        return 0

    now = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    header = f"📡 AI 뉴스레터 ({now})"
    report = render_report(header, categorized)

    sent = False
    if not args.dry_run:
        sent = send_to_telegram(config, header, categorized)

    total_items = sum(len(items) for items in platform_items.values())
    summary = f"{total_items}개 뉴스 수집, {len(categorized)}개 카테고리"
    if sent:
        summary += ", Telegram 전송 완료"
    else:
        summary += ", 터미널 출력"
    if uncategorized:
        summary += f" ({uncategorized}개 항목 제외)"

    if not args.summary_only or not sent:
        print(report)
        print()
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
