import pytest
from src.hook_library import generate_thumbnail, transcribe_subtitle

def test_generate_thumbnail():
    # 실제 API 호출은 모킹 필요
    result = generate_thumbnail("dummy.mp4")
    assert isinstance(result, dict)

def test_transcribe_subtitle():
    result = transcribe_subtitle("dummy.mp4", "ko")
    assert isinstance(result, dict)