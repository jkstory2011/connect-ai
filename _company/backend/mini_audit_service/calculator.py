from typing import Dict, Any, List
from pydantic import BaseModel, field_validator, ValidationError
import math

# --- 1. 데이터 스키마 정의 (Validation) ---
class AuditInput(BaseModel):
    """Potential Loss 계산에 필요한 입력 데이터 구조를 정의합니다."""
    discrepancies: List[Dict[str, Any]]
    avg_transaction_amount: float
    system_weight_factor: float = 1.0

    @field_validator('discrepancies')
    def validate_discrepancy_list(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discrepancy 리스트의 필수 필드를 검증합니다."""
        for item in v:
            if not all(k in item for k in ['source', 'description', 'severity_score']):
                raise ValueError("각 Discrepancy 객체는 'source', 'description', 'severity_score'를 포함해야 합니다.")
        return v

    @field_validator('avg_transaction_amount')
    def validate_avg_amount(cls, v: float) -> float:
        if v < 0:
            raise ValueError("평균 거래 금액은 음수일 수 없습니다.")
        return v

# --- 2. 핵심 계산 로직 (Pure Function) ---

def calculate_potential_loss(data: AuditInput) -> Dict[str, Any]:
    """
    잠재적 손실액($)을 산출하는 핵심 비즈니스 로직입니다.
    Loss = Discrepancy Count * Weight Factor * Avg Amount
    
    Args:
        data: 유효성 검사를 통과한 AuditInput 객체.
        
    Returns:
        계산된 Potential Loss 값 및 상세 구조 정보를 담은 딕셔너리.
    """
    try:
        # A. Discrepancy Count 계산 (Discrepancies의 개수)
        discrepancy_count = len(data.discrepancies)

        if discrepancy_count == 0:
            return {
                "potential_loss": 0.0,
                "risk_level": "Low",
                "details": "진단할 구조적 취약점이 발견되지 않았습니다.",
                "source_grounding": [] # 근거 데이터가 없으므로 빈 리스트
            }

        # B. Potential Loss 계산 (핵심 공식 적용)
        loss = discrepancy_count * data.system_weight_factor * data.avg_transaction_amount
        
        # C. 위험 레벨 자동 분류 (Potential Loss Quantification)
        if loss >= 5000:
            risk_level = "High" # 재무적 위기감 극대화 구간
        elif loss >= 1000:
            risk_level = "Medium" # Risk Amber
        else:
            risk_level = "Low"

        # D. 상세 구조 및 근거 기록 (Audit Trail)
        grounding_details = [
            {"type": "Discrepancy Count", "value": discrepancy_count, "formula_role": "Count"},
            {"type": "Weight Factor", "value": data.system_weight_factor, "formula_role": "Multiplier"},
            {"type": "Average Amount", "value": data.avg_transaction_amount, "formula_role": "Base Value"}
        ]

        return {
            "potential_loss": round(loss, 2),
            "risk_level": risk_level,
            "details": f"{discrepancy_count}개의 구조적 취약점과 평균 거래액을 기반으로 추산된 잠재적 손실입니다.",
            "source_grounding": grounding_details
        }

    except Exception as e:
        # 예상치 못한 서버 레벨 오류 처리
        return {
            "potential_loss": 0.0,
            "risk_level": "Error",
            "details": f"계산 중 내부 시스템 오류가 발생했습니다: {str(e)}",
            "source_grounding": []
        }

# --- 3. 테스트용 더미 데이터 (예제) ---
DUMMY_AUDIT_DATA = AuditInput(
    discrepancies=[
        {"source": "Inventory System", "description": "실시간 재고 미동기화", "severity_score": 0.8},
        {"source": "Billing API", "description": "과거 청구 데이터 파싱 오류", "severity_score": 0.9},
    ],
    avg_transaction_amount=500.0,
    system_weight_factor=1.2 # 비즈니스 가중치 적용
).model_dump()

# [근거: Self-RAG - Potential Loss 공식 및 구조화 원칙 반영]
# [추측] 없음