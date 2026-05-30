# Phase 3: 손실액 시각화 백엔드 아키텍처 초안

## 1️⃣ 목표
- **데이터 인제스트 → 통합 → 계산**  
- **Worker Queue(예: Celery + Redis)** 로 비동기 처리
- **REST API** 를 통해 **손실액 요약 & 시각화 데이터** 제공
- **자동 스케줄링** 으로 매일/주간 리포트 생성

## 2️⃣ 핵심 구성 요소
| Component | 역할 | 주요 기술 |
|-----------|------|-----------|
| **API Gateway** | 외부 요청 라우팅, 인증, rate‑limit | FastAPI + OAuth2 |
| **Worker Service** | 비동기 계산, 데이터 파이프라인 | Celery (Redis broker) + Python |
| **Data Store** | 원시/변환 데이터 저장 | PostgreSQL (TimescaleDB) |
| **Cache Layer** | 빈번 조회 캐시 | Redis |
| **Monitoring** | 작업 상태, 지표 모니터링 | Prometheus + Grafana |
| **CI/CD** | 코드 배포, 테스트 자동화 | GitHub Actions |

## 3️⃣ 데이터 흐름

```
┌─────────────────────┐
│ 1. API 호출 (GET /pl/v1/summary) │
└───────▲───────────────┘
        │
        ▼
┌─────────────────────┐   ┌───────────────────────────┐
│ 2. API Gateway      │ → │ 3. Worker Queue (Celery)   │
└───────▲───────────────┘   └─────▲─────────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────────┐   ┌───────────────────────────┐
│ 4. Data Retrieval   │ ← │ 5. Data Ingestion Job     │
└───────▲───────────────┘   └─────▼─────────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────────┐   ┌───────────────────────────┐
│ 6. PL Calculation   │ ← │ 7. Persistence (PostgreSQL)│
└───────▲───────────────┘   └─────▼─────────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────────┐   ┌───────────────────────────┐
│ 8. Cache (Redis)    │ ← │ 9. Metrics & Logs         │
└───────▲───────────────┘   └───────────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 10. API Response    │
└─────────────────────┘
```

### 세부 흐름
1. **API 호출**  
   - `/pl/v1/summary` (GET) → 인증 토큰 검증 → 요청 파라미터(날짜 범위 등)

2. **Worker Queue**  
   - API 게이트웨이에서 `Celery` task(`process_pl_summary`) 실행
   - 작업 ID 반환 → 클라이언트는 `GET /pl/v1/summary/{task_id}` 로 상태 확인

3. **Data Ingestion**  
   - `ingest_transactions` job은 외부 API(예: PayPal, Stripe)에서 과거 30일 거래를 가져와 PostgreSQL `transactions` 테이블에 저장
   - 주기적으로 `cron` 혹은 Celery beat 로 실행

4. **PL 계산**  
   - `calculate_pl` 함수는 `transactions`에서 환불/분쟁을 필터링 → `potential_loss_events`
   - 합계, 빈도, 평균 등 KPI 계산
   - 결과는 `pl_summary` 테이블에 저장

5. **Cache**  
   - 1분마다 최신 `pl_summary`를 Redis에 저장 → API 응답 지연 최소화

6. **API Response**  
   - 캐시에서 조회 → JSON 반환 (`total_pl`, `frequency`, `avg_loss`, `risk_level` 등)

## 4️⃣ Worker Queue 상세 설정

| 항목 | 설정 |
|------|------|
| **Broker** | Redis (`redis://localhost:6379/0`) |
| **Result Backend** | PostgreSQL `celery_results` 테이블 |
| **Concurrency** | 4 (CPU 코어 수에 따라 조정) |
| **Retries** | Exponential backoff, max 5 retries |
| **Health Check** | `/celery/health` endpoint |

## 5️⃣ API 명세 (OpenAPI)

```yaml
openapi: 3.0.1
info:
  title: Potential Loss API
  version: "1.0"
paths:
  /pl/v1/summary:
    get:
      summary: 손실액 요약 조회
      parameters:
        - in: query
          name: start_date
          schema:
            type: string
            format: date
        - in: query
          name: end_date
          schema:
            type: string
            format: date
      responses:
        '200':
          description: 요약 데이터 반환
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PLOutput'
  /pl/v1/summary/{task_id}:
    get:
      summary: 비동기 작업 상태 조회
      responses:
        '200':
          description: 작업 결과 반환
components:
  schemas:
    PLOutput:
      type: object
      properties:
        total_pl:
          type: number
        frequency:
          type: number
        avg_loss:
          type: number
        risk_level:
          type: string
```

## 6️⃣ 배포 & 모니터링

- **Docker Compose**: API, Celery worker, Redis, PostgreSQL, Grafana
- **Prometheus Exporter**: Celery task duration, Redis cache hit/miss
- **Alerting**: Worker 실패 >5회 → Slack 알림

## 7️⃣ 실행 예시 (CLI)

```bash
# 인제스트 작업 수동 실행
$ celery -A app.celery worker --loglevel=info

# PL 계산 작업 큐에 넣기
$ curl -X POST http://localhost:8000/pl/v1/summary?start_date=2024-05-01&end_date=2024-05-31
```

---

### 📌 참고 자료

- **Potential Loss 공식**: `Loss = Discrepancy Count * Weight Factor * Avg Amount` [근거: 2026-05-27]  
- **Risk Level 분류**: Low/Medium/High  [근거: 2026-05-27]  
- **데이터 인제스트 시나리오**: 외부 API 인증 토큰 관리, 재시도 로직  [근거: 2026-05-27]

---

> 이 초안은 **Phase 3** 목표를 달성하기 위한 첫 번째 구조적 설계입니다.  
> 다음 단계로는 **데이터 모델링**과 **Celery task 구현**을 진행합니다.