#!/usr/bin/env python3
"""Threads post collector — polls RSSHub for new posts."""

import os
import sys
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_rss, run_collector, format_output

RSSHUB_BASE = os.environ.get("RSSHUB_URL", "http://localhost:1200")
OUTPUT_MAX_AGE_HOURS = 24


def fetch_items(accounts=None):
    if not accounts:
        print("# WARN: no threads accounts configured", file=sys.stderr)
        return []
    items = []
    for account in accounts:
        url = f"{RSSHUB_BASE}/threads/{account}"
        tree = fetch_rss(url, user_agent="openclaw-threads/1.0")
        if not tree:
            continue

        for item in tree.findall(".//item"):
            title = (item.find("title").text or "").strip()
            link = (item.find("link").text or "").strip()
            desc_el = item.find("description")
            desc = (desc_el.text or "").strip() if desc_el is not None else ""
            pub = item.find("pubDate")
            ts = 0
            if pub is not None and pub.text:
                try:
                    dt = parsedate_to_datetime(pub.text)
                    ts = dt.timestamp()
                except Exception:
                    pass
            if not link:
                continue
            items.append({
                "title": title,
                "url": link,
                "source": f"Threads/@{account}",
                "time": ts,
                "score": 0,
                "description": desc,
            })
    return items


def collect(accounts=None, rsshub_url=None):
    if rsshub_url:
        global RSSHUB_BASE
        RSSHUB_BASE = rsshub_url
    return run_collector(
        "threads",
        lambda: fetch_items(accounts),
        output_max_age_hours=OUTPUT_MAX_AGE_HOURS,
    )


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_THREADS", file=sys.stderr)
