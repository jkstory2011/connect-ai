#!/usr/bin/env python3
# version: multi_platform_adapt_v1
"""Multi Platform Adapt — 하나의 스크립트를 YouTube·Instagram·블로그 형식으로 변환.

소스 텍스트(또는 파일)를 읽고 각 플랫폼별 최적 포맷으로 변환해 저장합니다.
변환은 규칙 기반 + LLM 없이 순수 Python으로 동작.

config (multi_platform_adapt.json):
  SOURCE_FILE    — 원본 스크립트/글 파일 경로
  SOURCE_TEXT    — 직접 텍스트 입력 (SOURCE_FILE이 없을 때)
  PLATFORMS      — 변환할 플랫폼 목록 (youtube,instagram,blog 중 콤마 구분)
  OUTPUT_DIR     — 출력 폴더 (기본 이 폴더 아래 adapted/)
  TITLE          — 콘텐츠 제목 (파일명에 사용)
"""
import os, sys, json, datetime, re, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "multi_platform_adapt.json")


def _log(msg, kind="info"):
    icons = {"info": "✍️", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_source(cfg: dict) -> str:
    source_file = cfg.get("SOURCE_FILE", "").strip()
    source_text = cfg.get("SOURCE_TEXT", "").strip()

    if source_file:
        path = os.path.expanduser(source_file)
        if not os.path.exists(path):
            _log(f"소스 파일 없음: {path}", "err")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    if source_text:
        return source_text
    _log("SOURCE_FILE 또는 SOURCE_TEXT 중 하나를 설정하세요.", "warn")
    sys.exit(1)


def _extract_key_points(text: str) -> list:
    lines = text.split("\n")
    points = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Headings and list items are likely key points
        if line.startswith("#") or line.startswith("-") or line.startswith("*"):
            clean = re.sub(r"^[#\-\*\s]+", "", line).strip()
            if len(clean) > 5:
                points.append(clean)
        elif re.match(r"^\d+\.", line):
            clean = re.sub(r"^\d+\.\s*", "", line).strip()
            if len(clean) > 5:
                points.append(clean)
    if not points:
        # Fallback: take first sentences
        sentences = re.split(r"[.!?]\s+", text)
        points = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
    return points[:10]


def _clean_text(text: str) -> str:
    # Remove markdown formatting for plain text
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text.strip()


def adapt_youtube(text: str, title: str) -> str:
    key_points = _extract_key_points(text)
    word_count = len(text.split())
    estimated_min = max(3, word_count // 130)  # ~130 Korean syllables/min

    lines = [
        f"# 📺 YouTube 스크립트 — {title}",
        f"",
        f"**예상 영상 길이**: {estimated_min}~{estimated_min + 2}분",
        f"",
        f"---",
        f"",
        f"## 🎯 후크 (0~5초)",
        f"",
        f"> (시청자의 관심을 잡는 한 문장으로 시작)",
        f"> 예: \"오늘 이 영상을 보면 [핵심 이득]을 얻을 수 있어요.\"",
        f"",
        f"---",
        f"",
        f"## 📋 인트로 (0:05~0:30)",
        f"",
        f"안녕하세요! 오늘은 **{title}**에 대해 이야기해볼게요.",
        f"",
        f"이 영상에서 다룰 내용:",
    ]
    for i, pt in enumerate(key_points[:5], 1):
        lines.append(f"{i}. {pt}")

    lines += [
        f"",
        f"끝까지 보시면 [핵심 이득]을 얻을 수 있습니다!",
        f"",
        f"---",
        f"",
        f"## 🎬 본문",
        f"",
        _clean_text(text),
        f"",
        f"---",
        f"",
        f"## 🏁 아웃트로 & CTA",
        f"",
        f"오늘 영상 어떠셨나요? 도움이 됐다면 **좋아요**와 **구독** 꼭 부탁드려요! 🙏",
        f"",
        f"궁금한 점은 **댓글**로 남겨주세요. 다음 영상에서 만나요!",
        f"",
        f"---",
        f"",
        f"## 🏷️ 메타데이터",
        f"",
        f"**제목 후보**:",
        f"- {title}",
        f"- {title} | 완벽 가이드",
        f"- {title}하는 법 (초보자도 쉽게)",
        f"",
        f"**설명 첫 줄 (검색용)**:",
        f"> 이 영상에서는 {title}에 대해 다룹니다.",
        f"",
        f"**태그 (예시)**: #{title.replace(' ', '')} #유튜브 #콘텐츠",
    ]
    return "\n".join(lines)


def adapt_instagram(text: str, title: str) -> str:
    key_points = _extract_key_points(text)
    hook = key_points[0] if key_points else title

    lines = [
        f"# 📷 Instagram 포맷 — {title}",
        f"",
        f"---",
        f"",
        f"## 🎯 피드 포스트",
        f"",
        f"**후크 (첫 줄)**:",
        f"> {hook}",
        f"",
        f"**캡션**:",
        f"```",
        f"{hook} ✨",
        f"",
    ]
    for pt in key_points[:4]:
        lines.append(f"👉 {pt}")
    lines += [
        f"",
        f"어떻게 생각하시나요? 댓글로 알려주세요! 💬",
        f"",
        f"{'→ ' + title}",
        f"",
        f"#콘텐츠 #{title.replace(' ', '')} #크리에이터 #한국 #인스타그램",
        f"```",
        f"",
        f"---",
        f"",
        f"## 🎬 릴스 스크립트 (15~30초)",
        f"",
        f"**0~3초 후크**: {hook}",
        f"",
        f"**본문** (빠르게 진행):",
    ]
    for i, pt in enumerate(key_points[:3], 1):
        lines.append(f"- {i}. {pt}")
    lines += [
        f"",
        f"**CTA**: 저장하고 나중에 다시 보세요! 💾",
        f"",
        f"**음악 분위기**: 밝고 경쾌한 팝 또는 트렌디 BGM",
        f"",
        f"---",
        f"",
        f"## 📱 스토리 (3~5장)",
        f"",
        f"1. 슬라이드: 질문/후크 — \"{hook}?\"",
        f"2. 슬라이드: 핵심 포인트 1 — {key_points[0] if key_points else '...'}",
        f"3. 슬라이드: 핵심 포인트 2 — {key_points[1] if len(key_points) > 1 else '...'}",
        f"4. 슬라이드: 결론 + 링크 — \"전체 내용은 피드에서!\"",
        f"5. 설문: \"도움이 됐나요? 👍/👎\"",
    ]
    return "\n".join(lines)


def adapt_blog(text: str, title: str) -> str:
    key_points = _extract_key_points(text)

    lines = [
        f"# 📝 블로그 포스트 — {title}",
        f"",
        f"**메타 설명** (SEO용, 150자 이내):",
        f"> {title}에 대해 알아봅니다. {key_points[0] if key_points else '핵심 내용을 정리했습니다.'}",
        f"",
        f"**키워드**: {title}, {', '.join(key_points[:3])}",
        f"",
        f"---",
        f"",
        f"## 서론",
        f"",
        f"{title}에 대해 궁금하신가요? 이 글에서는 {title}의 핵심을 쉽게 설명합니다.",
        f"",
        f"**이 글에서 다루는 내용:**",
    ]
    for i, pt in enumerate(key_points[:5], 1):
        lines.append(f"{i}. {pt}")

    lines += [
        f"",
        f"---",
        f"",
        f"## 본문",
        f"",
        text,
        f"",
        f"---",
        f"",
        f"## 결론",
        f"",
        f"지금까지 **{title}**에 대해 알아봤습니다.",
        f"",
        f"**핵심 요약:**",
    ]
    for pt in key_points[:4]:
        lines.append(f"- {pt}")
    lines += [
        f"",
        f"이 글이 도움이 됐다면 공유해주세요! 💌",
        f"",
        f"---",
        f"",
        f"*이 글은 Writer 에이전트가 자동 변환했습니다.*",
    ]
    return "\n".join(lines)


ADAPTERS = {
    "youtube": adapt_youtube,
    "instagram": adapt_instagram,
    "blog": adapt_blog,
}


def main():
    cfg = load_config()
    text = load_source(cfg)
    title = cfg.get("TITLE", "콘텐츠").strip() or "콘텐츠"

    platforms_raw = cfg.get("PLATFORMS", "youtube,instagram,blog")
    platforms = [p.strip().lower() for p in str(platforms_raw).split(",")]
    platforms = [p for p in platforms if p in ADAPTERS]
    if not platforms:
        _log("유효한 PLATFORMS가 없어요. youtube, instagram, blog 중 선택.", "warn")
        sys.exit(1)

    output_dir = cfg.get("OUTPUT_DIR", os.path.join(HERE, "adapted"))
    os.makedirs(output_dir, exist_ok=True)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = re.sub(r"[^\w가-힣\-]", "_", title)[:30]

    _log(f"'{title}' → {', '.join(platforms)} 변환 중...")

    saved = []
    for platform in platforms:
        adapter = ADAPTERS[platform]
        adapted = adapter(text, title)
        fname = f"{safe_title}_{platform}_{now}.md"
        fpath = os.path.join(output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(adapted)
        saved.append((platform, fpath))
        _log(f"  [{platform.upper()}] 저장: {fname}", "ok")

    print(f"\n✅ 변환 완료 — {len(saved)}개 플랫폼")
    for platform, fpath in saved:
        print(f"  📄 {platform.upper()}: {fpath}")
        print()

    # Print first platform result
    if saved:
        first_path = saved[0][1]
        with open(first_path, "r", encoding="utf-8") as f:
            print(f.read()[:3000])


if __name__ == "__main__":
    main()
