#!/usr/bin/env bash
set -euo pipefail
exec python3 "__RUNTIME_ROOT__/scripts/newsletter_doctor.py" --alias-mode status
