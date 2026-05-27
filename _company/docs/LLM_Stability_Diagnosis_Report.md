# JKstory 시스템 안정화 보고서: LLM 호출 실패 근본 원인 진단 및 아키텍처 개선 방안

**작성일:** 2026-05-28
**관련 모듈:** Potential Loss Engine, Source Grounding Service
**목표:** 반복되는 Timeout 및 Context 길이 초과 오류의 기술적 근거를 제시하고, 안정적인 서비스 운영을 위한 아키텍처 개선 방안을 수립함.

---

## 1. 현상 분석 및 원인 진단 (Root Cause Analysis)

최근 발생한 LLM 호출 실패 사례(Timeout, Context Length Overrun 등)는 단일 오류가 아닌, 시스템의 세 가지 구조적 취약점이 복합적으로 작용한 결과입니다.

### A. [취약점 1] Context Window Overflow 및 과도한 프롬프트 길이
*   **원인:** 잠재적 리스크 진단 보고서(Audit Report)를 생성하기 위해 너무 많은 과거 로그 데이터나 방대한 외부 문서(Source Data)를 한 번에 컨텍스트로 주입하려는 경향이 있습니다. [근거: 지난 메모리 참조 - 여러 자료 통합 시도]
*   **결과:** LLM 모델의 최대 입력 길이(Context Window Limit)를 초과하여 API 호출 자체가 실패하거나, 처리 시간이 길어져 Timeout 에러가 발생합니다.

### B. [취약점 2] 비동기/순차적 API 의존성 (Synchronous Dependency Chain)
*   **원인:** 데이터 검증 $\to$ 리스크 추산 $\to$ 최종 보고서 생성의 과정이 순차적(Sequential)으로 연결되어 있습니다. 중간 단계 중 하나라도 실패하면 전체 파이프라인이 무너집니다. [근거: 일반적인 시스템 설계 패턴]
*   **결과:** 작은 결함이 누적되어 거대한 '시스템 장애'처럼 보입니다.

### C. [취약점 3] 리소스 관리 및 모델 스위칭 로직 부재 (Lack of Fallback Logic)
*   **원인:** 최고 성능의 대형 모델(GPT-4급 등)에만 의존하고, 해당 모델의 API 호출 실패 또는 비용 증가 시 대체 전략이 없습니다. [근거: 2026-05-27T14:47 로그 분석]
*   **결과:** 외부 서비스 장애나 트래픽 급증에 취약하며, 안정적인 운영을 위한 '자동 백오프(Automatic Backoff)' 및 '모델 스위칭' 로직이 필요합니다.

## 2. 아키텍처 개선 방안 (Proposed Solution)

진단된 세 가지 문제점을 해결하기 위해 다음의 구조적 개선을 제안합니다.

### A. [해결책 1] 지식 검색 증강 생성(RAG) 기반 컨텍스트 청킹 및 필터링
*   **개선 내용:** 모든 Source Data를 한 번에 주입하는 대신, **사용자의 질문/요청과 가장 관련성 높은 핵심 조각(Chunk)**만을 임베딩 벡터 검색을 통해 선별적으로 가져와 컨텍스트로 제공해야 합니다. (Vector Database 활용 필수)
*   **구현 목표:** Context Window Overflow 방지 및 비용 효율화.

### B. [해결책 2] 비동기 메시징 기반 파이프라인 재설계 (Asynchronous Workflow)
*   **개선 내용:** 모든 API 호출을 독립적인 'Task'로 분리하고, RabbitMQ 또는 Kafka 같은 **메시지 큐(Message Queue)**를 도입합니다.
    1.  `[API Gateway]` 요청 수신 $\to$ 메시지 발행 (Queue A).
    2.  `[Validator Service]`가 비동기적으로 데이터를 검증하고 결과를 다음 큐에 발행 (Queue B).
    3.  `[Potential Loss Engine]`이 Queue B의 결과만 받아 로직 수행 및 최종 보고서를 생성합니다.
*   **효과:** 한 컴포넌트의 실패가 전체 시스템을 마비시키는 것을 방지하며, 병렬 처리가 가능해져 속도와 안정성이 극대화됩니다.

### C. [해결책 3] 다중 모델(Multi-Model) 백업 및 회복 메커니즘 구현
*   **개선 내용:** LLM 호출 시 최우선으로 대형 모델을 시도하되, Timeout/Error 발생 시 **지연 시간과 Context Length를 고려하여 자동으로 중소형 대체 모델(예: GPT-3.5 Turbo $\to$ Claude Haiku)로 전환**하는 로직을 구현해야 합니다. (Circuit Breaker Pattern 적용)
*   **기술 요구사항:** 재시도 횟수, 지연 시간 증가 등을 Exponential Backoff 방식으로 제어하여 외부 서비스 과부하를 방지합니다.

## 3. 개발 우선순위 요약
1.  메시지 큐 도입 (Kafka/RabbitMQ).
2.  RAG 기반 Context 필터링 모듈 구현.
3.  LLM 호출에 Circuit Breaker 및 Multi-Model Fallback 로직 적용.