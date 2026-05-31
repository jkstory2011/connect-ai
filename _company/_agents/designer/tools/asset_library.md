# 🗂️ 자산 라이브러리 (Asset Library)

`_company/assets/` 폴더를 스캔해 파일을 인덱싱하고 정리합니다.
이미지·영상·폰트·문서를 타입별로 분류하고 마크다운 카탈로그를 생성합니다.

## 작업 종류

| ACTION | 설명 |
|---|---|
| `catalog` | 전체 파일 목록 마크다운 생성 |
| `stats` | 용량·타입별 통계 |
| `organize` | 타입별 서브폴더로 정리 |

## 자동 분류 폴더

- `images/` — .png, .jpg, .webp, .svg 등
- `videos/` — .mp4, .mov, .webm 등
- `audio/` — .mp3, .wav, .m4a 등
- `docs/` — .pdf, .docx, .md 등
- `fonts/` — .ttf, .otf, .woff 등

## 주의사항

`organize` 작업은 파일을 실제로 이동합니다.
`AUTO_ORGANIZE=false`(기본)로 먼저 드라이런해서 확인하세요.

## 출력

`asset_catalog.md` — 자산 카탈로그 마크다운
