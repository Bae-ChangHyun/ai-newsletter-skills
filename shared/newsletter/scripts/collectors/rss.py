#!/usr/bin/env python3
"""Generic RSS collector — fetches from multiple configurable RSS feeds."""

import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_rss, run_collector, format_output, load_runtime_config

DEFAULT_RSS_FEEDS = [
    # AI Lab blogs
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/"},
    {"name": "HuggingFace Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "Meta Engineering (AI)", "url": "https://engineering.fb.com/category/ml-applications/feed/"},
    # Big Tech research
    {"name": "Microsoft Research", "url": "https://www.microsoft.com/en-us/research/feed/"},
    {"name": "Apple ML", "url": "https://machinelearning.apple.com/rss.xml"},
    {"name": "Amazon Science", "url": "https://www.amazon.science/index.rss"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/"},
    # Communities & aggregators
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=30"},
    {"name": "GeekNews", "url": "https://feeds.feedburner.com/geeknews-feed"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/feed"},
    {"name": "TLDR AI", "url": "https://bullrich.dev/tldr-rss/ai.rss"},
    # Dev tools & blogs
    {"name": "LangChain Blog", "url": "https://blog.langchain.com/rss/"},
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/"},
]

MAX_WORKERS = 6


def _parse_items_from_tree(tree, feed_name):
    """Parse RSS/Atom items from an ElementTree."""
    items = []
    if tree is None:
        return items

    # Try RSS <item> elements first, then Atom <entry>
    entries = tree.findall(".//{http://www.w3.org/2005/Atom}entry")
    rss_items = tree.findall(".//item")

    for item in rss_items:
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        desc_el = item.find("description")
        guid_el = item.find("guid")

        title = (title_el.text or "").strip() if title_el is not None else ""
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
            "source": feed_name,
            "time": ts,
            "score": 0,
            "description": desc,
        })

    # Atom feeds
    for entry in entries:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        updated_el = entry.find("atom:updated", ns)
        published_el = entry.find("atom:published", ns)
        summary_el = entry.find("atom:summary", ns)
        content_el = entry.find("atom:content", ns)

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = ""
        if link_el is not None:
            link = (link_el.get("href") or "").strip()
        desc = ""
        if summary_el is not None and summary_el.text:
            desc = summary_el.text.strip()
        elif content_el is not None and content_el.text:
            desc = content_el.text.strip()[:500]

        ts = 0
        date_el = published_el if published_el is not None else updated_el
        if date_el is not None and date_el.text:
            try:
                from datetime import datetime as _dt
                text = date_el.text.strip()
                # ISO 8601 format
                if text.endswith("Z"):
                    text = text[:-1] + "+00:00"
                dt = _dt.fromisoformat(text)
                ts = dt.timestamp()
            except Exception:
                try:
                    dt = parsedate_to_datetime(date_el.text)
                    ts = dt.timestamp()
                except Exception:
                    pass

        if not link or not title:
            continue

        items.append({
            "title": title,
            "url": link,
            "source": feed_name,
            "time": ts,
            "score": 0,
            "description": desc,
        })

    return items


def _fetch_single_feed(feed):
    """Fetch and parse a single RSS feed."""
    name = feed.get("name", "RSS")
    url = feed.get("url", "")
    if not url:
        return []
    tree = fetch_rss(url, user_agent="ai-newsletter-rss/1.0", timeout=20)
    return _parse_items_from_tree(tree, name)


def fetch_items(feeds=None):
    """Fetch items from all configured RSS feeds in parallel."""
    if feeds is None:
        feeds = DEFAULT_RSS_FEEDS

    all_items = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_single_feed, feed): feed
            for feed in feeds
        }
        for future in as_completed(futures):
            feed = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
                print(
                    f"RSS_FEED name={feed.get('name', '?')} items={len(items)}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"RSS_FEED name={feed.get('name', '?')} error={e}",
                    file=sys.stderr,
                )
    return all_items


def collect(feeds=None):
    if feeds is None:
        config = load_runtime_config()
        feeds = config.get("rss_feeds", DEFAULT_RSS_FEEDS)
    return run_collector("rss", lambda: fetch_items(feeds))


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_RSS", file=sys.stderr)
