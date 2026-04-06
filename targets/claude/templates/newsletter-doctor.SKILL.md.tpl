---
name: newsletter-doctor
description: "설정된 백엔드와 스케줄에 대한 뉴스레터 진단을 실행한다."
allowedTools:
  - "Bash(python3 *)"
  - "Bash(cat *)"
---

# Newsletter Doctor

## 실행

```bash
python3 __RUNTIME_ROOT__/scripts/newsletter_doctor.py
```

응답은 가능하면 `config.language`를 따르고, 현재 백엔드에 필요한 항목만 진단한다.
