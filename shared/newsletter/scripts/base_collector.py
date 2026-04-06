#!/usr/bin/env python3
"""Base collector — shared logic for all newsletter platform collectors."""

import functools
import json
import os
import re
import sys
import time
from datetime import timezone, timedelta, datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30
STATE_INGESTED = "ingested"
STATE_CURATED = "curated"
STATE_SEND_FAILED = "send_failed"
STATE_SENT = "sent"
ACTIVE_STATES = {STATE_INGESTED, STATE_CURATED, STATE_SEND_FAILED}
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "mkt_tok",
    "ref",
    "ref_src",
    "spm",
}

INTERVAL_RE = re.compile(r"^\s*(\d+)\s*([mhd])\s*$")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", ".data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


@functools.lru_cache(maxsize=1)
def load_runtime_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_schedule_window_hours(default_hours=None, grace_minutes=15):
    config = load_runtime_config()
    schedule = config.get("schedule") or {}
    if schedule.get("cron"):
        return None
    if schedule.get("mode") != "interval":
        return default_hours

    expression = (schedule.get("expression") or "").strip().lower()
    match = INTERVAL_RE.match(expression)
    if not match:
        return default_hours

    value = int(match.group(1))
    unit = match.group(2)
    if unit == "m":
        base_hours = value / 60
    elif unit == "h":
        base_hours = value
    elif unit == "d":
        base_hours = value * 24
    else:
        return default_hours

    return base_hours + (grace_minutes / 60)


