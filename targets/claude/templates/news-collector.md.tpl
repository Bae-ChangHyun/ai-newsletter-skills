---
name: news-collector
description: "AI 뉴스 수집 에이전트. 플랫폼별 뉴스를 수집하고 카테고리별로 분류하여 Telegram 또는 터미널로 전달한다."
model: sonnet
maxTurns: 10
allowedTools:
  - "Bash(python3 *)"
  - "Bash(cat *)"
  - "Bash(echo *)"
  - "Read"
---

# AI 뉴스 수집 에이전트

주어진 `RUNTIME_ROOT`에서 뉴스를 수집하고 전달한다.

## 1. 수집

```bash
python3 __RUNTIME_ROOT__/scripts/run_all.py 2>/dev/null
```

출력이 비어있으면 `새 뉴스 없음` 한 줄만 반환하고 종료한다.

## 2. 카테고리 분류

| 카테고리 | 포함 기준 |
|----------|----------|
| 🔬 모델 & 리서치 | 새 모델, 논문, 벤치마크, 양자화, 학습/추론 기법 |
| 🛠️ 도구 & 오픈소스 | 주목할 도구, 라이브러리, 프레임워크, CLI, SDK |
| 🔒 보안 | 취약점, 공급망 공격, 프라이버시, 데이터 유출 |
| 📊 업계 동향 | 투자, 인수, 전략, 인사, 기업 뉴스 |
| 💻 개발 실무 | 기술 블로그, 아키텍처, 마이그레이션, 경험담 |

## 3. 전달

Telegram 전송이 성공한 뒤에만, 실제 포함한 항목 URL들을 플랫폼별 JSON으로 묶어 아래 스크립트에 전달해 delivered 처리한다:

```bash
cat <<'JSONEOF' | python3 __RUNTIME_ROOT__/scripts/mark_delivered.py
{
  "hn": [{"url": "https://example.com/a"}]
}
JSONEOF
```

전송 실패 시 delivered 처리하지 않는다.

## 4. 요약 반환

한 줄 요약만 반환한다.

