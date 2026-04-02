#!/usr/bin/env python3
"""AI 뉴스레터 인터랙티브 설정 스크립트.

Usage:
    python3 onboard.py

config.json을 생성/업데이트한다.
"""

import json
import os
import re
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", ".data", "config.json")

PLATFORMS = [
    ("hn", "HN (Hacker News) — AI 관련 글 필터링"),
    ("reddit", "Reddit — AI 서브레딧"),
    ("geeknews", "GeekNews (news.hada.io)"),
    ("tldr", "TLDR — AI 뉴스레터 RSS"),
    ("threads", "Threads — AI 인플루언서 (RSSHub 필요)"),
    ("velopers", "Velopers (velopers.kr)"),
    ("devday", "DevDay (devday.kr)"),
]

DEFAULT_SUBREDDITS = [
    "Anthropic", "ArtificialInteligence", "ClaudeAI", "GithubCopilot",
    "LocalLLaMA", "ollama", "OpenAI", "openclaw", "opensource", "Qwen_AI", "Vllm",
]

DEFAULT_RSSHUB_URL = "http://localhost:1200"
CRON_FIELD_RE = re.compile(r"^[^\s]+(?:\s+[^\s]+){4}$")
INTERVAL_RE = re.compile(r"^\s*(\d+)\s*([mhdMHD])\s*$")


def load_existing():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def prompt_platforms(existing):
    current = existing.get("platforms", [p[0] for p in PLATFORMS])
    print("\n📡 수집할 플랫폼을 선택하세요 (번호, 콤마 구분)")
    print("   전체 선택: Enter\n")
    for i, (key, desc) in enumerate(PLATFORMS, 1):
        marker = "●" if key in current else "○"
        print(f"   {i}. {marker} {desc}")
    print()
    choice = input("   선택 (예: 1,2,3,5,6,7): ").strip()

    if not choice:
        return [p[0] for p in PLATFORMS]

    selected = []
    for c in choice.replace(" ", "").split(","):
        try:
            idx = int(c) - 1
            if 0 <= idx < len(PLATFORMS):
                selected.append(PLATFORMS[idx][0])
        except ValueError:
            pass
    return selected if selected else [p[0] for p in PLATFORMS]


def prompt_subreddits(existing):
    current = existing.get("subreddits", DEFAULT_SUBREDDITS)
    print(f"\n   Reddit 서브레딧 (현재: {', '.join(current)})")
    choice = input("   변경할 내용이 있으면 입력, 없으면 Enter: ").strip()
    if not choice:
        return current
    return [s.strip() for s in choice.split(",") if s.strip()]


def prompt_ai_keywords(existing):
    current = existing.get("ai_keywords", [])
    print("\n   AI 키워드 필터")
    print("   뉴스 필터링에 사용할 키워드를 콤마로 입력하세요.")
    print("   Enter만 치면 기본 내장 키워드를 사용합니다.")
    if current:
        print(f"   현재 설정: {', '.join(current)}")
    choice = input("   키워드 입력: ").strip()
    if not choice:
        return current
    return [k.strip().lower() for k in choice.split(",") if k.strip()]


def prompt_threads(existing):
    current_url = existing.get("rsshub_url", DEFAULT_RSSHUB_URL)
    print("\n   Threads는 RSSHub 서버가 필요합니다.")
    print(f"   기본값: {DEFAULT_RSSHUB_URL}")
    if current_url:
        print(f"   현재 설정: {current_url}")

    raw = input("   RSSHub URL (Enter면 기본값 사용): ").strip()
    url = raw or current_url or DEFAULT_RSSHUB_URL

    try:
        health_url = url.rstrip("/") + "/healthz"
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            if 200 <= resp.status < 400:
                print(f"   ✓ RSSHub 연결 확인: {health_url}")
                return url
    except Exception:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                if 200 <= resp.status < 400:
                    print(f"   ✓ RSSHub 연결 확인: {url}")
                    return url
        except Exception as e:
            print(f"   ⚠ RSSHub 연결 실패: {e}")

    print("   → Threads를 제외합니다.")
    print("   → RSSHub를 먼저 실행한 뒤 다시 onboard 하세요.")
    print("   → 예: docker run -d --name rsshub -p 1200:1200 diygod/rsshub")
    return ""


