# 📊 인사이트 조회 (Insights Pull)

Instagram 비즈니스 계정의 도달·노출·팔로워 추이를 조회해 보고서로 저장합니다.

## 필수 조건

- `instagram_account.py` 먼저 실행해 계정 연결 확인

## 조회 지표

| 지표 | 설명 |
|---|---|
| reach | 도달한 고유 계정 수 |
| impressions | 총 노출 수 |
| profile_views | 프로필 방문 수 |
| follower_count | 팔로워 증감 |
| website_clicks | 웹사이트 클릭 수 |

## 필요 패키지

```bash
pip install requests
```

## 출력

`insights_report.md` — 기간별 인사이트 + 최근 게시물 성과
