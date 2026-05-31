# 📱 멀티플랫폼 변환 (Multi Platform Adapt)

하나의 스크립트나 글을 YouTube·Instagram·블로그 형식으로 자동 변환합니다.
각 플랫폼 최적 포맷(후크·캡션·해시태그·CTA 등)을 자동 적용.

## 설정 방법

| 필드 | 설명 |
|---|---|
| `SOURCE_FILE` | 원본 글 파일 경로 |
| `SOURCE_TEXT` | 직접 텍스트 입력 (파일 없을 때) |
| `PLATFORMS` | 변환 플랫폼 (youtube, instagram, blog) |
| `TITLE` | 콘텐츠 제목 |

## 출력 예시

- `콘텐츠제목_youtube_20260101_1200.md` — YouTube 스크립트
- `콘텐츠제목_instagram_20260101_1200.md` — 인스타 피드·릴스·스토리
- `콘텐츠제목_blog_20260101_1200.md` — SEO 블로그 포스트

## 사용 흐름

1. 원본 글이나 스크립트를 준비
2. `SOURCE_FILE`에 경로 입력 (또는 `SOURCE_TEXT`에 붙여넣기)
3. `TITLE`과 `PLATFORMS` 설정
4. 실행 → `adapted/` 폴더에 플랫폼별 파일 생성
