Normalize one human-written newsletter schedule into a strict machine-readable shape.

Return JSON only. No markdown fences. No commentary.

Allowed output shapes:
- Interval:
  {
    "mode": "interval",
    "expression": "30m|1h|2h|6h|12h|24h|1d",
    "label": "human-readable label"
  }
- Cron:
  {
    "cron": "5-field cron expression",
    "label": "human-readable label"
  }

Rules:
- Prefer interval form when the user's request is clearly recurring by a fixed interval.
- Use cron only when the user specifies a particular time or a schedule that cannot be represented cleanly as an interval.
- Keep the label concise and human-readable in the user's language.
- Do not invent a schedule if the input is ambiguous. Pick the most conservative, clearly implied meaning.
- Use only valid 5-field cron expressions.
