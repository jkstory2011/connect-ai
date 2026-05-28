from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
import uuid
from datetime import datetime

# --- 1. 입력 데이터 스키마: 사용자가 제공하는 원본 데이터 ---
class AuditInputData(BaseModel):
    """
    Mini-Audit 시스템에 입력되는 핵심 트랜잭션 데이터의 표준 구조.
    Source Grounding을 위해 'Source ID' 필드를 반드시 포함해야 합니다.
    """
    transaction_id: str = Field(..., description="고유 거래 식별자")
    source_data: Dict[str, Any] = Field(..., description="데이터 원본 (예: CRM, ERP 등)") # 예: {'user_id': 123, 'amount': 500}
    # 필수 Source ID 목록: 이 값들이 누락되면 경고 발생.
    required_source_ids: List[str] = Field(..., description="데이터를 검증하는 데 필요한 모든 원본 증빙 자료의 식별자 리스트.")

# --- 2. PLV 계산 결과 스키마 ---
class LossComponent(BaseModel):
    """잠재적 손실액을 구성하는 개별 요소 (예: ESG 위반, 데이터 불일치 등)"""
    loss_type: str = Field(..., description="손실 유형") # 예: 'DataDiscrepancy', 'ESGViolation'
    calculated_value: float = Field(..., description="계산된 손실 금액")

class PLVResult(BaseModel):
    """잠재적 재무 손실액 (Potential Loss Value) 최종 결과."""
    total_plv: float = Field(..., description="총 잠재적 손실액 합계")
    risk_level: str = Field(..., description="위험 등급 (Low/Medium/High)") # High가 가장 심각
    loss_breakdown: List[LossComponent] = Field(..., description="손실 유형별 상세 내역 리스트")

# --- 3. 최종 보고서 스키마 (API 응답 구조) ---
class AuditReport(BaseModel):
    """비동기 워커가 완료 후 반환하는 최종 컨설팅 보고서의 핵심 데이터."""
    report_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="보고서 고유 ID")
    input_data_schema_checked: bool = True # 입력 스키마 유효성 검사 완료 여부
    source_grounding_check_passed: bool = True # 모든 필수 원본 자료가 확인되었는지 여부 (핵심)
    plv_result: PLVResult = Field(..., description="계산된 잠재적 재무 손실액 결과")
    audit_trail: List[str] = Field(..., description="리스크 진단 과정의 상세 감사 기록 및 근거 자료 출처.")

# --- 4. API 요청 응답 스키마 (비동기 작업 시작 시) ---
class JobStatusResponse(BaseModel):
    """작업이 접수되었음을 알리는 초기 응답."""
    job_id: str = Field(..., description="워커가 처리할 작업을 식별하는 ID")
    status: str = "Processing" # 'Processing' 또는 'Failed'
    message: str = "Mini-Audit 작업이 비동기 워커에 접수되었습니다. 잠시 후 상태를 확인해 주세요."