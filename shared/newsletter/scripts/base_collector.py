#!/usr/bin/env python3
"""Base collector — shared logic for all newsletter platform collectors."""

import functools
import json
import os
import sys
import time
from datetime import timezone, timedelta, datetime

KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30

DEFAULT_AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "anthropic", "openai", "gemini", "mistral",
    "llama", "qwen", "deepseek", "copilot", "chatgpt", "transformer", "diffusion",
    "stable diffusion", "midjourney", "dall-e", "sora", "neural", "machine learning",
    "deep learning", "langchain", "llamaindex", "hugging face", "huggingface",
    "nvidia", "cuda", "gpu", "rag", "vector", "embedding", "fine-tune", "finetune",
    "lora", "qlora", "quantiz", "gguf", "ggml", "ollama", "vllm", "mlx",
    "agent", "mcp", "tool use", "function calling", "reasoning", "chain of thought",
    "benchmark", "eval", "arxiv", "paper", "model", "inference", "training",
    "open source", "opensource", "open-source", "foundation model", "multimodal",
    "vision", "speech", "tts", "stt", "whisper", "grok", "xai", "cohere",
    "meta ai", "gemma", "phi", "openclaw", "cursor", "windsurf", "aider",
    "coding agent", "code generation", "robotics", "autonomous", "self-driving",
]

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


def get_ai_keywords():
    config = load_runtime_config()
    extra_keywords = config.get("ai_keywords", [])
    merged = []
    for keyword in DEFAULT_AI_KEYWORDS + extra_keywords:
        normalized = keyword.strip().lower()
        if normalized and normalized not in merged:
            merged.append(normalized)
    return merged


def is_ai_related(title, url=""):
    text = (title + " " + url).lower()
    return any(kw in text for kw in get_ai_keywords())


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
                    seen[entry["url"]] = entry
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
    return item["url"] not in seen


def is_pending(entry):
    return not entry.get("sent", True)


def merge_entry(existing, item):
    merged = dict(existing) if existing else {}
    merged.update(item)
    if existing:
        merged["sent"] = existing.get("sent", True)
        if "first_seen_at" in existing:
            merged["first_seen_at"] = existing["first_seen_at"]
    else:
        merged["sent"] = False
        merged["first_seen_at"] = time.time()
    return merged


def mark_delivered(platform, urls):
    seen_file = get_seen_file(platform)
    seen = load_seen(seen_file)
    delivered_at = time.time()
    changed = 0

    for url in urls:
        entry = seen.get(url)
        if not entry:
            continue
        if not entry.get("sent", False):
            changed += 1
        entry["sent"] = True
        entry["delivered_at"] = delivered_at

    save_seen(seen_file, seen)
    return changed


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
    pending_items = []
    new_count = 0

    items = fetch_fn()
    for item in items:
        url = item["url"]
        existing = seen.get(url)
        merged = merge_entry(existing, item)
        seen[url] = merged
        if existing is None:
            new_count += 1
        if is_pending(merged):
            pending_items.append(merged)

    save_seen(seen_file, seen)

    if output_max_age_hours is not None:
        output_cutoff = time.time() - output_max_age_hours * 3600
        output_items = [i for i in pending_items if i.get("time", 0) > output_cutoff]
    elif max_new_items is not None:
        output_items = pending_items[:max_new_items]
    else:
        output_items = pending_items

    pending_count = sum(1 for entry in seen.values() if is_pending(entry))
    print(
        f"# Seen: {len(seen)} total, {new_count} new, {pending_count} pending, {len(output_items)} output",
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
        print(f"# WARN: fetch failed {url}: {e}", file=sys.stderr)
        return None


def fetch_html(url, user_agent="Mozilla/5.0", timeout=10):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"# WARN: fetch failed {url}: {e}", file=sys.stderr)
        return None


def fetch_rss(url, user_agent="openclaw/1.0", timeout=15):
    import urllib.request
    import xml.etree.ElementTree as ET
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return ET.parse(resp)
    except Exception as e:
        print(f"# WARN: RSS fetch failed {url}: {e}", file=sys.stderr)
        return None
