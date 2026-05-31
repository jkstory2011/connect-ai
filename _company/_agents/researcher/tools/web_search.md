# 🔍 웹 검색 (Web Search)

DuckDuckGo HTML 검색으로 실시간 웹 결과를 가져옵니다. API 키 없이 즉시 사용 가능.
선택적으로 Brave Search API(유료)로 전환해 더 정확한 결과를 얻을 수 있습니다.

## 설정 방법

| 필드 | 설명 |
|---|---|
| `QUERY` | 검색어 (한국어·영어 모두 가능) |
| `MAX_RESULTS` | 가져올 결과 수 (기본 10) |
| `ENGINE` | `duckduckgo` (무료 기본) 또는 `brave` |
| `BRAVE_API_KEY` | Brave 엔진 사용 시만 필요 |

## 사용 예시

1. `QUERY`에 검색어 입력 → 실행
2. 결과가 `web_search_result.md`에 저장됨
3. Researcher 에이전트가 결과를 분석·요약

## 필요 패키지

```bash
pip install requests
# 선택사항 (더 정확한 파싱):
pip install beautifulsoup4
```

## 출력

`web_search_result.md` — 검색 결과 마크다운 보고서 (제목·URL·요약 포함)
