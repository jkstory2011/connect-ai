#!/usr/bin/env python3
# version: monitor_daily_v1
"""Monitor Daily — 지정 주제를 매일 자동 검색해 브리핑 보고서 생성.

설정한 TOPICS를 DuckDuckGo로 검색하고 결과를 날짜별 마크다운으로 저장.
CEO 브리핑이나 트렌드 모니터링 자동화에 사용.

config (monitor_daily.json):
  TOPICS        — 모니터링할 주제 목록 (배열)
  MAX_PER_TOPIC — 주제당 결과 수 (기본 5)
  REPORT_DIR    — 보고서 저장 폴더 (기본 이 폴더 아래 monitor_reports/)
  LANG          — 검색 언어/지역 코드 (기본 kr-kr)

Requires: pip install requests
"""
import os, sys, json, datetime, time
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "monitor_daily.json")


def _log(msg, kind="info"):
    icons = {"info": "📡", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


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
        self._in_t = False
        self._in_s = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        href = d.get("href", "")
        if "result__a" in cls:
            self._in_t = True
            self._cur = {"url": href, "title": "", "snippet": ""}
        if "result__snippet" in cls:
            self._in_s = True

    def handle_endtag(self, tag):
        if self._in_t and tag == "a":
            self._in_t = False
        if self._in_s and tag in ("a", "div"):
            self._in_s = False
            if self._cur.get("title"):
                self.results.append(dict(self._cur))
                self._cur = {}

    def handle_data(self, data):
        if self._in_t:
            self._cur["title"] = (self._cur.get("title", "") + data).strip()
        if self._in_s:
            self._cur["snippet"] = (self._cur.get("snippet", "") + data).strip()


def search_ddg(query: str, max_results: int = 5, lang: str = "kr-kr") -> list:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query, "kl": lang},
            headers=headers,
            timeout=20,
        )
        r.raise_for_status()
    except Exception as e:
        _log(f"검색 실패 [{query}]: {e}", "warn")
        return []

    p = _DDGParser()
    p.feed(r.text)
    return p.results[:max_results]


def main():
    cfg = load_config()
    topics = cfg.get("TOPICS", [])
    if not topics:
        _log("TOPICS가 비어있어요. monitor_daily.json에 모니터링할 주제를 추가하세요.", "warn")
        _log("예: [\"AI 뉴스\", \"유튜브 알고리즘\", \"한국 크리에이터 트렌드\"]", "info")
        sys.exit(1)

    max_per = int(cfg.get("MAX_PER_TOPIC", 5))
    lang = cfg.get("LANG", "kr-kr")
    report_dir = cfg.get("REPORT_DIR", os.path.join(HERE, "monitor_reports"))
    os.makedirs(report_dir, exist_ok=True)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    report_path = os.path.join(report_dir, f"monitor_{date_str}.md")

    _log(f"일일 모니터링 시작 — {date_str} {time_str}")
    _log(f"주제 {len(topics)}개: {', '.join(topics)}")

    lines = [
        f"# 📡 일일 모니터링 브리핑",
        f"",
        f"**날짜**: {date_str} {time_str}  ",
        f"**주제 수**: {len(topics)}개  ",
        f"",
        f"---",
        f"",
    ]

    total_results = 0
    for topic in topics:
        _log(f"  [{topic}] 검색 중...")
        results = search_ddg(topic, max_per, lang)
        total_results += len(results)
        time.sleep(1.2)  # 폴라이트 딜레이

        lines.append(f"## 📌 {topic}")
        lines.append("")
        if not results:
            lines.append("_검색 결과 없음_")
        else:
            for r in results:
                title = r.get("title", "(제목 없음)")
                url = r.get("url", "")
                snippet = r.get("snippet", "").strip()
                lines.append(f"- **[{title}]({url})**")
                if snippet:
                    lines.append(f"  > {snippet[:180]}")
                lines.append("")
        lines.append("")

    lines += [
        "---",
        "",
        f"_자동 생성: monitor_daily.py | {date_str} {time_str} | 총 {total_results}건_",
    ]
    content = "\n".join(lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 최신 보고서 링크도 latest.md로 복사
    latest_path = os.path.join(report_dir, "latest.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(content)

    _log(f"모니터링 완료!", "ok")
    print(f"   주제: {len(topics)}개 | 결과: {total_results}건")
    print(f"   저장: {report_path}")
    print(f"   최신: {latest_path}")
    print("\n" + "=" * 60)
    print(content[:4000])
    if len(content) > 4000:
        print(f"\n... (나머지 → {report_path})")


if __name__ == "__main__":
    main()
