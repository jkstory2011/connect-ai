# 📤 피드 게시 (Feed Poster)

Instagram 피드·릴스·스토리를 Meta Graph API로 게시합니다.
기본 Draft 모드로 동작해 게시 전 확인 단계를 거칩니다.

## 게시 흐름

1. `IMAGE_URL`과 `CAPTION` 설정
2. `AUTO_POST=false`(기본)로 실행 → Draft 파일 저장
3. Draft 내용 확인
4. `AUTO_POST=true`로 변경 후 재실행 → 게시 완료

## 이미지 URL 준비

Graph API는 공개 URL이 필요합니다. 로컬 이미지 업로드 방법:
- [Cloudinary](https://cloudinary.com) (무료 플랜 있음)
- [Imgur](https://imgur.com)
- AWS S3, Firebase Storage 등

## 지원 미디어

| 타입 | 설명 | 조건 |
|---|---|---|
| IMAGE | 피드 이미지 | 비율 4:5 권장 |
| REELS | 짧은 영상 | 최대 15분, 9:16 비율 |
| STORIES | 스토리 | 9:16, 24시간 후 사라짐 |

## 필요 패키지

```bash
pip install requests
```
