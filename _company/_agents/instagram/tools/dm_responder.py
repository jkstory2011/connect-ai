#!/usr/bin/env python3
# version: dm_responder_v1
"""DM Responder — 댓글·DM 조회 및 답글 초안 생성.

최근 게시물의 댓글을 가져와 분류하고 답글 초안을 생성합니다.
실제 답글 게시는 Draft 모드로 저장 후 수동 확인 권장.

config (dm_responder.json):
  ACCESS_TOKEN      — Instagram Access Token
  INSTAGRAM_USER_ID — 계정 ID
  ACTION            — list_comments | draft_replies
  MAX_POSTS         — 조회할 최근 게시물 수 (기본 3)
  MAX_COMMENTS      — 게시물당 댓글 수 (기본 10)
  REPLY_TONE        — friendly | professional | casual

Requires: pip install requests
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "dm_responder.json")
ACCOUNT_PATH = os.path.join(HERE, "instagram_account.json")
GRAPH_BASE = "https://graph.instagram.com"


def _log(msg, kind="info"):
    icons = {"info": "💬", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    cfg = {}
    for p in [ACCOUNT_PATH, CONFIG_PATH]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg.update(json.load(f))
            except Exception:
                pass
    return cfg


def api_get(endpoint: str, token: str, params: dict = None) -> dict:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)
    p = {"access_token": token}
    if params:
        p.update(params)
    try:
        r = requests.get(f"{GRAPH_BASE}{endpoint}", params=p, timeout=20)
        data = r.json()
        if "error" in data:
            err = data["error"]
            _log(f"API 오류 {err.get('code')}: {err.get('message')}", "err")
            sys.exit(1)
        return data
    except SystemExit:
        raise
    except Exception as e:
        _log(f"요청 실패: {e}", "err")
        sys.exit(1)


SENTIMENT_PATTERNS = {
    "positive": ["좋아요", "최고", "감사", "사랑", "대박", "👍", "❤️", "😍", "🔥", "완벽", "훌륭"],
    "negative": ["별로", "싫어", "최악", "실망", "아쉽", "👎", "😤", "화나", "불만"],
    "question": ["?", "어떻게", "뭐야", "언제", "어디", "얼마", "왜", "인가요", "인지"],
    "spam": ["팔로우", "f4f", "l4l", "맞팔", "광고", "할인", "http://", "https://"],
}


def classify_comment(text: str) -> str:
    text_lower = text.lower()
    for category, patterns in SENTIMENT_PATTERNS.items():
        if any(p.lower() in text_lower for p in patterns):
            return category
    return "neutral"


def draft_reply(comment: str, tone: str) -> str:
    sentiment = classify_comment(comment)
    replies = {
        "friendly": {
            "positive": "감사해요! 앞으로도 좋은 콘텐츠로 찾아올게요 😊",
            "negative": "소중한 피드백 감사합니다. 더 좋은 콘텐츠가 될 수 있도록 노력할게요!",
            "question": "좋은 질문이에요! 자세한 내용은 DM으로 알려드릴게요 💌",
            "spam": None,  # Don't reply to spam
            "neutral": "댓글 감사해요! 💛",
        },
        "professional": {
            "positive": "소중한 피드백 감사합니다.",
            "negative": "의견 주셔서 감사합니다. 지속적으로 개선하겠습니다.",
            "question": "문의 감사드립니다. 자세한 내용은 DM 또는 이메일로 안내드리겠습니다.",
            "spam": None,
            "neutral": "댓글 감사드립니다.",
        },
        "casual": {
            "positive": "ㅎㅎ 감사합니다!! 🙏",
            "negative": "아쉬우셨군요 😢 다음엔 더 잘 할게요!",
            "question": "오 좋은 질문! DM 주시면 자세히 설명해드릴게요~",
            "spam": None,
            "neutral": "댓글 감사해요~",
        },
    }
    tone_replies = replies.get(tone, replies["friendly"])
    return tone_replies.get(sentiment, tone_replies["neutral"])


def main():
    cfg = load_config()
    token = cfg.get("ACCESS_TOKEN", "").strip()
    user_id = cfg.get("INSTAGRAM_USER_ID", "").strip()

    if not token or not user_id:
        _log("ACCESS_TOKEN 또는 INSTAGRAM_USER_ID가 없어요.", "warn")
        _log("먼저 instagram_account.py를 실행하세요.", "info")
        sys.exit(1)

    action = cfg.get("ACTION", "list_comments").lower()
    max_posts = int(cfg.get("MAX_POSTS", 3))
    max_comments = int(cfg.get("MAX_COMMENTS", 10))
    tone = cfg.get("REPLY_TONE", "friendly").lower()

    _log(f"최근 게시물 {max_posts}개 조회 중...")

    # Get recent media
    media_data = api_get(
        f"/{user_id}/media",
        token,
        {"fields": "id,caption,timestamp,media_type", "limit": str(max_posts)},
    )
    posts = media_data.get("data", [])

    if not posts:
        _log("게시물이 없어요.", "warn")
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report_lines = [
        f"# 💬 댓글 분석 보고서",
        f"",
        f"**계정 ID**: {user_id}  ",
        f"**분석 시간**: {now}  ",
        f"**조회 게시물**: {len(posts)}개",
        f"",
        f"---",
        f"",
    ]

    total_comments = 0
    for post in posts:
        post_id = post.get("id", "")
        caption = (post.get("caption", "") or "")[:80].replace("\n", " ")
        mtype = post.get("media_type", "POST")
        ts = post.get("timestamp", "")[:10]

        _log(f"  [{ts}] {mtype} 댓글 조회 중...")

        # Get comments
        try:
            comments_data = api_get(
                f"/{post_id}/comments",
                token,
                {"fields": "id,text,username,timestamp", "limit": str(max_comments)},
            )
            comments = comments_data.get("data", [])
        except SystemExit:
            comments = []

        total_comments += len(comments)
        report_lines.append(f"## [{ts}] {mtype}")
        if caption:
            report_lines.append(f"_{caption}_")
        report_lines.append(f"")
        report_lines.append(f"**댓글 수**: {len(comments)}개")
        report_lines.append("")

        if not comments:
            report_lines.append("_댓글 없음_\n")
            continue

        # Categorize and draft
        by_category: dict = {}
        for c in comments:
            text = c.get("text", "")
            username = c.get("username", "")
            category = classify_comment(text)
            by_category.setdefault(category, []).append((username, text))

        category_emoji = {
            "positive": "💚 긍정",
            "negative": "🔴 부정",
            "question": "❓ 질문",
            "spam": "🚫 스팸",
            "neutral": "⚪ 중립",
        }
        for cat, items in by_category.items():
            report_lines.append(f"### {category_emoji.get(cat, cat)} ({len(items)}개)")
            for username, text in items[:5]:
                report_lines.append(f"- @{username}: {text[:100]}")
                if action == "draft_replies":
                    draft = draft_reply(text, tone)
                    if draft:
                        report_lines.append(f"  → 답글 초안: _{draft}_")
            report_lines.append("")

    report_lines += [
        f"---",
        f"_총 {total_comments}개 댓글 분석 완료_",
    ]

    content = "\n".join(report_lines)
    report_path = os.path.join(HERE, "comments_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    _log("댓글 분석 완료!", "ok")
    print(f"   총 댓글: {total_comments}개")
    print(f"   저장: {report_path}")
    print("\n" + "=" * 60)
    print(content[:4000])


if __name__ == "__main__":
    main()
