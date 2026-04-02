#!/usr/bin/env python3
"""GeekNews collector — scrapes news.hada.io."""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_html, run_collector, format_output


def fetch_items():
    items = []
    for page_url in ["https://news.hada.io/new", "https://news.hada.io/"]:
        html = fetch_html(page_url)
        if not html:
            continue

        pattern = r"<a\s+href='([^']+)'[^>]*><h1>([^<]+)</h1></a>\s*<span class=topicurl>\(([^)]+)\)</span></div><div class='topicdesc'><a href='topic\?id=(\w+)'"
        matches = re.findall(pattern, html)
        scores = {tid: int(s) for tid, s in re.findall(r"id='tp(\w+)'>(\d+)</span>", html)}

        for ext_url, title, domain, tid in matches:
            score = scores.get(tid, 0)
            items.append({
                "title": title.strip(),
                "url": ext_url,
                "source": "GeekNews",
                "time": 0,
                "score": score,
            })

    seen_titles = set()
    deduped = []
    for it in items:
        if it["title"] not in seen_titles:
            seen_titles.add(it["title"])
            deduped.append(it)
    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    return deduped


def collect():
    return run_collector("geeknews", fetch_items)


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_GEEKNEWS", file=sys.stderr)
