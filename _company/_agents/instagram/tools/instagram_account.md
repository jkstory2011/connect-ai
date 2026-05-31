# 📷 Instagram 계정 연결 (Instagram Account)

Meta Graph API를 통해 Instagram 비즈니스 계정에 연결하고 기본 정보를 조회합니다.
다른 Instagram 도구(feed_poster, insights_pull 등)의 기반이 됩니다.

## 필수 조건

- **Instagram 비즈니스 계정** (개인 계정 불가)
- **Facebook 페이지와 연결** 필요
- **Meta Developer 앱** 생성 필요

## 토큰 발급 방법

1. [developers.facebook.com](https://developers.facebook.com) 접속
2. 내 앱 → 새 앱 만들기 (비즈니스 타입)
3. Instagram Graph API 제품 추가
4. 비즈니스 계정 연결
5. Graph API Explorer에서 장기 토큰 발급
6. `ACCESS_TOKEN` 필드에 입력

## 토큰 갱신

장기 토큰은 60일 유효. 만료 전 갱신:
```
GET https://graph.instagram.com/refresh_access_token
  ?grant_type=ig_refresh_token
  &access_token={현재_토큰}
```

## 필요 패키지

```bash
pip install requests
```
