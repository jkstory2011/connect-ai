from pydantic import BaseModel, Field, PositiveFloat
from typing import List, Optional

class DataPoint(BaseModel):
    """개별 데이터 지점의 구조체. Source Grounding을 위해 출처를 포함해야 함."""
    value: float = Field(..., description="데이터 값 (예: 누락된 항목 수)")
    weight_factor: float = Field(..., description="가중치 계수")
    source_id: str = Field(..., min_length=3, description="필수 원본 증빙 자료의 식별자 (Source of Truth).")
    is_discrepancy: bool = Field(False, description="데이터 불일치 여부.")

class AuditInputData(BaseModel):
    """잠재적 손실액 계산을 위한 전체 입력 데이터 스키마."""
    transaction_id: str = Field(..., description="트랜잭션 식별자 (고유해야 함).")
    data_points: List[DataPoint] = Field(..., min_length=1, description="분석에 사용될 모든 DataPoint 목록.")
    average_amount: float = Field(..., gt=0.0, description="평균 금액 (Positive Float).")

class PotentialLossReport(BaseModel):
    """API 응답 스키마."""
    potential_loss_usd: float = Field(..., description="계산된 잠재적 손실액 ($).")
    risk_level: str = Field(..., description="리스크 레벨 (Low/Medium/High).")
    validation_status: str = Field(..., description="데이터 유효성 검증 상태.")
    audit_details: List[str] = Field(..., description="발견된 데이터 불일치 및 Source Grounding 관련 상세 경고 목록.")