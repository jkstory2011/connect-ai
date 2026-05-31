#!/usr/bin/env python3
# version: instagram_account_v1
"""Instagram Account — Meta Graph API 연결 확인 및 계정 정보 조회.

Meta Graph API (비즈니스 계정 전용)를 통해 연결을 검증하고
계정 기본 정보(팔로워·게시물 수·바이오)를 출력합니다.

설정 방법:
  1. Meta for Developers (developers.facebook.com)에서 앱 생성
  2. Instagram Basic Display API 또는 Instagram Graph API 활성화
  3. 비즈니스 계정에 앱 연결 후 Access Token 발급
  4. ACCESS_TOKEN과 INSTAGRAM_USER_ID를 아래에 입력

config (instagram_account.json):
  ACCESS_TOKEN      — Instagram Graph API 장기 액세스 토큰
  INSTAGRAM_USER_ID — Instagram 비즈니스 계정 ID (숫자)
  VERIFY_ONLY       — "true"면 연결 확인만 (기본 true)

Requires: pip install requests
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "instagram_account.json")
GRAPH_BASE = "https://graph.instagram.com"


def _log(msg, kind="info"):
    icons = {"info": "📷", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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
            _log("액세스 토큰이 유효한지, 비즈니스 계정인지 확인하세요.", "warn")
            _log("발급: developers.facebook.com → 내 앱 → Instagram → 토큰 발급", "info")
            sys.exit(1)
        return data
    except Exception as e:
        _log(f"요청 실패: {e}", "err")
        sys.exit(1)


def main():
    cfg = load_config()
    token = cfg.get("ACCESS_TOKEN", "").strip()
    user_id = cfg.get("INSTAGRAM_USER_ID", "").strip()

    if not token:
        _log("ACCESS_TOKEN이 비어있어요.", "warn")
        _log("발급 방법:", "info")
        _log("  1. developers.facebook.com → 내 앱 만들기", "info")
        _log("  2. Instagram Graph API 제품 추가", "info")
        _log("  3. 비즈니스 계정 연결 → 장기 토큰 발급 (60일)", "info")
        _log("  4. instagram_account.json의 ACCESS_TOKEN에 입력", "info")
        sys.exit(1)

    _log("Instagram Graph API 연결 확인 중...")

    # Get basic user info
    endpoint = f"/me" if not user_id else f"/{user_id}"
    fields = "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website"
    data = api_get(endpoint, token, {"fields": fields})

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    username = data.get("username", "unknown")
    name = data.get("name", "")
    followers = data.get("followers_count", "N/A")
    following = data.get("follows_count", "N/A")
    media_count = data.get("media_count", "N/A")
    bio = data.get("biography", "")
    website = data.get("website", "")
    actual_id = data.get("id", user_id)

    _log(f"연결 성공!", "ok")
    print(f"\n{'=' * 50}")
    print(f"📷 Instagram 계정 정보")
    print(f"{'=' * 50}")
    print(f"  사용자명  : @{username}")
    if name:
        print(f"  이름      : {name}")
    print(f"  계정 ID   : {actual_id}")
    print(f"  팔로워    : {followers:,}" if isinstance(followers, int) else f"  팔로워    : {followers}")
    print(f"  팔로잉    : {following:,}" if isinstance(following, int) else f"  팔로잉    : {following}")
    print(f"  게시물    : {media_count}")
    if bio:
        print(f"  바이오    : {bio[:100]}")
    if website:
        print(f"  웹사이트  : {website}")
    print(f"  확인 시간 : {now}")
    print(f"{'=' * 50}\n")

    # Update config with actual ID
    if not user_id and actual_id:
        cfg["INSTAGRAM_USER_ID"] = actual_id
        cfg["_username"] = username
        cfg["_last_verified"] = now
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        _log(f"계정 ID ({actual_id}) 설정에 저장됨", "ok")

    print(json.dumps({
        "status": "connected",
        "username": username,
        "user_id": actual_id,
        "followers": followers,
        "media_count": media_count,
        "verified_at": now,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
