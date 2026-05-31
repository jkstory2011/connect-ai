#!/usr/bin/env python3
# version: insights_pull_v1
"""Insights Pull — Instagram 비즈니스 계정 인사이트 조회.

도달·노출·팔로워 증감·인게이지먼트를 가져와 마크다운 보고서로 저장합니다.

config (insights_pull.json):
  ACCESS_TOKEN      — instagram_account.json에서 공유 가능
  INSTAGRAM_USER_ID — 비즈니스 계정 ID
  PERIOD            — day | week | month (기본 week)
  METRICS           — 조회할 지표 (기본값 사용 권장)
  REPORT_PATH       — 보고서 저장 경로

Requires: pip install requests
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "insights_pull.json")
ACCOUNT_PATH = os.path.join(HERE, "instagram_account.json")
GRAPH_BASE = "https://graph.instagram.com"

DEFAULT_METRICS = [
    "reach", "impressions", "profile_views",
    "follower_count", "email_contacts", "website_clicks",
]


def _log(msg, kind="info"):
    icons = {"info": "📊", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    cfg = {}
    # Merge account config first (lower priority)
    if os.path.exists(ACCOUNT_PATH):
        try:
            with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    # Insights config overrides
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
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
    except Exception as e:
        _log(f"요청 실패: {e}", "err")
        sys.exit(1)


def main():
    cfg = load_config()
    token = cfg.get("ACCESS_TOKEN", "").strip()
    user_id = cfg.get("INSTAGRAM_USER_ID", "").strip()

    if not token or not user_id:
        _log("ACCESS_TOKEN 또는 INSTAGRAM_USER_ID가 없어요.", "warn")
        _log("먼저 instagram_account.py를 실행해 계정을 연결하세요.", "info")
        sys.exit(1)

    period = cfg.get("PERIOD", "week")
    metrics_cfg = cfg.get("METRICS", DEFAULT_METRICS)
    if isinstance(metrics_cfg, str):
        metrics = [m.strip() for m in metrics_cfg.split(",")]
    else:
        metrics = metrics_cfg

    report_path = cfg.get("REPORT_PATH", os.path.join(HERE, "insights_report.md"))

    _log(f"인사이트 조회 중 (기간: {period})...")

    # Fetch insights
    insights_data = {}
    # Instagram Insights endpoint
    try:
        data = api_get(
            f"/{user_id}/insights",
            token,
            {
                "metric": ",".join(metrics),
                "period": period,
            },
        )
        for item in data.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                insights_data[name] = values[-1].get("value", 0)
    except SystemExit:
        _log("일부 지표가 비즈니스 계정에서만 지원됩니다.", "warn")
        _log("기본 계정 정보로 대체합니다...", "info")

    # Also get basic account info
    account_data = api_get(
        f"/{user_id}",
        token,
        {"fields": "username,followers_count,media_count,follows_count"},
    )

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    username = account_data.get("username", "")
    followers = account_data.get("followers_count", "N/A")
    following = account_data.get("follows_count", "N/A")
    media_count = account_data.get("media_count", "N/A")

    lines = [
        f"# 📊 Instagram 인사이트 보고서",
        f"",
        f"**계정**: @{username}  ",
        f"**기간**: {period}  ",
        f"**생성 시간**: {now}",
        f"",
        f"---",
        f"",
        f"## 기본 지표",
        f"",
        f"| 지표 | 값 |",
        f"|---|---|",
        f"| 팔로워 | {followers:,} |" if isinstance(followers, int) else f"| 팔로워 | {followers} |",
        f"| 팔로잉 | {following:,} |" if isinstance(following, int) else f"| 팔로잉 | {following} |",
        f"| 게시물 수 | {media_count} |",
    ]

    if insights_data:
        lines += ["", "## 인사이트 지표", "", "| 지표 | 값 |", "|---|---|"]
        metric_labels = {
            "reach": "도달 (Reach)",
            "impressions": "노출 (Impressions)",
            "profile_views": "프로필 조회",
            "follower_count": "팔로워 증감",
            "email_contacts": "이메일 클릭",
            "website_clicks": "웹사이트 클릭",
        }
        for k, v in insights_data.items():
            label = metric_labels.get(k, k)
            lines.append(f"| {label} | {v:,} |" if isinstance(v, (int, float)) else f"| {label} | {v} |")

    # Get recent media for engagement
    try:
        media_data = api_get(
            f"/{user_id}/media",
            token,
            {
                "fields": "id,caption,media_type,timestamp,like_count,comments_count",
                "limit": "5",
            },
        )
        recent_posts = media_data.get("data", [])
        if recent_posts:
            lines += ["", "## 최근 게시물 (상위 5개)", ""]
            for post in recent_posts:
                caption = (post.get("caption", "") or "")[:60].replace("\n", " ")
                mtype = post.get("media_type", "POST")
                ts = post.get("timestamp", "")[:10]
                likes = post.get("like_count", 0)
                comments = post.get("comments_count", 0)
                lines.append(f"- [{ts}] {mtype} — 좋아요 {likes} | 댓글 {comments}")
                if caption:
                    lines.append(f"  _{caption}_")
    except Exception:
        pass

    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    _log("인사이트 조회 완료!", "ok")
    print(f"   계정: @{username}")
    print(f"   팔로워: {followers}")
    print(f"   저장: {report_path}")
    print("\n" + "=" * 60)
    print(content)


if __name__ == "__main__":
    main()