def prompt_threads_accounts(existing):
    current = existing.get("threads_accounts", [])
    print("\n   Threads 계정")
    print("   @ 없이 콤마로 구분해서 입력하세요.")
    print("   Enter면 현재값 유지, 현재값도 없으면 Threads를 제외합니다.")
    if current:
        print(f"   현재 설정: {', '.join(current)}")
    choice = input("   계정명 입력: ").strip()
    if not choice:
        return current

    accounts = []
    for handle in choice.replace("\n", ",").split(","):
        normalized = handle.lstrip("@").strip()
        if normalized and normalized not in accounts:
            accounts.append(normalized)
    return accounts


def prompt_telegram(existing):
    tg = existing.get("telegram", {})
    print("\n📱 Telegram 전송 설정")
    choice = input("   Telegram으로 뉴스를 전송할까요? (y/n, 기본: y): ").strip().lower()
    if choice == "n":
        return {"enabled": False}

    # bot token
    current_token = tg.get("bot_token", "")
    if current_token:
        masked = current_token[:8] + "..." + current_token[-4:]
        print(f"   현재 봇 토큰: {masked}")
        token = input("   새 토큰 입력 (유지하려면 Enter): ").strip()
        if not token:
            token = current_token
    else:
        token = input("   Telegram Bot 토큰 (@BotFather에서 발급): ").strip()
        if not token:
            print("   ⚠ 토큰 없이는 Telegram 전송 불가. 건너뜁니다.")
            return {"enabled": False}

    # chat_id 자동 조회
    current_chat_id = tg.get("chat_id", "")
    print("\n   chat_id를 자동 조회합니다...")
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("result"):
                chat_id = str(data["result"][-1]["message"]["chat"]["id"])
                print(f"   ✓ chat_id: {chat_id}")
                confirm = input("   이 ID로 설정할까요? (y/n, 기본: y): ").strip().lower()
                if confirm == "n":
                    chat_id = input("   chat_id 직접 입력: ").strip()
            else:
                print("   ⚠ 봇에게 아무 메시지를 보낸 후 다시 시도하세요.")
                if current_chat_id:
                    print(f"   기존 chat_id 사용: {current_chat_id}")
                    chat_id = current_chat_id
                else:
                    chat_id = input("   chat_id 직접 입력 (없으면 Enter): ").strip()
    except Exception as e:
        print(f"   ⚠ 조회 실패: {e}")
        if current_chat_id:
            chat_id = current_chat_id
            print(f"   기존 chat_id 사용: {chat_id}")
        else:
            chat_id = input("   chat_id 직접 입력: ").strip()

    if not chat_id:
        print("   ⚠ chat_id 없이는 전송 불가. 건너뜁니다.")
        return {"enabled": False}

    return {"enabled": True, "bot_token": token, "chat_id": chat_id}


