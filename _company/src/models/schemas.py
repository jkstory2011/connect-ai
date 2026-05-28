from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any
from datetime import date

# 1. 입력 트랜잭션 데이터 스키마 (실제 외부 API에서 들어올 가능성이 있는 원본 데이터)
class TransactionData(BaseModel):
    """외부 시스템으로부터 들어오는 기본 거래 데이터."""
    transaction_id: str = Field(description="고유한 거래 식별자")
    customer_id: str
    amount_paid: float = Field(ge=0, description="실제 지불된 금액")
    data_source: str = Field(description="데이터가 유래한 원본 시스템명 (Source of Truth)")
    transaction_date: date

# 2. 리스크 감지 및 프로세스 실패 스키마
class AuditFinding(BaseModel):
    """특정 트랜잭션에서 발견된 감사 지점."""
    risk_trigger: str = Field(description="발견된 핵심 위험 요소 (예: 데이터 불일치, 계약 조건 미준수)")
    process_failure_stage: str = Field(description="리스크가 발생한 프로세스 단계 (예: 결제 검증, 재고 연동)")
    discrepancy_detail: str = Field(description="불일치의 상세 내용")

# 3. 최종 PLV 계산 결과 보고서 스키마 (출력 포맷)
class PlvReportSchema(BaseModel):
    """최종 잠재적 손실액(PLV)과 그 근거를 포함하는 리포트 구조."""
    transaction_id: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="잠재적 손실 규모에 따른 위험 등급")
    potential_loss_value: float = Field(description="계산된 총 잠재적 재무 손실액 (PLV)")
    source_grounding_report: List[str] = Field(description="각 PLV 수치를 뒷받침하는 원본 데이터 소스 및 근거 로그 목록")
    audit_findings: List[AuditFinding] = Field(description="발견된 모든 감사 지점 목록")