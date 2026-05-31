#!/usr/bin/env python3
# version: asset_library_v1
"""Asset Library — _company/assets/ 자동 정리·태깅.

자산 폴더를 스캔해 파일 목록을 인덱싱하고,
타입별·날짜별로 정리된 마크다운 카탈로그를 생성합니다.
필요하면 하위 폴더로 자동 분류도 수행합니다.

config (asset_library.json):
  ASSETS_DIR   — 관리할 자산 폴더 (기본 _company/assets/)
  ACTION       — catalog | organize | stats
  AUTO_ORGANIZE — "true"이면 파일 타입별 폴더로 자동 이동 (기본 false)
  CATALOG_PATH — 카탈로그 저장 경로

Actions:
  catalog  — 파일 목록 + 태그 마크다운 생성
  organize — 타입별 서브폴더로 정리 (images/, videos/, docs/)
  stats    — 용량·타입별 통계
"""
import os, sys, json, datetime, shutil, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "asset_library.json")

CATEGORY_MAP = {
    "images": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg", ".tiff"},
    "videos": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    "audio": {".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg"},
    "docs": {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md"},
    "fonts": {".ttf", ".otf", ".woff", ".woff2"},
    "data": {".json", ".csv", ".xml", ".yaml", ".yml"},
}


def _log(msg, kind="info"):
    icons = {"info": "🗂️", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_category(ext: str) -> str:
    ext = ext.lower()
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    return "misc"


def scan_assets(assets_dir: str) -> list:
    files = []
    for root, dirs, fnames in os.walk(assets_dir):
        # Skip hidden and system folders
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in fnames:
            if f.startswith("."):
                continue
            full = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            try:
                stat = os.stat(full)
                files.append({
                    "path": full,
                    "name": f,
                    "rel": os.path.relpath(full, assets_dir),
                    "ext": ext,
                    "category": get_category(ext),
                    "size": stat.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                })
            except Exception:
                pass
    return sorted(files, key=lambda x: x["modified"], reverse=True)


def do_catalog(files: list, assets_dir: str, catalog_path: str):
    by_cat = defaultdict(list)
    for f in files:
        by_cat[f["category"]].append(f)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    total_size = sum(f["size"] for f in files) / (1024 * 1024)

    lines = [
        f"# 🗂️ 자산 라이브러리 카탈로그",
        f"",
        f"**생성 시간**: {now}  ",
        f"**자산 폴더**: {assets_dir}  ",
        f"**총 파일**: {len(files)}개 | **총 용량**: {total_size:.1f} MB",
        f"",
        f"---",
        f"",
    ]

    cat_emoji = {
        "images": "🖼️", "videos": "🎬", "audio": "🎵",
        "docs": "📄", "fonts": "🔤", "data": "📊", "misc": "📦"
    }
    for cat, items in sorted(by_cat.items()):
        emoji = cat_emoji.get(cat, "📁")
        cat_size = sum(f["size"] for f in items) / 1024
        lines.append(f"## {emoji} {cat.capitalize()} ({len(items)}개, {cat_size:.0f} KB)")
        lines.append("")
        lines.append("| 파일명 | 크기 | 수정일 |")
        lines.append("|---|---|---|")
        for f in items[:50]:
            size_kb = f["size"] / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            lines.append(f"| `{f['rel']}` | {size_str} | {f['modified']} |")
        if len(items) > 50:
            lines.append(f"| _...외 {len(items) - 50}개_ | | |")
        lines.append("")

    content = "\n".join(lines)
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(content)
    _log(f"카탈로그 생성: {catalog_path}", "ok")
    return content


def do_stats(files: list):
    by_cat = defaultdict(list)
    for f in files:
        by_cat[f["category"]].append(f)

    total_size = sum(f["size"] for f in files)
    lines = ["## 📊 자산 통계\n"]
    lines.append(f"- 총 파일: {len(files)}개")
    lines.append(f"- 총 용량: {total_size / (1024*1024):.1f} MB\n")

    for cat, items in sorted(by_cat.items(), key=lambda x: -sum(f["size"] for f in x[1])):
        cat_size = sum(f["size"] for f in items) / 1024
        pct = sum(f["size"] for f in items) / total_size * 100 if total_size > 0 else 0
        lines.append(f"- {cat}: {len(items)}개 ({cat_size:.0f} KB, {pct:.1f}%)")

    return "\n".join(lines)


def do_organize(files: list, assets_dir: str, dry_run: bool = False):
    moved = 0
    for f in files:
        cat = f["category"]
        if cat == "misc":
            continue
        target_dir = os.path.join(assets_dir, cat)
        current_dir = os.path.dirname(f["path"])
        # Don't move files already in their category folder
        if os.path.basename(current_dir) == cat:
            continue
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f["name"])
        if os.path.exists(target_path):
            # Avoid overwrite
            base, ext = os.path.splitext(f["name"])
            target_path = os.path.join(target_dir, f"{base}_{datetime.datetime.now().strftime('%H%M%S')}{ext}")
        if not dry_run:
            shutil.move(f["path"], target_path)
        _log(f"  {f['name']} → {cat}/", "ok")
        moved += 1
    return moved


def main():
    cfg = load_config()
    assets_dir = cfg.get("ASSETS_DIR", "").strip()
    if not assets_dir:
        candidate = os.path.normpath(os.path.join(HERE, "..", "..", "..", "assets"))
        if os.path.isdir(candidate):
            assets_dir = candidate
        else:
            _log("ASSETS_DIR을 설정하세요.", "warn")
            sys.exit(1)
    assets_dir = os.path.expanduser(assets_dir)

    if not os.path.isdir(assets_dir):
        _log(f"폴더가 없어요: {assets_dir}", "err")
        sys.exit(1)

    action = cfg.get("ACTION", "catalog").lower()
    auto_organize = str(cfg.get("AUTO_ORGANIZE", "false")).lower() == "true"
    catalog_path = cfg.get("CATALOG_PATH", os.path.join(HERE, "asset_catalog.md"))

    _log(f"자산 스캔: {assets_dir}")
    files = scan_assets(assets_dir)
    _log(f"파일 {len(files)}개 발견")

    if action == "catalog":
        content = do_catalog(files, assets_dir, catalog_path)
        print("\n" + content[:4000])

    elif action == "stats":
        stats = do_stats(files)
        _log("통계 생성 완료", "ok")
        print("\n" + stats)

    elif action == "organize":
        if not auto_organize:
            _log("AUTO_ORGANIZE=false → 드라이런 모드 (실제 이동 없음)", "warn")
            moved = do_organize(files, assets_dir, dry_run=True)
            _log(f"이동 예정 파일: {moved}개 (실행하려면 AUTO_ORGANIZE=true)", "warn")
        else:
            _log("파일 정리 시작 (되돌리기 어려움 — 백업 권장)", "warn")
            moved = do_organize(files, assets_dir, dry_run=False)
            _log(f"정리 완료: {moved}개 이동됨", "ok")
            # Regenerate catalog after organizing
            files = scan_assets(assets_dir)
            do_catalog(files, assets_dir, catalog_path)
    else:
        _log(f"알 수 없는 ACTION: {action}. catalog/organize/stats 중 선택.", "warn")
        sys.exit(1)


if __name__ == "__main__":
    main()
