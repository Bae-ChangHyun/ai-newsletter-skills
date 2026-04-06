#!/usr/bin/env python3
"""Velopers collector — fetches from velopers.kr RSS."""

import sys
import os
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_rss, run_collector, format_output

def fetch_items():
    items = []
    tree = fetch_rss("https://www.velopers.kr/rss.xml", user_agent="openclaw-velopers/1.0")
    if not tree:
        return items

    for item in tree.findall(".//item"):
        title = (item.find("title").text or "").strip()
        link = (item.find("link").text or "").strip()
        pub = item.find("pubDate")
        pub_text = pub.text if pub is not None else ""
        ts = 0
        if pub_text:
            try:
                dt = parsedate_to_datetime(pub_text)
                ts = dt.timestamp()
            except Exception:
                pass
        if not link:
            continue
        items.append({
            "title": title,
            "url": link,
            "source": "Velopers",
            "time": ts,
            "score": 0,
        })
    return items


def collect():
    return run_collector("velopers", fetch_items)


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_VELOPERS", file=sys.stderr)
