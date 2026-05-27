# Potential Loss Service Backend Skeleton
"""
Potential Loss API Endpoints and Core Logic Container.
This service is designed to handle the core business logic: 
1. Source Grounding Validation (Data Integrity Check)
2. Potential Loss Calculation (Business Rule Engine)

[NOTE]: This skeleton assumes a message queue setup (e.g., Kafka/RabbitMQ) for true stability, 
but starts with synchronous function calls for initial PoC readiness.
"""

import json
from typing import Dict, Any, List

# --- Mock Dependencies for PoC Readiness ---
class MessageQueue:
    """Mock class for Message Queue integration (e.g., Kafka Producer/Consumer)."""
    def publish_validation_request(self, payload: Dict[str, Any]):
        print("--- [MQ] Publishing Validation Request to Queue B ---")
        # In a real system, this would push to Kafka topic 'validation_requests'
        return True

class LLMClient:
    """Mock client simulating an advanced LLM API call with fallback logic."""
    def analyze_source_data(self, chunks: List[str], context_limit: int = 1024) -> str:
        print(f"--- [LLM] Analyzing {len(chunks)} chunks. Context Limit Check: {context_limit} ---")
        # Simulate successful LLM call after filtering/chunking
        if len(" ".join(chunks)) > context_limit * 0.9:
            return "Analysis successful. Potential inconsistencies identified based on provided sources."
        else:
            return "Insufficient source data for comprehensive analysis. Review required."

# --- Core Business Logic Functions ---

def validate_source_grounding(raw_data: Dict[str, Any], validation_sources: List[str]) -> Dict[str, Any]:
    """
    데이터의 출처 기반 유효성 검증 (Source Grounding).
    Input: 원본 데이터와 반드시 참조해야 할 외부 증빙 자료 목록.
    Output: 불일치 지점(Discrepancies) 및 누락 경고(Missing Sources).
    """
    print("--> Running Source Grounding Validation...")
    discrepancy_count = 0
    missing_sources = []

    # [Audit Logic Simulation]
    if 'transaction_id' not in raw_data:
        discrepancy_count += 1
        print(f"[🚨 WARNING] Data Missing: transaction_id 필드가 누락되었습니다.")
    
    for source in validation_sources:
        # 실제로는 DB/API를 호출하여 Source 존재 여부를 체크해야 함.
        if "Proof of Payment" not in source and "Contract ID" not in source:
            missing_sources.append(f"Source Missing: {source}에 대한 증빙 자료가 필요합니다.")

    return {
        "status": "Validation Complete",
        "discrepancies": [
            {"field": "transaction_id", "reason": "필수 필드 누락", "severity": "High"}
        ] if discrepancy_count > 0 else [],
        "missing_sources": missing_sources,
    }


def calculate_potential_loss(validation_report: Dict[str, Any], raw_data: Dict[str, Any]) -> float:
    """
    잠재적 재무 손실액 계산 (Potential Loss Calculation).
    Formula: Loss = Discrepancy Count * Weight Factor * Avg Amount
    """
    print("--> Calculating Potential Loss...")
    
    # 1. 불일치 지점 카운트
    discrepancy_count = len(validation_report.get("discrepancies", []))
    
    # 2. 평균 금액 (가정)
    avg_amount = raw_data.get("total_value", 0)
    
    # 3. 가중치 적용 (Weight Factor: 임의 설정 - High Severity는 높은 가중치를 갖는다 가정)
    weight_factor = 1.5 if discrepancy_count > 0 else 1.0

    potential_loss = discrepancy_count * weight_factor * avg_amount
    
    return round(potential_loss, 2)


def process_risk_assessment_pipeline(raw_data: Dict[str, Any], external_sources: List[str]) -> Dict[str, Any]:
    """
    전체 리스크 진단 파이프라인 실행 함수. (API의 핵심 로직)
    """
    print("\n================================================")
    print("🚀 Starting Potential Loss Assessment Pipeline...")

    # 1. Step 1: Source Grounding Validation
    validation_report = validate_source_grounding(raw_data, external_sources)
    
    # 2. Step 2: Potential Loss Calculation (재무적 손실액 산출)
    potential_loss_amount = calculate_potential_loss(validation_report, raw_data)

    # 3. Step 3: LLM 분석을 통한 보고서 요약 및 컨설팅 메시지 생성
    llm_client = LLMClient()
    source_chunks = [f"Discrepancy detected in {d['field']}." for d in validation_report["discrepancies"]] + \
                    [f"Missing source evidence: {s}" for s in validation_report["missing_sources"]]
    
    # Context Length를 고려하여 LLM 분석 요청 (가드 로직 적용)
    llm_summary = llm_client.analyze_source_data(source_chunks, context_limit=2048)

    final_result = {
        "status": "Success",
        "potential_loss": potential_loss_amount,
        "risk_level": "High" if potential_loss_amount > 1000 else ("Medium" if potential_loss_amount > 0 else "Low"),
        "validation_report": validation_report,
        "llm_summary": llm_summary,
        "audit_timestamp": "2026-05-28T12:00:00Z" # 실제 시간으로 대체 필요
    }

    print("✅ Pipeline Finished. Result ready for client.")
    return final_result

# --- Example Usage (Test Case) ---
if __name__ == "__main__":
    mock_data = {
        "transaction_id": "TX-20260528", # 의도적으로 누락시키거나 잘못된 값을 넣는 테스트 필요
        "total_value": 1500.00,
        "details": "..."
    }
    mock_sources = ["Contract ID: ABC-123", "Proof of Payment: XYZ"]

    # Test Case 1: Failure Simulation (Source Missing & Discrepancy)
    print("\n--- RUNNING TEST CASE 1: High Risk Scenario ---")
    result_high_risk = process_risk_assessment_pipeline(mock_data, mock_sources)
    print("\n[FINAL OUTPUT - HIGH RISK]:", json.dumps(result_high_risk, indent=2))

# End of potential_loss_service.py