#!/usr/bin/env python3
"""Run one collection cycle and emit timestamped operational logs."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_ALL = os.path.join(SCRIPT_DIR, "run_all.py")
KST = ZoneInfo("Asia/Seoul")


def log(message: str) -> None:
    timestamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{timestamp}] {message}")


def main() -> int:
    log("RUN start mode=collect-only")
    result = subprocess.run(
        ["python3", RUN_ALL, "--collect-only"],
        text=True,
        capture_output=True,
        check=False,
    )
    for stream in (result.stderr, result.stdout):
        for line in (stream or "").splitlines():
            line = line.strip()
            if line:
                log(line)
    if result.returncode != 0:
        log(f"RUN failed mode=collect-only exit={result.returncode}")
        return result.returncode
    log("RUN success mode=collect-only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
