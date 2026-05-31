#!/usr/bin/env python3
# version: hook_library_v1
"""Hook Library — 후크·CTA 라이브러리 관리.

후크와 CTA를 JSON DB에 저장·조회·추가합니다.
에이전트가 콘텐츠 작성 시 여기서 맞는 후크를 가져옵니다.

config (hook_library.json):
  ACTION     — list | search | add | export
  KEYWORD    — 검색 키워드 (ACTION=search 때)
  CATEGORY   — 카테고리 필터 (youtube, instagram, blog, universal)
  NEW_HOOK   — 추가할 후크 텍스트 (ACTION=add 때)
  NEW_CATEGORY — 새 후크의 카테고리
  NEW_TAGS   — 태그 (쉼표 구분)
  DB_PATH    — 라이브러리 파일 경로 (기본 hooks_db.json)
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "hook_library.json")
DEFAULT_DB = os.path.join(HERE, "hooks_db.json")

BUILTIN_HOOKS = [
    {"id": 1, "hook": "오늘 이 영상 하나로 [결과]를 바꿀 수 있어요.", "category": "youtube", "tags": ["후크", "약속"], "created": "2026-01-01"},
    {"id": 2, "hook": "대부분의 사람들이 [실수]를 하는데, 당신은 다를 수 있어요.", "category": "youtube", "tags": ["차별화", "후크"], "created": "2026-01-01"},
    {"id": 3, "hook": "3분 안에 [주제]의 핵심을 알려드릴게요.", "category": "youtube", "tags": ["시간", "효율"], "created": "2026-01-01"},
    {"id": 4, "hook": "[수치]만에 [결과]를 달성하는 법", "category": "universal", "tags": ["수치", "결과"], "created": "2026-01-01"},
    {"id": 5, "hook": "이걸 모르면 손해예요 👀", "category": "instagram", "tags": ["긴급성", "후크"], "created": "2026-01-01"},
    {"id": 6, "hook": "당신이 [행동]하지 않는 진짜 이유", "category": "universal", "tags": ["심리", "공감"], "created": "2026-01-01"},
    {"id": 7, "hook": "솔직히 말할게요. [불편한 진실].", "category": "universal", "tags": ["솔직함", "신뢰"], "created": "2026-01-01"},
    {"id": 8, "hook": "저도 처음엔 [실패]했어요. 그런데...", "category": "universal", "tags": ["스토리", "공감"], "created": "2026-01-01"},
    {"id": 9, "hook": "전문가들은 [방법]을 쓰는데 아무도 안 가르쳐줘요.", "category": "youtube", "tags": ["권위", "비밀"], "created": "2026-01-01"},
    {"id": 10, "hook": "저장하세요. 나중에 꼭 필요해질 거예요 📌", "category": "instagram", "tags": ["저장", "CTA"], "created": "2026-01-01"},
    {"id": 11, "hook": "오늘부터 [기간] 동안 [도전]해봤습니다.", "category": "youtube", "tags": ["챌린지", "실험"], "created": "2026-01-01"},
    {"id": 12, "hook": "구독하고 [이득]을 놓치지 마세요!", "category": "youtube", "tags": ["구독", "CTA"], "created": "2026-01-01"},
    {"id": 13, "hook": "댓글로 [질문]에 대한 의견 알려주세요 💬", "category": "universal", "tags": ["참여", "CTA"], "created": "2026-01-01"},
    {"id": 14, "hook": "이 포스트 공유해서 [대상]에게도 알려주세요!", "category": "instagram", "tags": ["공유", "CTA"], "created": "2026-01-01"},
    {"id": 15, "hook": "링크 클릭하면 [이득] 받을 수 있어요 ⬆️", "category": "instagram", "tags": ["링크", "CTA"], "created": "2026-01-01"},
]


def _log(msg, kind="info"):
    icons = {"info": "📚", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_db(db_path: str) -> list:
    if not os.path.exists(db_path):
        # Seed with built-in hooks
        save_db(db_path, BUILTIN_HOOKS)
        return BUILTIN_HOOKS[:]
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db_path: str, hooks: list):
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(hooks, f, ensure_ascii=False, indent=2)


def do_list(hooks: list, category: str):
    if category and category != "all":
        filtered = [h for h in hooks if h.get("category", "") == category]
    else:
        filtered = hooks

    _log(f"라이브러리 — {len(filtered)}개 후크 ({category or '전체'})", "ok")
    print()
    for h in filtered:
        print(f"[{h.get('id', '?')}] ({h.get('category', '?')}) {h.get('hook', '')}")
        if h.get("tags"):
            print(f"     태그: {', '.join(h['tags'])}")
        print()
    return filtered


def do_search(hooks: list, keyword: str) -> list:
    keyword_lower = keyword.lower()
    matches = [
        h for h in hooks
        if keyword_lower in h.get("hook", "").lower()
        or keyword_lower in " ".join(h.get("tags", [])).lower()
        or keyword_lower in h.get("category", "").lower()
    ]
    _log(f"'{keyword}' 검색 결과 — {len(matches)}개", "ok")
    print()
    for h in matches:
        print(f"[{h.get('id', '?')}] ({h.get('category', '?')}) {h.get('hook', '')}")
        print(f"     태그: {', '.join(h.get('tags', []))}")
        print()
    return matches


def do_add(hooks: list, hook_text: str, category: str, tags_raw: str) -> list:
    tags = [t.strip() for t in str(tags_raw).split(",") if t.strip()]
    new_id = max((h.get("id", 0) for h in hooks), default=0) + 1
    new_hook = {
        "id": new_id,
        "hook": hook_text,
        "category": category or "universal",
        "tags": tags,
        "created": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    hooks.append(new_hook)
    _log(f"추가됨 [ID {new_id}]: {hook_text[:60]}", "ok")
    return hooks


def do_export(hooks: list, category: str) -> str:
    if category and category != "all":
        filtered = [h for h in hooks if h.get("category", "") == category]
    else:
        filtered = hooks

    lines = [f"# 📚 후크·CTA 라이브러리 ({category or '전체'})\n"]
    by_cat: dict = {}
    for h in filtered:
        cat = h.get("category", "기타")
        by_cat.setdefault(cat, []).append(h)

    for cat, items in by_cat.items():
        lines.append(f"## {cat.upper()}\n")
        for h in items:
            lines.append(f"- {h.get('hook', '')}")
            if h.get("tags"):
                lines.append(f"  _(태그: {', '.join(h['tags'])})_")
        lines.append("")

    return "\n".join(lines)


def main():
    cfg = load_config()
    action = cfg.get("ACTION", "list").lower()
    keyword = cfg.get("KEYWORD", "").strip()
    category = cfg.get("CATEGORY", "").strip()
    new_hook = cfg.get("NEW_HOOK", "").strip()
    new_category = cfg.get("NEW_CATEGORY", "universal").strip()
    new_tags = cfg.get("NEW_TAGS", "").strip()
    db_path = cfg.get("DB_PATH", DEFAULT_DB)
    if not os.path.isabs(db_path):
        db_path = os.path.join(HERE, db_path)

    hooks = load_db(db_path)

    if action == "list":
        do_list(hooks, category)

    elif action == "search":
        if not keyword:
            _log("KEYWORD를 입력하세요.", "warn")
            sys.exit(1)
        do_search(hooks, keyword)

    elif action == "add":
        if not new_hook:
            _log("NEW_HOOK을 입력하세요.", "warn")
            sys.exit(1)
        hooks = do_add(hooks, new_hook, new_category, new_tags)
        save_db(db_path, hooks)
        print(f"📦 DB 저장: {db_path} ({len(hooks)}개)")

    elif action == "export":
        content = do_export(hooks, category)
        export_path = os.path.join(HERE, "hooks_export.md")
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)
        _log(f"내보내기 완료: {export_path}", "ok")
        print(content)

    else:
        _log(f"알 수 없는 ACTION: {action}. list/search/add/export 중 선택.", "warn")
        sys.exit(1)


if __name__ == "__main__":
    main()
