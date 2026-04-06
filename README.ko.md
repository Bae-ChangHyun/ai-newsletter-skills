<div align="center">

# AI Newsletter Skills

**큐레이팅된 AI 뉴스를, 원하는 AI 에이전트로, 자동으로 받아보세요.**

지원되는 7개 소스에서 수집. AI로 노이즈 제거. 텔레그램 전달 또는 로컬 미리보기 — 모두 CLI 하나로.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Bae-ChangHyun/ai-newsletter-skills?style=flat-square&color=f9c74f)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/stargazers)
[![Issues](https://img.shields.io/github/issues/Bae-ChangHyun/ai-newsletter-skills?style=flat-square&color=ef476f)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/issues)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/code)
[![Codex](https://img.shields.io/badge/Codex-111827?style=flat-square&logo=openai&logoColor=white)](https://openai.com/codex)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-0F172A?style=flat-square&logo=githubcopilot&logoColor=white)](https://github.com/features/copilot)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI%20Compatible-2563EB?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/)

[English](./README.md)

</div>

---

## 목차

- [이 프로젝트를 만든 이유](#-이-프로젝트를-만든-이유)
- [작동 방식](#-작동-방식)
- [주요 기능](#-주요-기능)
- [빠른 시작](#-빠른-시작)
- [명령어](#-명령어)
- [온보딩 Wizard](#-온보딩-wizard)
- [AI 엔진](#-ai-엔진)
- [뉴스 소스](#-뉴스-소스)
- [라이선스](#-라이선스)

---

## 이 프로젝트를 만든 이유

AI 트렌드를 따라가는 것 자체가 풀타임 작업입니다.

매일 새로운 논문, 도구, GitHub 저장소, 커뮤니티 글이 Hacker News, Reddit, Threads, 그리고 수많은 포럼에 쏟아집니다. 이걸 전부 직접 확인하기엔 대부분의 개발자에게 시간이 부족합니다.

**AI Newsletter Skills는 이 전체 파이프라인을 자동화합니다:**

- 지원되는 7개 소스에서 스케줄에 맞춰 수집
- 선호하는 AI 엔진으로 노이즈를 걸러내고 중요한 것만 요약
- 깔끔한 다이제스트를 텔레그램 또는 터미널로 전달 — 외부 서비스 없음, 구독 없음

---

## 작동 방식

```
┌─────────────────────────────────────────────────────────────┐
│                      뉴스 소스 (7개)                         │
│  Hacker News · Reddit · Threads · GeekNews                  │
│  DevDay · TLDR · Velopers                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │  수집
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    수집기 (Python)                           │
│       Fetch → 중복 제거 → 정규화                              │
└──────────────────────┬──────────────────────────────────────┘
                       │  원본 항목
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI 엔진 (선택 가능)                          │
│   Claude Code  │  Codex  │  GitHub Copilot  │  OpenAI API   │
│   노이즈 필터 · 관련성 점수화 · 다이제스트 작성                  │
└──────────────────────┬──────────────────────────────────────┘
                       │  큐레이팅된 다이제스트
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram 전달                             │
│         Bot API → 설정한 채팅 또는 그룹 채널                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 주요 기능

- **한 줄 설치** — `curl | python3` 한 줄이면 모든 준비 완료
- **대화형 온보딩 wizard** — 실시간 검증과 재실행 가능한 설정을 갖춘 안내형 셋업
- **4개 AI 엔진** — Claude Code, Codex, GitHub Copilot, 그리고 모든 OpenAI-compatible 엔드포인트
- **지원되는 7개 뉴스 소스** — Hacker News, Reddit, Threads (RSSHub 경유), GeekNews, DevDay, TLDR, Velopers
- **Telegram 전달** — 온보딩 중 봇 토큰 검증 및 채팅 ID 확인
- **터미널 미리보기 모드** — 원하면 Telegram 없이 로컬 출력으로 실행 가능
- **RSSHub 연동** — 헬스 체크된 Threads 수집과 우아한 fallback
- **cron 기반 스케줄링** — 명령어 하나로 반복 실행 등록 및 제거
- **설정 보존** — 온보딩을 다시 실행하면 이전 값을 기본값으로 불러옴
- **6개 핵심 셸 명령어** — 각 작업에 하나씩: onboard, doctor, history, now, start, stop

---

## 빠른 시작

**필수 조건**

- `python3`
- `node` 와 `npm`
- `crontab` / cron
- 사용할 AI 백엔드 하나 (`codex`, `claude`, GitHub Copilot, 또는 OpenAI-compatible API key)

**1단계 — 설치**

```bash
curl -fsSL https://raw.githubusercontent.com/Bae-ChangHyun/ai-newsletter-skills/main/install.py | python3 -
```

**2단계 — Wizard 실행**

```bash
newsletter-onboard
```

> `newsletter-onboard`가 `PATH`에 없다면:
> ```bash
> ~/.ai-newsletter/bin/newsletter-onboard
> ```

**3단계 — 확인 및 실행**

```bash
newsletter-doctor   # 설정, 백엔드 상태, cron 상태를 함께 진단
newsletter-history  # 최근 발송 기사와 요약 확인
newsletter-now      # 다이제스트 즉시 1회 전송
newsletter-start    # 반복 cron 스케줄 활성화
```

끝입니다. 설정한 스케줄에 따라 텔레그램으로 큐레이팅된 AI 뉴스가 도착하고, 터미널 전용 모드를 선택했다면 `newsletter-now`가 로컬에 다이제스트를 출력합니다.

---

## 명령어

| 명령어 | 설명 |
| --- | --- |
| `newsletter-onboard` | 안내형 설정 wizard를 실행하고 선택한 AI 엔진 연동을 설치 |
| `newsletter-doctor` | 설정, 현재 백엔드 진단, 전달 모드, 최근 요약, 활성 cron 줄을 표시 |
| `newsletter-history` | 최근 발송 요약과 최근에 전달된 뉴스 항목을 표시 |
| `newsletter-now` | 설정된 AI 엔진으로 뉴스레터 사이클 1회 즉시 실행 |
| `newsletter-start` | 설정된 AI 엔진용 반복 cron 엔트리 1줄 등록 |
| `newsletter-stop` | 뉴스레터 cron 엔트리 제거 |

> `newsletter-status`는 호환성 alias로 남아 있으며 이제 `newsletter-doctor`를 호출합니다.

### 백엔드 스모크 테스트

고정된 수집 데이터는 재사용하고, 실제 AI 백엔드 편집/메시지 구성은 그대로 실행하려면:

```bash
python3 scripts/smoke_backends.py --backend all --mode terminal --skip-missing
```

- 라이브 수집 대신 fixture `.jsonl` 데이터를 사용
- 선택/요약/메시지 구성은 실제 AI 백엔드가 수행
- fixture 수를 작게 유지해서 실행 시간을 줄임
- 필요한 로컬 인증/환경변수가 없으면 해당 백엔드는 자동 skip
- 보통 Codex/Claude 사용자는 로컬 CLI 로그인만 되어 있으면 바로 smoke 가능
- GitHub Copilot은 한 번 onboarding/login을 끝내 둬야 함
- OpenAI는 `SMOKE_OPENAI_BASE_URL`, `SMOKE_OPENAI_MODEL`, API key env가 필요
- 최종 실전 확인은 `--mode telegram` 으로 가능
- 자세한 내용은 `docs/testing.md` 참고

cron 등록/실행/제거까지 확인하는 스모크 테스트:

```bash
python3 scripts/smoke_cron.py --backend all --skip-missing --timeout 150
```

---

## 온보딩 Wizard

`newsletter-onboard`는 모든 설정을 대화형으로 안내합니다:

| 프롬프트 | 설정 항목 |
| --- | --- |
| Language | 다이제스트 출력 언어 |
| AI Engine | 편집 단계를 실행할 AI 에이전트 |
| Sources | 수집할 플랫폼 |
| Subreddits | 모니터링할 Reddit 커뮤니티 |
| 전달 방식 | Telegram 전달 또는 터미널 전용 미리보기 |
| Telegram bot token | 전달 엔드포인트 (`getMe`로 실시간 검증) |
| Telegram chat ID | 대상 채팅 또는 그룹 |
| RSSHub URL | Threads 수집용 base URL |
| Threads handles | RSSHub로 팔로우할 계정 |
| Schedule | `1h`, `30m`, 5필드 cron 또는 `1시간마다` 같은 자연어 |

`newsletter-onboard`를 다시 실행하면 기존 `config.json` 값을 기본값으로 불러옵니다 — 직접 변경하지 않는 한 아무것도 사라지지 않습니다.

<details>
<summary><strong>Telegram 설정 상세</strong></summary>

온보딩 중에:

- 봇 토큰을 Telegram `getMe` API로 확인합니다
- 선택한 채팅으로 인증 코드를 전송합니다
- 입력한 코드가 일치해야 다음 단계로 넘어갑니다

팁:

- Telegram에서 `@BotFather`로 봇 생성
- `@get_id_bot` 같은 헬퍼로 대상 채팅 ID 확인

</details>

<details>
<summary><strong>RSSHub / Threads 설정 상세</strong></summary>

온보딩 중에:

- RSSHub를 `/healthz`, 이어서 base URL로 헬스 체크합니다
- Threads handle을 실제 RSSHub feed로 검증합니다
- RSSHub가 응답하지 않으면 재시도하거나 Threads 수집을 비활성화하고 계속할 수 있습니다

기본 RSSHub URL:

```
http://localhost:1200
```

Docker로 RSSHub 로컬 실행:

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

</details>

---

## AI 엔진

<details>
<summary><strong>Claude Code</strong></summary>

- `claude` CLI가 설치되어 있고 인증된 상태여야 합니다
- 헤드리스 실행을 위해 `claude -p ... --dangerously-skip-permissions`를 사용합니다
- 온보딩 중 Claude용 newsletter skill 템플릿을 자동 설치합니다

</details>

<details>
<summary><strong>Codex</strong></summary>

- `codex` CLI가 설치되어 있고 인증된 상태여야 합니다
- `codex exec --dangerously-bypass-approvals-and-sandbox`를 사용합니다
- 온보딩 중 Codex용 skill 템플릿을 자동 설치합니다

</details>

<details>
<summary><strong>GitHub Copilot</strong></summary>

- 온보딩 중 공식 GitHub device-login OAuth 흐름을 사용합니다
- 브라우저 인증 페이지를 열고 승인을 기다립니다
- 선택한 Copilot 모델로 config 생성 및 편집 실행을 처리합니다

</details>

<details>
<summary><strong>OpenAI-compatible</strong></summary>

- 온보딩 중 `base_url`, `model`, `api_key_env`를 입력합니다
- 표준 `/chat/completions` 엔드포인트를 호출합니다
- OpenAI API 호환 프로바이더라면 어디든 사용 가능 (Groq, Together, 로컬 Ollama 등)

</details>

---

## 뉴스 소스

| 소스 | 수집 범위 |
| --- | --- |
| Hacker News | AI 및 기술 분야 상위 게시글 |
| Reddit | 설정 가능한 subreddit (예: r/MachineLearning, r/LocalLLaMA) |
| Threads | RSSHub feed를 통한 계정 수집 |
| GeekNews | 한국 기술 커뮤니티 게시글 |
| DevDay | 개발자 중심 AI 발표 소식 |
| TLDR | 큐레이팅된 기술 뉴스레터 |
| Velopers | 한국 개발자 커뮤니티 |

---

## 라이선스

[MIT License](LICENSE)로 배포됩니다.

---

<div align="center">

[Bae-ChangHyun](https://github.com/Bae-ChangHyun)과 기여자들이 만들었습니다.

이 프로젝트가 시간을 아껴줬다면 스타를 눌러주세요.

[![GitHub Stars](https://img.shields.io/github/stars/Bae-ChangHyun/ai-newsletter-skills?style=social)](https://github.com/Bae-ChangHyun/ai-newsletter-skills/stargazers)

</div>
