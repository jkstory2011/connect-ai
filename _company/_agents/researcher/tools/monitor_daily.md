# 📡 일일 모니터링 (Monitor Daily)

지정한 주제를 매일 자동 검색해 브리핑 보고서를 생성합니다.
CEO 에이전트나 YouTube 에이전트의 트렌드 파악에 활용할 수 있습니다.

## 설정 방법

| 필드 | 설명 |
|---|---|
| `TOPICS` | 모니터링할 주제 목록 (쉼표로 구분) |
| `MAX_PER_TOPIC` | 주제당 결과 수 (기본 5) |
| `REPORT_DIR` | 보고서 저장 폴더 |
| `LANG` | 검색 언어 (기본 kr-kr) |

## 출력

- `monitor_reports/monitor_YYYY-MM-DD.md` — 날짜별 브리핑
- `monitor_reports/latest.md` — 가장 최근 보고서 (항상 덮어씀)

## 자동화 설정

매일 자동 실행하려면 crontab에 추가:
```bash
0 8 * * * cd /path/to/tools && python3 monitor_daily.py
```

## 필요 패키지

```bash
pip install requests
```
