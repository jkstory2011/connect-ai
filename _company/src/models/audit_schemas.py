from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

# --------------------------------------------------------------------
# ENUM & TYPE DEFINITIONS (명확한 상태 코드 정의가 필수)
# --------------------------------------------------------------------

class Status(str):
    """처리 상태 코드: Success, Warning, Error."""
    SUCCESS = "SUCCESS"
    WARNING = "WARNING" # 경고 (재무적 리스크 발생 지점 등)
    ERROR = "ERROR"     # 치명적인 오류 (데이터 파싱 실패 등)

class ProcessStep(str):
    """처리 단계: Ingestion, Validation, Calculation, Reporting."""
    INGESTION = "Ingestion"
    VALIDATION = "Validation"
    CALCULATION = "Calculation"
    REPORTING = "Reporting"

# --------------------------------------------------------------------
# CORE DATA MODELS
# --------------------------------------------------------------------

class AuditRecord(BaseModel):
    """
    하나의 처리 단계를 기록하는 최소 단위. Source Grounding을 통해 모든 주장을 뒷받침해야 함.
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC 기준 이벤트 발생 시점.")
    process_step: ProcessStep = Field(description="데이터를 처리한 단계 (Ingestion, Validation, Calculation 등).")
    status_code: Status = Field(description="해당 단계의 성공/경고/오류 상태.")
    source_grounding_url: Optional[str] = Field(None, description="이 데이터가 추출된 원본 출처 URL (필수 기록).")
    data_payload: Dict[str, Any] = Field(description="해당 단계에서 처리되거나 검증된 원본/변환된 데이터 스냅샷.")
    notes: Optional[str] = Field(None, description="담당 엔지니어 또는 시스템이 추가한 비즈니스 로직 주석.")

class PotentialLossRecord(BaseModel):
    """잠재적 손실액 (PLV)의 세부 산출 근거를 기록."""
    loss_type: str = Field(description="손실 유형 (예: Source Grounding Failure, Data Inconsistency).")
    risk_factor: float = Field(description="해당 리스크에 곱해지는 가중치 계수.")
    discrepancy_count: int = Field(description="불일치한 데이터 건수 또는 발견된 문제 항목 수.")
    calculated_amount: float = Field(description="최종 계산된 잠재적 손실액 (Loss = Count * Factor * Avg).")

class AuditReportSchema(BaseModel):
    """
    PLV 산출 전체 프로세스에 대한 최종 증명서 구조.
    이 스키마는 단순한 결과물이 아니라, '왜 이 값이 나왔는지'를 설명한다.
    """
    report_id: str = Field(description="Unique Report ID.")
    calculation_datetime: datetime = Field(default_factory=datetime.utcnow)
    final_plv_value: float = Field(description="최종 확정된 총 잠재적 손실액 (PLV).")
    risk_level: str = Field(description="Low, Medium (Risk Amber), High 중 결정된 리스크 등급.")
    summary_message: Optional[str] = Field(description="요약 진단 메시지. 재무 언어를 사용해야 함.")
    audit_trail_records: List[AuditRecord] = Field(description="전 과정의 모든 단계를 기록한 감사 추적 목록 (핵심).")
    potential_loss_breakdown: List[PotentialLossRecord] = Field(description="PLV를 구성하는 개별 리스크 항목들의 상세 분해 구조.")

# --------------------------------------------------------------------
# API INPUT SCHEMAS (사용자가 시스템에 제공해야 하는 데이터)
# --------------------------------------------------------------------

class RawDataInputSchema(BaseModel):
    """
    시스템에 입력되는 원본 데이터의 최소 스키마.
    모든 핵심 필드는 Source Grounding을 위해 출처 정보가 필요함.
    """
    transaction_id: str = Field(description="거래 고유 ID.")
    data_source: str = Field(description="데이터가 온 시스템/API 이름 (Source of Truth).")
    raw_records: List[Dict[str, Any]] = Field(description="실제 검증해야 할 원본 데이터 레코드 목록. 각 레코드는 출처와 함께 기록되어야 함.")
    calculation_parameters: Dict[str, float] = Field(description="PLV 계산에 사용될 초기 가중치 및 파라미터 맵.")

# Pydantic 모델 검증을 위해 validator를 추가합니다. (선택적)
@validator('source_grounding_url')
def check_source_url(cls, v):
    if not v:
        raise ValueError("Source Grounding URL은 필수 필드입니다.")
    return v