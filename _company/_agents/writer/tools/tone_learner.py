#!/usr/bin/env python3
# version: tone_learner_v1
"""Tone Learner — 과거 글을 스캔해 톤 프로파일을 memory.md에 저장.

지정한 폴더에서 .md / .txt 파일을 읽고 어휘·문장 패턴·톤을 분석해
writer/memory.md에 "톤 프로파일" 섹션을 업데이트합니다.

config (tone_learner.json):
  SOURCE_DIR   — 분석할 과거 글 폴더 (필수)
  FILE_TYPES   — 분석할 확장자 (기본 .md,.txt)
  SAMPLE_LINES — 파일당 샘플 줄 수 (기본 50)
  MAX_FILES    — 최대 파일 수 (기본 20)
  MEMORY_PATH  — 결과 저장 위치 (기본 ../memory.md)
"""
import os, sys, json, datetime, re, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "tone_learner.json")
DEFAULT_MEMORY = os.path.join(HERE, "..", "memory.md")


def _log(msg, kind="info"):
    icons = {"info": "✍️", "ok": "✅", "warn": "⚠️ ", "err": "❌"}
    print(f"{icons.get(kind, '•')} {msg}", flush=True)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_files(source_dir: str, file_types: list, max_files: int) -> list:
    if not os.path.isdir(source_dir):
        _log(f"폴더가 없어요: {source_dir}", "err")
        sys.exit(1)

    found = []
    for root, _, files in os.walk(source_dir):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in file_types:
                found.append(os.path.join(root, f))
        if len(found) >= max_files * 3:
            break

    # Sample randomly if too many
    if len(found) > max_files:
        found = random.sample(found, max_files)
    return found


def analyze_text(texts: list) -> dict:
    combined = "\n".join(texts)
    sentences = re.split(r"[.!?。！？]\s*", combined)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return {}

    # Sentence length distribution
    lengths = [len(s) for s in sentences]
    avg_len = sum(lengths) / len(lengths) if lengths else 0

    # Tone markers (Korean)
    formal_markers = ["습니다", "입니다", "합니다", "했습니다", "됩니다"]
    casual_markers = ["해요", "예요", "이에요", "거든요", "잖아요", "이죠"]
    very_casual = ["야", "이야", "해", "됐어", "이야기", "근데", "그냥"]

    formal_count = sum(combined.count(m) for m in formal_markers)
    casual_count = sum(combined.count(m) for m in casual_markers)
    very_casual_count = sum(combined.count(m) for m in very_casual)

    total = formal_count + casual_count + very_casual_count + 1
    if formal_count / total > 0.5:
        tone_style = "격식체 (합니다/습니다)"
    elif casual_count / total > 0.3:
        tone_style = "반격식체 (해요/예요)"
    else:
        tone_style = "구어체/친근체"

    # Emoji usage
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001F9FF\U00002702-\U000027B0\U0001F600-\U0001F64F]", re.UNICODE
    )
    emoji_count = len(emoji_pattern.findall(combined))
    emoji_freq = "많음" if emoji_count > len(sentences) * 0.5 else ("중간" if emoji_count > len(sentences) * 0.1 else "적음")

    # Common words (simple)
    words = re.findall(r"[가-힣a-zA-Z]{2,}", combined)
    word_freq = Counter(words).most_common(20)

    # Sample sentences (short + punchy ones first)
    samples = sorted(sentences, key=len)[:5]

    return {
        "문체": tone_style,
        "평균_문장_길이": f"{avg_len:.0f}자",
        "이모지_사용": emoji_freq,
        "자주_쓰는_단어": [w for w, _ in word_freq if len(w) >= 2][:10],
        "샘플_문장": samples[:3],
        "분석_문장_수": len(sentences),
    }


def main():
    cfg = load_config()
    source_dir = cfg.get("SOURCE_DIR", "").strip()
    if not source_dir:
        _log("SOURCE_DIR이 비어있어요. tone_learner.json에 분석할 글 폴더를 입력하세요.", "warn")
        sys.exit(1)

    # Expand home dir
    source_dir = os.path.expanduser(source_dir)

    file_types_raw = cfg.get("FILE_TYPES", ".md,.txt")
    file_types = [t.strip().lower() for t in str(file_types_raw).split(",")]
    sample_lines = int(cfg.get("SAMPLE_LINES", 50))
    max_files = int(cfg.get("MAX_FILES", 20))
    memory_path = cfg.get("MEMORY_PATH", DEFAULT_MEMORY)
    if not os.path.isabs(memory_path):
        memory_path = os.path.join(HERE, memory_path)
    memory_path = os.path.normpath(memory_path)

    _log(f"글 스캔 중: {source_dir}")
    files = scan_files(source_dir, file_types, max_files)
    _log(f"파일 {len(files)}개 발견")

    texts = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            sample = lines[:sample_lines]
            texts.append("".join(sample))
        except Exception:
            pass

    if not texts:
        _log("읽을 수 있는 파일이 없어요.", "warn")
        sys.exit(1)

    _log(f"톤 분석 중 ({len(texts)}개 파일)...")
    profile = analyze_text(texts)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    profile_block = f"""
<!-- TONE_PROFILE_START -->
## 🎨 톤 프로파일 (자동 분석 — {now})

| 항목 | 값 |
|---|---|
| 문체 | {profile.get('문체', '미확인')} |
| 평균 문장 길이 | {profile.get('평균_문장_길이', '미확인')} |
| 이모지 사용 빈도 | {profile.get('이모지_사용', '미확인')} |
| 분석 문장 수 | {profile.get('분석_문장_수', 0):,}개 |

**자주 쓰는 단어**: {', '.join(profile.get('자주_쓰는_단어', []))}

**샘플 문장**:
{chr(10).join('- ' + s for s in profile.get('샘플_문장', []))}

_소스: {source_dir} ({len(files)}개 파일)_
<!-- TONE_PROFILE_END -->
"""

    # Update memory.md
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            existing = f.read()
        # Replace existing profile block
        if "<!-- TONE_PROFILE_START -->" in existing:
            existing = re.sub(
                r"<!-- TONE_PROFILE_START -->.*?<!-- TONE_PROFILE_END -->",
                profile_block.strip(),
                existing,
                flags=re.DOTALL,
            )
        else:
            existing = existing.rstrip() + "\n\n" + profile_block
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write(existing)
    else:
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write(f"# Writer Memory\n\n{profile_block}")

    _log("톤 프로파일 업데이트 완료!", "ok")
    print(f"   문체: {profile.get('문체', '미확인')}")
    print(f"   평균 문장 길이: {profile.get('평균_문장_길이', '미확인')}")
    print(f"   이모지: {profile.get('이모지_사용', '미확인')}")
    print(f"   저장: {memory_path}")
    print("\n" + profile_block)


if __name__ == "__main__":
    main()
