"""
hook_library.py

이 모듈은 썸네일과 자막 생성에 필요한 외부 API와의 연동을 담당합니다.
현재는 초기 구조만 제공하며, 실제 엔드포인트와 인증 로직은 나중에 채워집니다.

- Thumbnail API : POST /api/v1/thumbnail
- Subtitle API : POST /api/v1/subtitle

각 함수는 요청 파라미터를 받아서 API 호출 결과를 반환합니다.
"""

import os
import json
from typing import Dict, Any

# 환경 변수 로드 (API 키 등)
THUMBNAIL_API_URL = os.getenv("THUMBNAIL_API_URL", "https://api.example.com/v1/thumbnail")
SUBTITLE_API_URL = os.getenv("SUBTITLE_API_URL", "https://api.example.com/v1/subtitle")
API_KEY = os.getenv("API_KEY")  # 공통 키

def _post_request(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    내부 헬퍼: POST 요청 수행
    [근거: 코드 베이스에서 공통 API 호출 패턴 참고]
    """
    import requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def generate_thumbnail(video_path: str, output_dir: str = "./thumbs") -> Dict[str, Any]:
    """
    썸네일 생성 API 호출
    :param video_path: 입력 비디오 파일 경로
    :param output_dir: 썸네일 저장 디렉터리 (생성 가능)
    """
    payload = {
        "video_path": video_path,
        "output_dir": output_dir
    }
    return _post_request(THUMBNAIL_API_URL, payload)

def transcribe_subtitle(video_path: str, language: str = "ko") -> Dict[str, Any]:
    """
    자막 생성 API 호출
    :param video_path: 입력 비디오 파일 경로
    :param language: 타깃 언어 코드
    """
    payload = {
        "video_path": video_path,
        "language": language
    }
    return _post_request(SUBTITLE_API_URL, payload)

if __name__ == "__main__":
    # 예시 실행
    video = "./sample.mp4"
    print("Thumbnail 생성 시도:", generate_thumbnail(video))
    print("Subtitle 생성 시도:", transcribe_subtitle(video, "ko"))