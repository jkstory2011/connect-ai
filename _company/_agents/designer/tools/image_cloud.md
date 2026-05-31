# 🎨 클라우드 이미지 생성 (Image Cloud)

DALL-E 3 또는 Stable Diffusion으로 텍스트 프롬프트에서 이미지를 생성합니다.
유튜브 썸네일, 인스타 피드, 브랜드 자산 생성에 활용.

## 엔진 비교

| 엔진 | 품질 | 속도 | 비용 | API 키 |
|---|---|---|---|---|
| DALL-E 3 | ⭐⭐⭐⭐⭐ | 중간 | $0.04~0.12/장 | OpenAI |
| DALL-E 2 | ⭐⭐⭐ | 빠름 | $0.02/장 | OpenAI |
| Stability AI | ⭐⭐⭐⭐ | 빠름 | $0.003/step | Stability |

## 프롬프트 팁

- 영어로 구체적으로 작성할수록 품질이 높아집니다
- 스타일 키워드 추가: `cinematic, 8K, ultra-realistic, minimal`
- 인스타용: `9:16 aspect ratio, mobile optimized`
- 썸네일용: `eye-catching, bold text space, YouTube thumbnail style`

## 필요 패키지

```bash
# DALL-E 사용 시:
pip install openai requests

# Stability AI 사용 시:
pip install requests
```

## 출력

`~/connect-ai-images/img_[프롬프트]_[날짜].png`
