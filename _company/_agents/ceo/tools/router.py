#!/usr/bin/env python3
# version: router_v1
"""Router — 사용자 명령을 분석해 적합한 specialist 에이전트를 추천.

키워드 기반 분류로 작업을 담당 에이전트에 매핑하고
CEO 시스템 프롬프트에 라우팅 결정을 주입합니다.

config (router.json):
  QUERY        — 라우팅할 사용자 명령
  MODE         — suggest (추천만) | brief (추천 + 작업 브리프)
  OUTPUT_PATH  — 라우팅 결과 저장 경로
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "router.json")


def _log(msg, kind="info"):
    icons = {"info": "🧭", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Routing rules: agent_id -> keywords (Korean + English)
ROUTING_RULES = {
    "youtube": [
        "유튜브", "youtube", "영상", "video", "채널", "channel", "구독", "조회수", "views",
        "썸네일", "thumbnail", "트렌드", "trend", "시청", "업로드", "upload", "레오",
        "스크립트", "쇼츠", "shorts", "알고리즘", "algorithm",
    ],
    "instagram": [
        "인스타", "instagram", "릴스", "reels", "피드", "feed", "스토리", "story",
        "팔로워", "followers", "해시태그", "hashtag", "게시", "post", "댓글",
    ],
    "designer": [
        "디자인", "design", "이미지", "image", "썸네일 디자인", "로고", "logo",
        "색상", "color", "브랜드", "brand", "비주얼", "visual", "그래픽", "graphic",
        "생성", "그려", "만들어", "dall-e", "stable diffusion",
    ],
    "developer": [
        "코드", "code", "개발", "develop", "프로그램", "program", "버그", "bug",
        "웹사이트", "website", "앱", "app", "api", "자동화", "automation",
        "스크립트", "script", "파이썬", "python", "타입스크립트", "코다리",
        "빌드", "build", "배포", "deploy", "git",
    ],
    "business": [
        "비즈니스", "business", "수익", "revenue", "매출", "sales", "수익화",
        "monetize", "가격", "price", "전략", "strategy", "roi", "kpi",
        "시장", "market", "경쟁", "competitor", "현빈", "paypal",
    ],
    "secretary": [
        "일정", "schedule", "캘린더", "calendar", "미팅", "meeting", "약속",
        "텔레그램", "telegram", "알림", "notification", "할 일", "todo",
        "브리핑", "briefing", "영숙", "비서", "secretary",
    ],
    "editor": [
        "음악", "music", "bgm", "사운드", "sound", "오디오", "audio",
        "영상 편집", "video edit", "루나", "luna", "musicgen", "ace-step",
        "배경음", "효과음", "합성",
    ],
    "writer": [
        "글", "writing", "카피", "copy", "스크립트", "script", "캡션", "caption",
        "블로그", "blog", "후크", "hook", "cta", "문장", "텍스트", "text",
        "카피라이팅", "copywriting",
    ],
    "researcher": [
        "리서치", "research", "조사", "investigate", "트렌드 조사", "경쟁사 조사",
        "검색", "search", "찾아", "데이터", "data", "분석", "analyze",
        "뉴스", "news", "통계", "statistics",
    ],
}

AGENT_INFO = {
    "youtube": {"name": "레오", "emoji": "📺", "role": "YouTube 전략가"},
    "instagram": {"name": "Instagram", "emoji": "📷", "role": "Instagram 운영"},
    "designer": {"name": "Designer", "emoji": "🎨", "role": "디자이너"},
    "developer": {"name": "코다리", "emoji": "💻", "role": "시니어 개발자"},
    "business": {"name": "현빈", "emoji": "💼", "role": "비즈니스 전략가"},
    "secretary": {"name": "영숙", "emoji": "📱", "role": "비서"},
    "editor": {"name": "루나", "emoji": "🎵", "role": "사운드 디렉터"},
    "writer": {"name": "Writer", "emoji": "✍️", "role": "카피라이터"},
    "researcher": {"name": "Researcher", "emoji": "🔍", "role": "리서처"},
}


def score_agents(query: str) -> list:
    query_lower = query.lower()
    scores = {}
    for agent_id, keywords in ROUTING_RULES.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        # Exact name match gets bonus
        info = AGENT_INFO.get(agent_id, {})
        if info.get("name", "").lower() in query_lower:
            score += 3
        if score > 0:
            scores[agent_id] = score
    return sorted(scores.items(), key=lambda x: -x[1])


def build_brief(query: str, agent_id: str, info: dict) -> str:
    templates = {
        "youtube": f"YouTube 관련 작업입니다. 레오에게 다음을 요청하세요:\n- 키워드: {query[:100]}\n- 필요 시 trend_sniper 또는 channel_full_analysis 도구 활용",
        "instagram": f"Instagram 콘텐츠 작업입니다:\n- 요청: {query[:100]}\n- 피드/릴스/스토리 형식 결정 후 캡션·해시태그 생성",
        "designer": f"디자인 작업입니다:\n- 요청: {query[:100]}\n- image_cloud 도구로 이미지 생성 또는 brand_check로 자산 검토",
        "developer": f"개발 작업입니다:\n- 요청: {query[:100]}\n- 코드 작성 후 lint_test 도구로 검증",
        "business": f"비즈니스 분석 작업입니다:\n- 요청: {query[:100]}\n- paypal_revenue 도구로 매출 데이터 확인 가능",
        "secretary": f"일정·알림 작업입니다:\n- 요청: {query[:100]}\n- 캘린더 추가 또는 텔레그램 알림 설정",
        "editor": f"음악·사운드 작업입니다:\n- 요청: {query[:100]}\n- music_generate 또는 music_to_video 도구 활용",
        "writer": f"글쓰기 작업입니다:\n- 요청: {query[:100]}\n- multi_platform_adapt 또는 hook_library 도구 활용",
        "researcher": f"리서치 작업입니다:\n- 요청: {query[:100]}\n- web_search 또는 page_fetcher 도구 활용",
    }
    return templates.get(agent_id, f"작업: {query[:100]}")


def main():
    cfg = load_config()
    query = cfg.get("QUERY", "").strip()
    if not query:
        _log("QUERY가 비어있어요. 라우팅할 명령을 입력하세요.", "warn")
        sys.exit(1)

    mode = cfg.get("MODE", "suggest").lower()
    output_path = cfg.get("OUTPUT_PATH", os.path.join(HERE, "routing_result.md"))

    _log(f"라우팅 분석: {query[:80]}")
    ranked = score_agents(query)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 🧭 CEO 라우팅 결과",
        f"",
        f"**명령**: {query}  ",
        f"**분석 시간**: {now}",
        f"",
        f"---",
        f"",
    ]

    if not ranked:
        lines += [
            f"## 결과",
            f"",
            f"⚠️  명확한 담당 에이전트를 찾지 못했어요.",
            f"",
            f"**권장**: 명령을 더 구체적으로 작성하거나 직접 에이전트를 선택하세요.",
            f"",
            f"**전체 에이전트 목록:**",
        ]
        for aid, info in AGENT_INFO.items():
            lines.append(f"- {info['emoji']} **{info['name']}** ({info['role']})")
    else:
        primary_id, primary_score = ranked[0]
        primary_info = AGENT_INFO.get(primary_id, {})

        lines += [
            f"## 🎯 주 담당",
            f"",
            f"**{primary_info.get('emoji', '')} {primary_info.get('name', primary_id)}** ({primary_info.get('role', primary_id)})",
            f"",
        ]

        if mode == "brief":
            brief = build_brief(query, primary_id, primary_info)
            lines += [
                f"### 작업 브리프",
                f"",
                brief,
                f"",
            ]

        if len(ranked) > 1:
            lines += ["## 🤝 협력 필요 에이전트", ""]
            for aid, score in ranked[1:3]:
                info = AGENT_INFO.get(aid, {})
                lines.append(f"- {info.get('emoji', '')} **{info.get('name', aid)}** — {info.get('role', '')}")
            lines.append("")

    lines += [
        f"---",
        f"",
        f"## 라우팅 점수표",
        f"",
        f"| 에이전트 | 점수 |",
        f"|---|---|",
    ]
    for aid, score in ranked[:5]:
        info = AGENT_INFO.get(aid, {})
        lines.append(f"| {info.get('emoji', '')} {info.get('name', aid)} | {'⭐' * min(score, 5)} ({score}) |")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Console output
    _log("라우팅 완료!", "ok")
    if ranked:
        primary_id, _ = ranked[0]
        primary_info = AGENT_INFO.get(primary_id, {})
        print(f"\n🎯 → {primary_info.get('emoji', '')} {primary_info.get('name', primary_id)} ({primary_info.get('role', '')})")
        if len(ranked) > 1:
            others = [AGENT_INFO.get(a, {}).get("name", a) for a, _ in ranked[1:3]]
            print(f"🤝 협력: {', '.join(others)}")
    else:
        print("⚠️  담당 에이전트를 특정할 수 없어요.")

    print(f"\n📄 저장: {output_path}")
    print("\n" + "=" * 60)
    print(content)


if __name__ == "__main__":
    main()
