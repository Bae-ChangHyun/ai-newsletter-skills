#!/usr/bin/env python3
"""Hacker News AI collector."""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_json, is_ai_related, run_collector, format_output

OUTPUT_MAX_AGE_HOURS = 2


def fetch_items():
    items = []
    cutoff = time.time() - 2 * 3600
    for endpoint in ["topstories", "newstories"]:
        ids = fetch_json(
            f"https://hacker-news.firebaseio.com/v0/{endpoint}.json",
            user_agent="openclaw-hn/1.0",
        )
        if not ids:
            continue
        for sid in ids[:80]:
            item = fetch_json(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                user_agent="openclaw-hn/1.0",
            )
            if not item or item.get("type") != "story":
                continue
            created = item.get("time", 0)
            if created < cutoff:
                continue
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")
            score = item.get("score", 0)
            if not is_ai_related(title, url):
                continue
            items.append({
                "title": title,
                "url": url,
                "source": "HN",
                "time": created,
                "score": score,
            })
    seen = set()
    deduped = []
    for it in items:
        if it["url"] not in seen:
            seen.add(it["url"])
            deduped.append(it)
    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    return deduped


def collect():
    return run_collector("hn", fetch_items, output_max_age_hours=OUTPUT_MAX_AGE_HOURS)


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_HN", file=sys.stderr)
