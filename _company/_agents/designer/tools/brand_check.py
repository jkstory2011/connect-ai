#!/usr/bin/env python3
# version: brand_check_v1
"""Brand Check — 브랜드 색상·타이포 일관성 검증.

_company/assets/ 폴더의 이미지 파일을 스캔해 색상 팔레트를 추출하고
브랜드 가이드라인과 일치하는지 보고합니다.
이미지 분석에는 Pillow 라이브러리를 사용합니다.

config (brand_check.json):
  ASSETS_DIR       — 검사할 자산 폴더 (기본 _company/assets/)
  BRAND_COLORS     — 브랜드 주요 색상 목록 (hex, 예: #FF4444,#FFFFFF)
  COLOR_TOLERANCE  — 색상 허용 오차 (0~50, 기본 25)
  MAX_FILES        — 검사할 최대 파일 수 (기본 20)
  REPORT_PATH      — 보고서 저장 경로

Requires: pip install Pillow
"""
import os, sys, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "brand_check.json")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def _log(msg, kind="info"):
    icons = {"info": "🎨", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.strip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1: tuple, c2: tuple) -> float:
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


def extract_dominant_colors(img_path: str, n_colors: int = 5) -> list:
    try:
        from PIL import Image
    except ImportError:
        return []

    try:
        img = Image.open(img_path).convert("RGB")
        # Resize for speed
        img.thumbnail((100, 100))
        pixels = list(img.getdata())
        # Simple k-means-like: bucket into 8 bins per channel
        buckets: dict = {}
        for r, g, b in pixels:
            key = (r // 32 * 32, g // 32 * 32, b // 32 * 32)
            buckets[key] = buckets.get(key, 0) + 1
        sorted_colors = sorted(buckets.items(), key=lambda x: -x[1])
        return [k for k, _ in sorted_colors[:n_colors]]
    except Exception:
        return []


def scan_images(assets_dir: str, max_files: int) -> list:
    found = []
    for root, _, files in os.walk(assets_dir):
        for f in files:
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                found.append(os.path.join(root, f))
        if len(found) >= max_files * 3:
            break
    return found[:max_files]


def check_brand_consistency(img_path: str, brand_rgbs: list, tolerance: int) -> dict:
    dominant = extract_dominant_colors(img_path)
    if not dominant:
        return {"path": img_path, "status": "skip", "reason": "Pillow 미설치 또는 파싱 실패"}

    matches = []
    mismatches = []
    for color in dominant[:3]:  # Check top 3 dominant colors
        best_dist = min((color_distance(color, b) for b in brand_rgbs), default=999) if brand_rgbs else 999
        hex_color = "#{:02X}{:02X}{:02X}".format(*color)
        if best_dist <= tolerance or not brand_rgbs:
            matches.append(hex_color)
        else:
            mismatches.append(hex_color)

    status = "ok" if not mismatches else ("warn" if matches else "fail")
    return {
        "path": img_path,
        "status": status,
        "dominant": ["#{:02X}{:02X}{:02X}".format(*c) for c in dominant[:3]],
        "brand_matches": matches,
        "non_brand_colors": mismatches,
    }


def main():
    cfg = load_config()

    assets_dir = cfg.get("ASSETS_DIR", "").strip()
    if not assets_dir:
        # Try to find _company/assets relative to HERE
        candidate = os.path.normpath(os.path.join(HERE, "..", "..", "..", "assets"))
        if os.path.isdir(candidate):
            assets_dir = candidate
        else:
            _log("ASSETS_DIR을 설정하세요.", "warn")
            sys.exit(1)
    assets_dir = os.path.expanduser(assets_dir)

    brand_colors_raw = cfg.get("BRAND_COLORS", "")
    if isinstance(brand_colors_raw, list):
        brand_hex = brand_colors_raw
    else:
        brand_hex = [c.strip() for c in str(brand_colors_raw).split(",") if c.strip()]
    brand_rgbs = []
    for h in brand_hex:
        try:
            brand_rgbs.append(hex_to_rgb(h))
        except Exception:
            pass

    tolerance = int(cfg.get("COLOR_TOLERANCE", 25))
    max_files = int(cfg.get("MAX_FILES", 20))
    report_path = cfg.get("REPORT_PATH", os.path.join(HERE, "brand_check_report.md"))

    _log(f"자산 스캔: {assets_dir}")
    if brand_rgbs:
        _log(f"브랜드 색상: {', '.join(brand_hex)}")
    else:
        _log("브랜드 색상 미설정 — 색상 추출만 수행", "warn")

    images = scan_images(assets_dir, max_files)
    _log(f"이미지 {len(images)}개 발견")

    if not images:
        _log("이미지 파일이 없어요.", "warn")
        sys.exit(1)

    results = []
    ok_count = warn_count = fail_count = skip_count = 0
    for img in images:
        result = check_brand_consistency(img, brand_rgbs, tolerance)
        results.append(result)
        s = result["status"]
        if s == "ok": ok_count += 1
        elif s == "warn": warn_count += 1
        elif s == "fail": fail_count += 1
        else: skip_count += 1
        fname = os.path.basename(img)
        icon = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "⏭️"}.get(s, "•")
        print(f"  {icon} {fname}: {result.get('dominant', [])}")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🎨 브랜드 일관성 검사 보고서",
        f"",
        f"**검사 시간**: {now}  ",
        f"**자산 폴더**: {assets_dir}  ",
        f"**브랜드 색상**: {', '.join(brand_hex) if brand_hex else '미설정'}  ",
        f"**허용 오차**: {tolerance}",
        f"",
        f"## 요약",
        f"",
        f"| 상태 | 수 |",
        f"|---|---|",
        f"| ✅ 일치 | {ok_count} |",
        f"| ⚠️  부분 일치 | {warn_count} |",
        f"| ❌ 불일치 | {fail_count} |",
        f"| ⏭️  건너뜀 | {skip_count} |",
        f"| **합계** | **{len(results)}** |",
        f"",
        f"---",
        f"",
        f"## 파일별 결과",
        f"",
    ]
    for r in results:
        status = r["status"]
        icon = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "⏭️"}.get(status, "•")
        fname = os.path.relpath(r["path"], assets_dir)
        lines.append(f"### {icon} {fname}")
        if r.get("dominant"):
            lines.append(f"- 주요 색상: {', '.join(r['dominant'])}")
        if r.get("brand_matches"):
            lines.append(f"- 브랜드 매칭: {', '.join(r['brand_matches'])}")
        if r.get("non_brand_colors"):
            lines.append(f"- 비브랜드 색상: {', '.join(r['non_brand_colors'])}")
        if r.get("reason"):
            lines.append(f"- 메모: {r['reason']}")
        lines.append("")

    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    _log("검사 완료!", "ok")
    print(f"   ✅ {ok_count} / ⚠️  {warn_count} / ❌ {fail_count}")
    print(f"   저장: {report_path}")
    print("\n" + content[:3000])


if __name__ == "__main__":
    main()
