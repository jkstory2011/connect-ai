#!/usr/bin/env python3
# version: web_search_v1
"""Web Search — DuckDuckGo HTML 검색 (API 키 불필요) + 선택적 Brave Search API.

config (web_search.json):
  QUERY        — 검색어
  MAX_RESULTS  — 결과 수 (기본 10)
  ENGINE       — "duckduckgo" (기본, 무료) | "brave" (유료)
  BRAVE_API_KEY — Brave Search API 키 (ENGINE=brave 일 때만)
  REPORT_APPEND — "true" 이면 기존 보고서에 추가, "false" 이면 덮어쓰기

Requires: pip install requests (beautifulsoup4 선택사항 — 더 정확한 파싱)
"""
import os, sys, json, datetime, re, time
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "web_search.json")
REPORT_PATH = os.path.join(HERE, "web_search_result.md")


def _log(msg, kind="info"):
    icons = {"info": "🔍", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind,'•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class _DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._cur = {}
        self._in_title = False
        self._in_snippet = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        href = d.get("href", "")
        if "result__a" in cls:
            self._in_title = True
            self._cur = {"url": href, "title": "", "snippet": ""}
        if "result__snippet" in cls:
            self._in_snippet = True

    def handle_endtag(self, tag):
        if self._in_title and tag == "a":
            self._in_title = False
        if self._in_snippet and tag in ("a", "div"):
            self._in_snippet = False
            if self._cur.get("title"):
                self.results.append(dict(self._cur))
                self._cur = {}

    def handle_data(self, data):
        if self._in_title:
            self._cur["title"] = (self._cur.get("title", "") + data).strip()
        if self._in_snippet:
            self._cur["snippet"] = (self._cur.get("snippet", "") + data).strip()


def search_duckduckgo(query: str, max_results: int = 10) -> list:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query, "kl": "kr-kr"},
            headers=headers,
            timeout=20,
        )
        r.raise_for_status()
    except Exception as e:
        _log(f"DuckDuckGo 요청 실패: {e}", "err")
        return []

    parser = _DDGParser()
    parser.feed(r.text)
    return parser.results[:max_results]


def search_brave(query: str, api_key: str, max_results: int = 10) -> list:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)

    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
            params={"q": query, "count": max_results, "country": "KR"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        _log(f"Brave Search 실패: {e}", "err")
        return []

    return [
        {"url": x.get("url", ""), "title": x.get("title", ""), "snippet": x.get("description", "")}
        for x in data.get("web", {}).get("results", [])
    ]


def main():
    cfg = load_config()
    query = cfg.get("QUERY", "").strip()
    if not query:
        _log("QUERY가 비어있어요. web_search.json에 검색어를 입력하세요.", "warn")
        sys.exit(1)

    max_results = int(cfg.get("MAX_RESULTS", 10))
    engine = cfg.get("ENGINE", "duckduckgo").lower()
    append_mode = str(cfg.get("REPORT_APPEND", "false")).lower() == "true"

    _log(f"[{engine.upper()}] 검색: {query}")

    if engine == "brave":
        api_key = cfg.get("BRAVE_API_KEY", "").strip()
        if not api_key:
            _log("BRAVE_API_KEY 없음 → DuckDuckGo로 전환", "warn")
            engine = "duckduckgo"

    results = search_brave(query, api_key, max_results) if engine == "brave" else search_duckduckgo(query, max_results)

    if not results:
        _log("검색 결과가 없습니다.", "warn")
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🔍 웹 검색 결과\n",
        f"**검색어**: {query}  ",
        f"**엔진**: {engine.upper()}  ",
        f"**시간**: {now}  ",
        f"**결과**: {len(results)}건\n",
        f"---\n",
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r.get('title', '(제목 없음)')}")
        lines.append(f"- URL: {r.get('url', '')}")
        snip = r.get("snippet", "").strip()
        if snip:
            lines.append(f"- 요약: {snip}")
        lines.append("")

    content = "\n".join(lines)
    mode = "a" if append_mode else "w"
    with open(REPORT_PATH, mode, encoding="utf-8") as f:
        if append_mode:
            f.write(f"\n\n---\n\n")
        f.write(content)

    _log(f"검색 완료 — {len(results)}건", "ok")
    for i, r in enumerate(results, 1):
        print(f"  {i:2d}. {r.get('title','')[:55]}")
        print(f"      {r.get('url','')[:70]}")
    print(f"\n📄 결과 저장: {REPORT_PATH}")
    print("\n" + "=" * 60)
    print(content)


if __name__ == "__main__":
    main()
