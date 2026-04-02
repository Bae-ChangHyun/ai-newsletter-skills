#!/usr/bin/env python3
"""Unified newsletter runner — runs selected platform collectors in parallel.

Outputs JSON grouped by platform with score-based filtering applied.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_collector import canonicalize_url, get_entry_state, normalize_title

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", ".data", "config.json")

COLLECTOR_MAP = {
    "hn": "collectors.hn",
    "reddit": "collectors.reddit",
    "geeknews": "collectors.geeknews",
    "tldr": "collectors.tldr",
    "threads": "collectors.threads",
    "velopers": "collectors.velopers",
    "devday": "collectors.devday",
}

DEFAULT_PLATFORMS = ["hn", "reddit", "geeknews", "tldr", "threads", "velopers", "devday"]

# Minimum score thresholds per platform (0 = no filtering)
MIN_SCORE = {
    "hn": 3,
    "reddit": 3,
    "geeknews": 5,
    "tldr": 0,
    "threads": 0,
    "velopers": 0,
    "devday": 0,
}

# Filter out question/error posts (lowercase match)
NOISE_PATTERNS = [
    "keep getting error", "how to ", "how do i ", "any good advice",
    "help me ", "what model does", "question about",
]
DOMAIN_BLOCKLIST = {
    "youtube.com",
    "youtu.be",
    "m.youtube.com",
}
STATE_PRIORITY = {
    "send_failed": 0,
    "curated": 1,
    "ingested": 2,
    "sent": 3,
}


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"platforms": DEFAULT_PLATFORMS}


def run_collector(platform, config):
    import importlib
    module_name = COLLECTOR_MAP.get(platform)
    if not module_name:
        print(f"# WARN: unknown platform {platform}", file=sys.stderr)
        return []

    mod = importlib.import_module(module_name)

    kwargs = {}
    if platform == "reddit" and "subreddits" in config:
        kwargs["subreddits"] = config["subreddits"]
    elif platform == "threads":
        if "threads_accounts" in config:
            kwargs["accounts"] = config["threads_accounts"]
        if "rsshub_url" in config:
            kwargs["rsshub_url"] = config["rsshub_url"]

    return mod.collect(**kwargs)


def is_noise(title):
    t = title.lower()
    return any(p in t for p in NOISE_PATTERNS)


def is_blocked_domain(url):
    domain = urlsplit(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain in DOMAIN_BLOCKLIST


def candidate_priority(item):
    return (
        STATE_PRIORITY.get(get_entry_state(item), 9),
        -(item.get("score", 0) or 0),
        -(item.get("comments", 0) or 0),
        -(item.get("time", 0) or 0),
        item.get("source", ""),
    )


def should_keep(item, platform):
    state = get_entry_state(item)
    if state in {"curated", "send_failed"}:
        return True

    title = (item.get("title") or "").strip()
    url = canonicalize_url(item.get("url", ""))
    score = item.get("score", 0) or 0
    if not title or len(title) < 8 or not url:
        return False
    if is_noise(title):
        return False
    if is_blocked_domain(url):
        return False
    min_score = MIN_SCORE.get(platform, 0)
    if min_score > 0 and score < min_score:
        return False
    return True


def filter_items(items, platform):
    filtered = []
    for item in items:
        if should_keep(item, platform):
            filtered.append(item)
    return filtered


def dedupe_candidates(items):
    by_url = {}
    for item in items:
        key = canonicalize_url(item.get("url", ""))
        if not key:
            continue
        item["url"] = key
        current = by_url.get(key)
        if current is None or candidate_priority(item) < candidate_priority(current):
            by_url[key] = item

    by_title = {}
    for item in by_url.values():
        title_key = normalize_title(item.get("title", ""))
        if not title_key:
            title_key = item["url"]
        current = by_title.get(title_key)
        if current is None or candidate_priority(item) < candidate_priority(current):
            by_title[title_key] = item

    return list(by_title.values())


def main():
    config = load_config()
    platforms = config.get("platforms", DEFAULT_PLATFORMS)
    platform_items = {}
    all_candidates = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(run_collector, p, config): p
            for p in platforms
        }
        for future in as_completed(futures):
            platform = futures[future]
            try:
                items = future.result()
                filtered = filter_items(items, platform)
                deduped = dedupe_candidates(filtered)
                for item in deduped:
                    item["platform"] = platform
                all_candidates.extend(deduped)
                print(f"# {platform}: {len(items)} raw → {len(filtered)} filtered → {len(deduped)} pre-deduped", file=sys.stderr)
            except Exception as e:
                print(f"# ERROR: {platform} failed: {e}", file=sys.stderr)

    final_candidates = dedupe_candidates(all_candidates)
    final_candidates.sort(key=candidate_priority)
    for item in final_candidates:
        platform = item.get("platform") or item.get("source") or "unknown"
        platform_items.setdefault(platform, []).append({
            "title": item["title"],
            "url": item["url"],
            "score": item.get("score", 0),
            "comments": item.get("comments", 0),
            "source": item.get("source", platform),
            "state": get_entry_state(item),
        })

    if platform_items:
        print(
            f"# Total candidates: {len(all_candidates)} collected → {len(final_candidates)} after global prefilter/dedupe",
            file=sys.stderr,
        )
        print(json.dumps(platform_items, ensure_ascii=False, indent=2))
    else:
        print("NO_NEW_ITEMS", file=sys.stderr)


if __name__ == "__main__":
    main()
