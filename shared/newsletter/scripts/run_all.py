#!/usr/bin/env python3
"""Unified newsletter runner — runs selected platform collectors in parallel.

Outputs JSON grouped by platform with score-based filtering applied.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def filter_items(items, platform):
    min_score = MIN_SCORE.get(platform, 0)
    filtered = []
    for item in items:
        score = item.get("score", 0)
        if min_score > 0 and score < min_score:
            continue
        if is_noise(item.get("title", "")):
            continue
        filtered.append(item)
    return filtered


def main():
    config = load_config()
    platforms = config.get("platforms", DEFAULT_PLATFORMS)
    seen_urls = set()
    platform_items = {}

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
                deduped = []
                for item in filtered:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        deduped.append({
                            "title": item["title"],
                            "url": item["url"],
                            "score": item.get("score", 0),
                            "source": item.get("source", platform),
                        })
                if deduped:
                    platform_items[platform] = deduped
                print(f"# {platform}: {len(items)} raw → {len(filtered)} filtered → {len(deduped)} deduped", file=sys.stderr)
            except Exception as e:
                print(f"# ERROR: {platform} failed: {e}", file=sys.stderr)

    if platform_items:
        print(json.dumps(platform_items, ensure_ascii=False, indent=2))
    else:
        print("NO_NEW_ITEMS", file=sys.stderr)


if __name__ == "__main__":
    main()
