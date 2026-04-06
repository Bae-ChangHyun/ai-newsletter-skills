---
name: newsletter-status
description: "newsletter-doctor 호환성 alias."
allowedTools:
  - "Bash(cat *)"
  - "Bash(python3 *)"
---

# Newsletter Status

이 호환성 alias는 `newsletter-doctor`를 호출한다.

```bash
python3 __RUNTIME_ROOT__/scripts/newsletter_doctor.py --alias-mode status
```

`config.language`가 있으면 그 언어로 답한다.
