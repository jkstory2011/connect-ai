#!/usr/bin/env python3
# version: image_cloud_v1
"""Image Cloud — DALL-E 3 / Stable Diffusion API 이미지 생성.

OpenAI DALL-E 3 (기본) 또는 Stable Diffusion API로
텍스트 프롬프트에서 이미지를 생성하고 로컬에 저장합니다.

config (image_cloud.json):
  OPENAI_API_KEY — OpenAI API 키 (DALL-E 3용)
  PROMPT         — 이미지 생성 프롬프트 (영어 권장)
  NEGATIVE_PROMPT — 제외할 요소 (SD 전용)
  ENGINE         — dalle3 | dalle2 | stability
  STABILITY_KEY  — Stability AI API 키 (engine=stability 때)
  SIZE           — 이미지 크기 (dalle3: 1024x1024 등)
  QUALITY        — standard | hd (DALL-E 3 전용)
  OUTPUT_DIR     — 저장 폴더 (기본 ~/connect-ai-images/)
  STYLE          — vivid | natural (DALL-E 3 전용)

Requires: pip install requests openai (openai는 dalle 사용 시)
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "image_cloud.json")
DEFAULT_OUTPUT = os.path.expanduser("~/connect-ai-images")


def _log(msg, kind="info"):
    icons = {"info": "🎨", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_dalle(api_key: str, prompt: str, engine: str, size: str, quality: str, style: str) -> str:
    try:
        import openai
    except ImportError:
        _log("openai 미설치. pip install openai", "err")
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    model = "dall-e-3" if engine == "dalle3" else "dall-e-2"

    _log(f"{model} 이미지 생성 중...")
    kwargs: dict = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }
    if model == "dall-e-3":
        kwargs["quality"] = quality
        kwargs["style"] = style

    try:
        response = client.images.generate(**kwargs)
        image_url = response.data[0].url
        revised_prompt = getattr(response.data[0], "revised_prompt", prompt)
        return image_url, revised_prompt
    except openai.OpenAIError as e:
        _log(f"OpenAI API 오류: {e}", "err")
        sys.exit(1)


def generate_stability(api_key: str, prompt: str, negative_prompt: str, size: str) -> bytes:
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)

    # Parse size
    match = re.match(r"(\d+)x(\d+)", size)
    width, height = (1024, 1024)
    if match:
        width, height = int(match.group(1)), int(match.group(2))

    _log("Stability AI 이미지 생성 중...")
    try:
        r = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "image/png",
            },
            json={
                "text_prompts": [
                    {"text": prompt, "weight": 1.0},
                    {"text": negative_prompt, "weight": -1.0} if negative_prompt else None,
                ],
                "width": width,
                "height": height,
                "steps": 30,
                "cfg_scale": 7.0,
            },
            timeout=60,
        )
        if r.status_code != 200:
            _log(f"Stability API 오류 {r.status_code}: {r.text[:200]}", "err")
            sys.exit(1)
        return r.content
    except Exception as e:
        _log(f"요청 실패: {e}", "err")
        sys.exit(1)


def download_image(url: str, save_path: str):
    try:
        import requests
    except ImportError:
        _log("requests 미설치. pip install requests", "err")
        sys.exit(1)
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        _log(f"이미지 다운로드 실패: {e}", "err")
        sys.exit(1)


def main():
    cfg = load_config()
    prompt = cfg.get("PROMPT", "").strip()
    if not prompt:
        _log("PROMPT가 비어있어요. 이미지 설명을 입력하세요.", "warn")
        _log("예: A serene Korean mountain landscape at sunrise, ultra-realistic, 8K", "info")
        sys.exit(1)

    engine = cfg.get("ENGINE", "dalle3").lower()
    negative_prompt = cfg.get("NEGATIVE_PROMPT", "").strip()
    size = cfg.get("SIZE", "1024x1024")
    quality = cfg.get("QUALITY", "standard")
    style = cfg.get("STYLE", "vivid")
    output_dir = cfg.get("OUTPUT_DIR", DEFAULT_OUTPUT)
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = re.sub(r"[^\w가-힣\-]", "_", prompt[:30])
    filename = f"img_{safe_prompt}_{now}.png"
    save_path = os.path.join(output_dir, filename)

    _log(f"엔진: {engine.upper()} | 크기: {size}")
    _log(f"프롬프트: {prompt[:80]}")

    if engine in ("dalle3", "dalle2"):
        api_key = cfg.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            _log("OPENAI_API_KEY가 없어요.", "warn")
            _log("발급: platform.openai.com/api-keys", "info")
            sys.exit(1)
        image_url, revised_prompt = generate_dalle(api_key, prompt, engine, size, quality, style)
        _log("다운로드 중...")
        download_image(image_url, save_path)
        if revised_prompt != prompt:
            _log(f"수정된 프롬프트: {revised_prompt[:100]}", "info")

    elif engine == "stability":
        api_key = cfg.get("STABILITY_KEY", "").strip()
        if not api_key:
            _log("STABILITY_KEY가 없어요.", "warn")
            _log("발급: platform.stability.ai", "info")
            sys.exit(1)
        image_data = generate_stability(api_key, prompt, negative_prompt, size)
        with open(save_path, "wb") as f:
            f.write(image_data)
    else:
        _log(f"알 수 없는 엔진: {engine}", "err")
        sys.exit(1)

    file_size = os.path.getsize(save_path) / 1024

    _log("이미지 생성 완료!", "ok")
    print(f"\n{'=' * 50}")
    print(f"🎨 이미지 생성 결과")
    print(f"{'=' * 50}")
    print(f"  엔진: {engine.upper()}")
    print(f"  크기: {size}")
    print(f"  파일: {filename}")
    print(f"  용량: {file_size:.1f} KB")
    print(f"  저장: {save_path}")
    print(f"{'=' * 50}")

    # Update config with last output
    cfg["_last_output"] = save_path
    cfg["_last_prompt"] = prompt
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
