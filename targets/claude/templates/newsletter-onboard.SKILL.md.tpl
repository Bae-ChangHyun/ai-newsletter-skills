---
name: newsletter-onboard
description: "AI 뉴스레터 초기 설정. 플랫폼, Telegram, 수집 주기를 설정한다. 사용자가 onboarding, 설정 변경, 텔레그램 연동, 주기 변경을 원하면 이 스킬을 사용한다."
allowedTools:
  - "Bash(python3 *)"
  - "Bash(cat *)"
  - "Read"
---

# Newsletter Onboard

실제 설정은 공용 `onboard.py`가 처리한다.

```bash
python3 __RUNTIME_ROOT__/scripts/onboard.py
```

설정 파일은 `__RUNTIME_ROOT__/.data/config.json`에 저장된다.
