#!/usr/bin/env python3
"""Mark newsletter items as send_failed after a delivery error."""

import json
import sys

from base_collector import mark_send_failed


def main():
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise SystemExit("Expected JSON object grouped by platform")

    total = 0
    for platform, entries in payload.items():
        urls = []
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, str):
                urls.append(entry)
            elif isinstance(entry, dict) and entry.get("url"):
                urls.append(entry["url"])
        total += mark_send_failed(platform, urls)

    print(f"OK {total}")


if __name__ == "__main__":
    main()
