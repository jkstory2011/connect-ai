#!/usr/bin/env python3
# version: feed_poster_v1
"""Feed Poster — Instagram 피드/릴스 게시 (Draft → 승인 → 게시).

자율도 레벨 2 (Draft) 기본: 게시 전 사용자 승인 파일을 생성하고 대기.
AUTO_POST=true 로 설정 시 즉시 게시 (자율도 3, 주의).

피드 이미지는 공개 URL이 필요합니다 (로컬 파일 직접 업로드는
Graph API 지원 안 함 — Cloudinary나 S3 같은 CDN 사용).

config (feed_poster.json):
  ACCESS_TOKEN      — Instagram Access Token
  INSTAGRAM_USER_ID — 계정 ID
  IMAGE_URL         — 이미지/영상 공개 URL (필수)
  CAPTION           — 캡션 (해시태그 포함)
  MEDIA_TYPE        — IMAGE | REELS | STORIES
  AUTO_POST         — "false"(기본, Draft 저장) | "true"(즉시 게시, 주의!)
  DRAFT_DIR         — Draft 저장 폴더

Requires: pip install requests
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "feed_poster.json")
ACCOUNT_PATH = os.path.join(HERE, "instagram_account.json")
GRAPH_BASE = "https://graph.instagram.com"


def _log(msg, kind="info"):
    icons = {"info": "📤", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
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


def api_post(endpoint: str, token: str, data: dict) -> dict:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)
    try:
        r = requests.post(
            f"https://graph.facebook.com/v19.0{endpoint}",
            params={"access_token": token},
            json=data,
            timeout=30,
        )
        result = r.json()
        if "error" in result:
            err = result["error"]
            _log(f"API 오류 {err.get('code')}: {err.get('message')}", "err")
            sys.exit(1)
        return result
    except SystemExit:
        raise
    except Exception as e:
        _log(f"요청 실패: {e}", "err")
        sys.exit(1)


def save_draft(caption: str, image_url: str, media_type: str, draft_dir: str) -> str:
    os.makedirs(draft_dir, exist_ok=True)
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    draft_path = os.path.join(draft_dir, f"draft_{now}.json")
    draft = {
        "status": "pending_approval",
        "media_type": media_type,
        "image_url": image_url,
        "caption": caption,
        "created_at": now,
        "instructions": "승인하려면 이 파일의 status를 'approved'로 변경 후 AUTO_POST=true로 재실행",
    }
    with open(draft_path, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
    return draft_path


def publish_post(token: str, user_id: str, image_url: str, caption: str, media_type: str) -> dict:
    _log(f"미디어 컨테이너 생성 중 ({media_type})...")

    container_data: dict = {"caption": caption}
    if media_type == "REELS":
        container_data["media_type"] = "REELS"
        container_data["video_url"] = image_url
        container_data["share_to_feed"] = True
    elif media_type == "STORIES":
        container_data["media_type"] = "STORIES"
        container_data["image_url"] = image_url
    else:
        container_data["image_url"] = image_url

    container = api_post(f"/{user_id}/media", token, container_data)
    container_id = container.get("id")
    if not container_id:
        _log("컨테이너 ID를 받지 못했어요.", "err")
        sys.exit(1)

    _log(f"게시 중 (container: {container_id})...")
    result = api_post(f"/{user_id}/media_publish", token, {"creation_id": container_id})

    return result


def main():
    cfg = load_config()
    token = cfg.get("ACCESS_TOKEN", "").strip()
    user_id = cfg.get("INSTAGRAM_USER_ID", "").strip()
    image_url = cfg.get("IMAGE_URL", "").strip()
    caption = cfg.get("CAPTION", "").strip()
    media_type = cfg.get("MEDIA_TYPE", "IMAGE").upper()
    auto_post = str(cfg.get("AUTO_POST", "false")).lower() == "true"
    draft_dir = cfg.get("DRAFT_DIR", os.path.join(HERE, "drafts"))

    if not token or not user_id:
        _log("ACCESS_TOKEN 또는 INSTAGRAM_USER_ID가 없어요.", "warn")
        _log("먼저 instagram_account.py를 실행하세요.", "info")
        sys.exit(1)

    if not image_url:
        _log("IMAGE_URL이 없어요. 게시할 이미지/영상의 공개 URL을 입력하세요.", "warn")
        _log("💡 로컬 이미지는 Cloudinary/Imgur 등에 먼저 업로드하세요.", "info")
        sys.exit(1)

    if not caption:
        _log("CAPTION이 비어있어요. 캡션을 입력하면 더 좋아요.", "warn")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if not auto_post:
        # Draft mode
        draft_path = save_draft(caption, image_url, media_type, draft_dir)
        _log("Draft 저장 완료 (아직 게시 안 됨)", "ok")
        print(f"\n{'=' * 50}")
        print(f"📝 게시 초안 (Draft)")
        print(f"{'=' * 50}")
        print(f"  미디어 타입: {media_type}")
        print(f"  이미지 URL : {image_url}")
        print(f"  캡션 미리보기:")
        print()
        print(caption[:500])
        print()
        print(f"  Draft 저장: {draft_path}")
        print(f"\n⚠️  게시하려면:")
        print(f"  1. draft 파일 확인 후 OK 이면")
        print(f"  2. feed_poster.json의 AUTO_POST를 'true'로 변경")
        print(f"  3. 다시 실행")
        print(f"{'=' * 50}")
        return

    # Auto post mode
    _log("게시 시작 (AUTO_POST=true)...", "warn")
    result = publish_post(token, user_id, image_url, caption, media_type)
    post_id = result.get("id", "unknown")

    _log("게시 완료!", "ok")
    print(f"\n{'=' * 50}")
    print(f"✅ Instagram 게시 완료")
    print(f"{'=' * 50}")
    print(f"  게시물 ID: {post_id}")
    print(f"  타입: {media_type}")
    print(f"  시간: {now}")
    print(f"{'=' * 50}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
