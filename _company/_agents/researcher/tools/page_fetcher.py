#!/usr/bin/env python3
# version: page_fetcher_v1
"""Page Fetcher — URL 본문 추출 + 출처 인용.

URL의 메인 텍스트를 추출해 마크다운으로 저장합니다.
BeautifulSoup4 설치 시 더 정확한 본문 파싱.

config (page_fetcher.json):
  URL       — 가져올 페이지 URL
  MAX_CHARS — 최대 글자 수 (기본 6000)
  SAVE_TO   — 저장 파일명 (기본 page_fetch_result.md, 이 폴더 기준)

Requires: pip install requests
Optional: pip install beautifulsoup4
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "page_fetcher.json")


def _log(msg, kind="info"):
    icons = {"info": "📄", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_and_extract(url: str, max_chars: int) -> tuple:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
    except Exception as e:
        _log(f"페이지 요청 실패: {e}", "err")
        sys.exit(1)

    title = ""
    text = ""

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            tag.decompose()
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Try common content containers
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(id=re.compile(r"(content|main|article|post)", re.I))
            or soup.find(class_=re.compile(r"(content|article|post|body|entry)", re.I))
        )
        target = main if main else soup.find("body") or soup
        lines = [l.strip() for l in target.get_text(separator="\n", strip=True).split("\n") if l.strip()]
        text = "\n".join(lines)
    except ImportError:
        # Regex fallback
        t_m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        title = t_m.group(1).strip() if t_m else ""
        body_m = re.search(r"<body[^>]*>(.*?)</body>", html, re.I | re.S)
        raw = body_m.group(1) if body_m else html
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[... 이하 {len(text) - max_chars:,}자 생략 — 전체는 URL 직접 참조]"

    return title, text


def main():
    cfg = load_config()
    url = cfg.get("URL", "").strip()
    if not url:
        _log("URL이 비어있어요. page_fetcher.json에 URL을 입력하세요.", "warn")
        sys.exit(1)

    max_chars = int(cfg.get("MAX_CHARS", 6000))
    save_name = cfg.get("SAVE_TO", "page_fetch_result.md")
    save_path = save_name if os.path.isabs(save_name) else os.path.join(HERE, save_name)

    _log(f"가져오는 중: {url}")
    title, content = fetch_and_extract(url, max_chars)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report = "\n".join([
        f"# 📄 페이지 내용 추출",
        f"",
        f"**제목**: {title}",
        f"**URL**: {url}",
        f"**추출 시간**: {now}",
        f"**글자 수**: {len(content):,}자",
        f"",
        f"---",
        f"",
        content,
        f"",
        f"---",
        f"",
        f"*출처: [{title or url}]({url})*",
    ])

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(report)

    _log(f"추출 완료!", "ok")
    print(f"   제목: {title}")
    print(f"   글자 수: {len(content):,}자")
    print(f"   저장: {save_path}")
    print("\n" + "=" * 60)
    preview = report[:3000]
    print(preview)
    if len(report) > 3000:
        print(f"\n... (나머지 {len(report) - 3000:,}자 → 파일 참조)")


if __name__ == "__main__":
    main()
