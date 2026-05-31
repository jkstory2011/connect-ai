# 📄 페이지 가져오기 (Page Fetcher)

웹 페이지 URL에서 본문 텍스트를 추출해 마크다운으로 저장합니다.
스크립트·광고·네비게이션을 제거하고 핵심 본문만 추출. 출처 인용 포함.

## 설정 방법

| 필드 | 설명 |
|---|---|
| `URL` | 본문을 추출할 페이지 URL (필수) |
| `MAX_CHARS` | 최대 글자 수 (기본 6000) |
| `SAVE_TO` | 저장 파일명 (기본 page_fetch_result.md) |

## 필요 패키지

```bash
pip install requests
# 선택사항 (더 정확한 파싱):
pip install beautifulsoup4
```

## 출력

`page_fetch_result.md` — 제목·URL·추출 시간·본문 포함 마크다운 파일
