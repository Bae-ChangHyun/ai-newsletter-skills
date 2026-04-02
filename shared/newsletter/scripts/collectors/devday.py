#!/usr/bin/env python3
"""DevDay collector — scrapes devday.kr/space/ai-data."""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_html, run_collector, format_output


def fetch_items():
    items = []
    html = fetch_html("https://devday.kr/space/ai-data")
    if not html:
        return items

    blocks = re.findall(
        r'href=["\'](/article/([^"\']+))["\'].*?<[^>]*class=["\'][^"\']*title[^"\']*["\'][^>]*>([^<]+)<',
        html,
        re.DOTALL,
    )
    if blocks:
        seen_slugs = set()
        for path, slug, title in blocks:
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            items.append({
                "title": title.strip(),
                "url": f"https://devday.kr{path}",
                "source": "DevDay",
                "time": 0,
                "score": 0,
            })
    else:
        articles = re.findall(r'href=["\'](/article/[^"\']+)["\']', html)
        seen_slugs = set()
        for path in articles:
            slug = path.split("/article/")[-1]
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            title = slug.replace("-", " ").title()
            items.append({
                "title": title,
                "url": f"https://devday.kr{path}",
                "source": "DevDay",
                "time": 0,
                "score": 0,
            })
    return items


def collect():
    return run_collector("devday", fetch_items)


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_DEVDAY", file=sys.stderr)
