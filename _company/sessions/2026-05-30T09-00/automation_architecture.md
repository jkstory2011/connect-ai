# ⚙️ JKstory 자동화 파이프라인 초기 시스템 아키텍처

## 1. 목표
- **최소 실행 가능**(MVP)으로 데이터 수집 → 처리 → 시각화/알림 순서
- **에이전트 간 데이터 흐름**을 명확히 정의하여 인프라와 서비스가 독립적이면서도 상호 운용 가능하도록 설계

## 2. 핵심 구성 요소
| Layer | Component | 역할 |
|-------|-----------|------|
| **Ingress** | `data_collector` (API) | 외부 API(PayPal, Shopify 등) 호출 및 웹훅 수신 |
| **Processing** | `worker_queue` (Celery + Redis) | 비동기 작업, 데이터 변환, 검증 |
| **Storage** | `db_primary` (PostgreSQL) <br> `cache_store` (Redis) | 영속적 저장, 빠른 조회 |
| **API Gateway** | `api_gateway` (FastAPI) | 내부 서비스 호출, 인증, rate‑limit |
| **Visualization** | `dashboard` (Next.js + Chart.js) | KPI 대시보드, 알림 UI |
| **Monitoring** | `prometheus` + `grafana` | 메트릭 수집, 알람 |

## 3. 데이터 흐름 (에이전트 간)
1. **Collector** → `api_gateway` POST `/tasks/collect`
2. **Gateway** → `worker_queue` (Celery task) `process_task`
3. **Worker** →  
   - 데이터 검증 & 변환 → `db_primary` 저장  
   - 필요 시 외부 API 호출 (예: 세금계산서 발행) → `api_gateway` POST `/external`
4. **Worker** → 성공 시 `cache_store`에 이벤트 키 저장
5. **Dashboard** → `api_gateway` GET `/metrics` + WebSocket (`/ws/updates`)  
   - Redis Pub/Sub에 구독해 실시간 업데이트

## 4. API 스키마 (예시)
```yaml
# POST /tasks/collect
request:
  type: object
  properties:
    source_id: string   # PayPal, Shopify 등 식별자
    payload: object     # 원시 데이터

response:
  type: object
  properties:
    task_id: string
    status: string

# GET /metrics/{source}
response:
  type: object
  properties:
    total_collected: integer
    successful: integer
    failed: integer
```

## 5. 보안 & 인증
- **JWT** 토큰 발급(내부 서비스 간)
- **API Key** 관리: Vault 또는 AWS Secrets Manager
- HTTPS + HSTS

## 6. 배포 전략
- **Docker Compose** 로 개발/테스트 환경 구성  
- CI/CD 파이프라인: GitHub Actions → Docker Hub → Kubernetes (minikube local)

## 7. 향후 확장 포인트
- **Event Bus** (Kafka) 도입 시 실시간 스트림 처리
- **Serverless** 함수(Edge, Lambda)로 비용 최적화

> 이 설계안은 **MVP** 수준이며, 이후 데이터 품질 검증과 Source Grounding 로직이 추가될 예정입니다.  
> ✅ 설계안은 `automation_architecture.md`에 저장되었습니다.