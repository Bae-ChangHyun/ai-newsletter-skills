#!/usr/bin/env python3
"""TLDR AI collector — fetches from tldr.tech RSS."""

import sys
import os
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_rss, run_collector, format_output

RSS_URL = "https://bullrich.dev/tldr-rss/ai.rss"


def fetch_items():
    items = []
    tree = fetch_rss(RSS_URL, user_agent="openclaw-tldr/1.0")
    if not tree:
        return items

    for item in tree.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        desc_el = item.find("description")

        title = (title_el.text or "").strip() if title_el is not None else ""
        guid_el = item.find("guid")
        link = (link_el.text or "").strip() if link_el is not None else ""
        if not link:
            link = (guid_el.text or "").strip() if guid_el is not None else ""
        desc = (desc_el.text or "").strip() if desc_el is not None else ""

        ts = 0
        if pub_el is not None and pub_el.text:
            try:
                dt = parsedate_to_datetime(pub_el.text)
                ts = dt.timestamp()
            except Exception:
                pass

        if not link or not title:
            continue
        if "(sponsor)" in title.lower():
            continue

        items.append({
            "title": title,
            "url": link,
            "source": "TLDR",
            "time": ts,
            "score": 0,
            "description": desc,
        })
    return items


def collect():
    return run_collector("tldr", fetch_items)


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_TLDR", file=sys.stderr)