def prompt_schedule(existing):
    current = existing.get("schedule", {})
    print("\n⏰ 수집 주기")
    print("   interval 형식 또는 cron 표현식을 직접 입력하세요.")
    print("   interval 예: 30m, 1h, 2h, 1d")
    print("   cron 예: 15 * * * *")
    print("   interval 형식은 start 시점 기준 현재+2분 anchor로 등록됩니다.")
    if current:
        current_label = current.get("label") or current.get("expression") or current.get("cron", "")
        print(f"   현재 설정: {current_label}")

    while True:
        raw = input("   주기 입력 (Enter면 현재값 유지, 없으면 기본 1h): ").strip()
        if not raw:
            if current:
                return current
            return {"mode": "interval", "expression": "1h", "label": "1시간마다"}

        interval_match = INTERVAL_RE.match(raw)
        if interval_match:
            value = int(interval_match.group(1))
            unit = interval_match.group(2).lower()
            if value <= 0:
                print("   ⚠ 0보다 큰 interval을 입력하세요.")
                continue
            if unit == "m" and 60 % value != 0:
                print("   ⚠ 분 interval은 현재 60의 약수만 지원합니다. 예: 10m, 15m, 20m, 30m")
                print("   ⚠ 그 외 간격은 cron 표현식을 사용하세요.")
                continue
            if unit == "h" and 24 % value != 0:
                print("   ⚠ 시간 interval은 현재 24의 약수만 지원합니다. 예: 1h, 2h, 3h, 4h, 6h, 8h, 12h")
                print("   ⚠ 그 외 간격은 cron 표현식을 사용하세요.")
                continue
            if unit == "d" and value != 1:
                print("   ⚠ day interval은 현재 1d만 지원합니다. 그 외에는 cron을 사용하세요.")
                continue
            label_unit = {"m": "분마다", "h": "시간마다", "d": "매일"}[unit]
            label = "매일" if unit == "d" and value == 1 else f"{value}{label_unit}"
            return {"mode": "interval", "expression": f"{value}{unit}", "label": label}

        if CRON_FIELD_RE.match(raw):
            label = input("   표시용 라벨 (없으면 Enter): ").strip() or f"cron: {raw}"
            return {"mode": "cron", "cron": raw, "label": label}

        print("   ⚠ interval(예: 30m, 2h, 1d) 또는 5필드 cron 표현식을 입력하세요.")


def main():
    print("=" * 50)
    print("  📡 AI 뉴스레터 설정")
    print("=" * 50)

    existing = load_existing()

    # 1. 플랫폼
    platforms = prompt_platforms(existing)

    # 2. 플랫폼별 상세
    config = {"platforms": platforms}

    if "reddit" in platforms:
        config["subreddits"] = prompt_subreddits(existing)

    keywords = prompt_ai_keywords(existing)
    if keywords:
        config["ai_keywords"] = keywords

    if "threads" in platforms:
        rsshub_url = prompt_threads(existing)
        if rsshub_url:
            config["rsshub_url"] = rsshub_url
            threads_accounts = prompt_threads_accounts(existing)
            if threads_accounts:
                config["threads_accounts"] = threads_accounts
            else:
                config["platforms"] = [p for p in platforms if p != "threads"]
                print("   → Threads 제외됨")
        else:
            config["platforms"] = [p for p in platforms if p != "threads"]
            print("   → Threads 제외됨")

    # 3. Telegram
    config["telegram"] = prompt_telegram(existing)

    # 4. 주기
    config["schedule"] = prompt_schedule(existing)

    # 5. 저장
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print("  ✅ 설정 완료!")
    print("=" * 50)
    print(f"\n  플랫폼: {', '.join(config['platforms'])}")
    if config.get("ai_keywords"):
        print(f"  AI 키워드: {', '.join(config['ai_keywords'])}")
    tg = config["telegram"]
    if tg.get("enabled"):
        print(f"  Telegram: {tg['chat_id']}")
    else:
        print("  Telegram: 비활성")
    if config.get("threads_accounts"):
        print(f"  Threads 계정: {', '.join(config['threads_accounts'])}")
        print(f"  RSSHub: {config.get('rsshub_url', '')}")
    print(f"  주기: {config['schedule']['label']}")
    print(f"\n  설정 파일: {CONFIG_FILE}")
    print("\n  다음 단계:")
    manage_cron = os.path.join(RUNTIME_ROOT, "scripts", "manage_cron.py")
    codex_runner = os.path.join(RUNTIME_ROOT, "scripts", "run_with_codex.sh")
    claude_runner = os.path.join(RUNTIME_ROOT, "scripts", "run_with_claude.sh")
    print(f"    python3 {manage_cron} start")
    if os.path.exists(codex_runner):
        print(f"    {codex_runner}")
    if os.path.exists(claude_runner):
        print(f"    {claude_runner}")
    print()


if __name__ == "__main__":
    main()
