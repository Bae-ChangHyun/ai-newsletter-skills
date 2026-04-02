#!/usr/bin/env python3
"""Reddit AI collector."""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_json, is_ai_related, run_collector, format_output

OUTPUT_MAX_AGE_HOURS = 1
DEFAULT_SUBREDDITS = [
    "Anthropic", "ArtificialInteligence", "ClaudeAI", "GithubCopilot",
    "LocalLLaMA", "ollama", "OpenAI", "openclaw", "opensource", "Qwen_AI", "Vllm",
]


def fetch_items(subreddits=None):
    if subreddits is None:
        subreddits = DEFAULT_SUBREDDITS
    seen_urls = set()
    items = []
    cutoff = time.time() - 1 * 3600
    endpoints = ["hot.json?limit=30", "rising.json?limit=20"]
    for sub in subreddits:
        for endpoint in endpoints:
            data = fetch_json(
                f"https://www.reddit.com/r/{sub}/{endpoint}",
                user_agent="openclaw-reddit/1.0",
            )
            if not data or "data" not in data:
                continue
            for post in data["data"]["children"]:
                d = post["data"]
                created = d.get("created_utc", 0)
                if created < cutoff:
                    continue
                title = d.get("title", "")
                url = d.get("url", "")
                permalink = f"https://reddit.com{d.get('permalink', '')}"
                if permalink in seen_urls:
                    continue
                seen_urls.add(permalink)
                score = d.get("score", 0)
                if not is_ai_related(title, url):
                    continue
                items.append({
                    "title": title,
                    "url": permalink,
                    "source": f"r/{sub}",
                    "time": created,
                    "score": score,
                    "comments": d.get("num_comments", 0),
                })
    items.sort(key=lambda x: x.get("score", 0), reverse=True)
    return items


def collect(subreddits=None):
    return run_collector(
        "reddit",
        lambda: fetch_items(subreddits),
        output_max_age_hours=OUTPUT_MAX_AGE_HOURS,
    )


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_REDDIT", file=sys.stderr)