def canonicalize_url(url):
    if not url:
        return ""
    parts = urlsplit(url.strip())
    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    kept_query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        normalized_key = key.lower()
        if normalized_key.startswith("utm_") or normalized_key in TRACKING_QUERY_KEYS:
            continue
        kept_query.append((key, value))
    query = urlencode(kept_query, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def normalize_title(title):
    normalized = re.sub(r"[^\w\s]", " ", (title or "").lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def get_entry_state(entry):
    state = entry.get("state")
    if state:
        return state
    if entry.get("sent", False):
        return STATE_SENT
    return STATE_INGESTED


def get_seen_file(platform):
    return os.path.join(DATA_DIR, f"{platform}_seen.jsonl")


def load_seen(seen_file):
    seen = {}
    try:
        with open(seen_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    canonical_url = canonicalize_url(entry.get("url", ""))
                    entry["canonical_url"] = canonical_url
                    entry["normalized_title"] = normalize_title(entry.get("title", ""))
                    entry["state"] = get_entry_state(entry)
                    entry["sent"] = entry["state"] == STATE_SENT
                    if canonical_url:
                        seen[canonical_url] = entry
    except FileNotFoundError:
        pass
    return seen


def save_seen(seen_file, seen, max_age_days=MAX_AGE_DAYS):
    cutoff = time.time() - max_age_days * 86400
    os.makedirs(os.path.dirname(seen_file), exist_ok=True)
    with open(seen_file, "w", encoding="utf-8") as f:
        for entry in seen.values():
            if entry.get("time", 0) > cutoff or entry.get("time", 0) == 0:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def is_new(item, seen):
    return canonicalize_url(item["url"]) not in seen


def is_pending(entry):
    return get_entry_state(entry) in ACTIVE_STATES


def merge_entry(existing, item):
    merged = dict(existing) if existing else {}
    merged.update(item)
    merged["canonical_url"] = canonicalize_url(item.get("url", merged.get("url", "")))
    merged["normalized_title"] = normalize_title(item.get("title", merged.get("title", "")))
    if existing:
        merged["state"] = get_entry_state(existing)
        if "first_seen_at" in existing:
            merged["first_seen_at"] = existing["first_seen_at"]
    else:
        merged["state"] = STATE_INGESTED
        merged["first_seen_at"] = time.time()
    merged["sent"] = merged["state"] == STATE_SENT
    return merged


def mark_state(platform, urls, state):
    seen_file = get_seen_file(platform)
    seen = load_seen(seen_file)
    updated_at = time.time()
    changed = 0
    target_urls = {canonicalize_url(url) for url in urls if url}

    for url, entry in seen.items():
        if canonicalize_url(url) not in target_urls and entry.get("canonical_url") not in target_urls:
            continue
        previous_state = get_entry_state(entry)
        if previous_state != state:
            changed += 1
        entry["state"] = state
        entry["sent"] = state == STATE_SENT
        if state == STATE_CURATED:
            entry["curated_at"] = updated_at
        elif state == STATE_SEND_FAILED:
            entry["send_failed_at"] = updated_at
        elif state == STATE_SENT:
            entry["delivered_at"] = updated_at

    save_seen(seen_file, seen)
    return changed


def mark_curated(platform, urls):
    return mark_state(platform, urls, STATE_CURATED)


def mark_send_failed(platform, urls):
    return mark_state(platform, urls, STATE_SEND_FAILED)


def mark_delivered(platform, urls):
    return mark_state(platform, urls, STATE_SENT)


def format_output(items, header=None):
    if not items:
        return ""
    lines = []
    if header:
        lines.append(header)
    for i, item in enumerate(items, 1):
        ts = ""
        if item.get("time"):
            dt = datetime.fromtimestamp(item["time"], KST)
            ts = dt.strftime("%y%m%d.%H:%M")
        source = item.get("source", "")
        score = item.get("score", 0)
        meta_parts = []
        if ts:
            meta_parts.append(ts)
        if source:
            if score:
                meta_parts.append(f"{source}|{score}pt")
            else:
                meta_parts.append(source)
        meta = " ".join(f"[{p}]" for p in meta_parts) if meta_parts else ""
        line = f"{i}. [{item['title']}]({item['url']})"
        if meta:
            line += f" - {meta}"
        lines.append(line)
    return "\n".join(lines)


def run_collector(platform, fetch_fn, output_max_age_hours=None, max_new_items=None):
    seen_file = get_seen_file(platform)
    seen = load_seen(seen_file)
    new_count = 0

    items = fetch_fn()
    for item in items:
        url = canonicalize_url(item["url"])
        existing = seen.get(url)
        merged = merge_entry(existing, item)
        seen[url] = merged
        if existing is None:
            new_count += 1

    save_seen(seen_file, seen)

    retry_items = []
    fresh_items = []
    for entry in seen.values():
        state = get_entry_state(entry)
        if state == STATE_SENT:
            continue
        if state in {STATE_CURATED, STATE_SEND_FAILED}:
            retry_items.append(entry)
        elif state == STATE_INGESTED:
            fresh_items.append(entry)

    resolved_output_max_age_hours = get_schedule_window_hours(output_max_age_hours)

    if resolved_output_max_age_hours is not None:
        output_cutoff = time.time() - resolved_output_max_age_hours * 3600
        fresh_items = [
            i for i in fresh_items
            if i.get("time", 0) == 0 or i.get("time", 0) > output_cutoff
        ]
    elif max_new_items is not None:
        fresh_items = fresh_items[:max_new_items]

    state_priority = {
        STATE_SEND_FAILED: 0,
        STATE_CURATED: 1,
        STATE_INGESTED: 2,
        STATE_SENT: 3,
    }

    def sort_key(entry):
        return (
            state_priority.get(get_entry_state(entry), 9),
            -(entry.get("score", 0) or 0),
            -(entry.get("time", 0) or 0),
            entry.get("title", ""),
        )

    output_items = sorted(retry_items, key=sort_key) + sorted(fresh_items, key=sort_key)

    pending_count = sum(1 for entry in seen.values() if is_pending(entry))
    state_counts = {
        state: sum(1 for entry in seen.values() if get_entry_state(entry) == state)
        for state in [STATE_INGESTED, STATE_CURATED, STATE_SEND_FAILED, STATE_SENT]
    }
    print(
        "COLLECT_STATE "
        f"platform={platform} "
        f"seen_total={len(seen)} "
        f"new={new_count} "
        f"pending={pending_count} "
        f"output={len(output_items)} "
        f"ingested={state_counts[STATE_INGESTED]} "
        f"curated={state_counts[STATE_CURATED]} "
        f"send_failed={state_counts[STATE_SEND_FAILED]} "
        f"sent={state_counts[STATE_SENT]}",
        file=sys.stderr,
    )
    return output_items


def fetch_json(url, user_agent="openclaw/1.0", timeout=10):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"WARN fetch_json url={url} error={e}", file=sys.stderr)
        return None


def fetch_html(url, user_agent="Mozilla/5.0", timeout=10):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"WARN fetch_html url={url} error={e}", file=sys.stderr)
        return None


def fetch_rss(url, user_agent="openclaw/1.0", timeout=15):
    import urllib.request
    import xml.etree.ElementTree as ET
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return ET.parse(resp)
    except Exception as e:
        print(f"WARN fetch_rss url={url} error={e}", file=sys.stderr)
        return None
