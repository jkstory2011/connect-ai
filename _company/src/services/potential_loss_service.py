from typing import List, Tuple
from src.models.data_schema import AuditInputData, DataPoint, PotentialLossReport

def _calculate_risk_level(loss: float) -> str:
    """Potential Loss 규모에 따른 리스크 레벨을 결정합니다."""
    if loss >= 5000:
        return "High (🚨 즉각적 조치 필요)" # 강렬한 대비색 연상
    elif loss >= 1000:
        return "Medium (⚠️ 주의 및 검토 필요)"
    else:
        return "Low (✅ 안정적 범위 내)"

def _validate_source_grounding(data_points: List[DataPoint]) -> Tuple[bool, List[str]]:
    """Source Grounding 원칙을 체크하고 경고 목록을 반환합니다. [근거: 코다리 검증된 지식]"""
    warnings = []
    is_valid = True
    
    # 1. 모든 Source ID가 최소 길이 요구사항을 만족하는지 확인 (스키마 레벨에서 일부 처리되지만, 로직에서도 보강)
    for dp in data_points:
        if len(dp.source_id) < 3 or not dp.source_id.isalnum():
            warnings.append(f"❌ Source Grounding 위반: '{dp.source_id}'의 식별자가 너무 짧거나 비정상적입니다.")
            is_valid = False
    
    # 2. 데이터 포인트가 서로 다른 출처를 참조하는지 확인 (중복된 근거 자료 경고)
    unique_sources = set(dp.source_id for dp in data_points)
    if len(unique_sources) != len([s['source'] for s in data_points]): # 가상 체크 로직 추가
        warnings.append("⚠️ Source Redundancy: 분석에 사용된 근거 자료 간의 출처가 논리적으로 중복되거나 충돌할 가능성이 있습니다.")

    return is_valid, warnings

def calculate_potential_loss(input_data: AuditInputData) -> PotentialLossReport:
    """
    핵심 로직: 잠재적 손실액을 계산하고 리스크 보고서를 생성합니다.
    [근거: 코다리 검증된 지식 - Potential Loss 공식]
    Potential Loss = Discrepancy Count * Weight Factor * Avg Amount (이 구조를 확장)
    """
    # 1. 데이터 유효성 및 출처 검증 수행
    is_valid, audit_warnings = _validate_source_grounding(input_data.data_points)

    if not is_valid:
        # Source Grounding에 문제가 있다면 계산을 신뢰할 수 없습니다.
        return PotentialLossReport(
            potential_loss_usd=0.0, 
            risk_level="Error (🛑 데이터 출처 불분명)", 
            validation_status="Failed - Source Missing/Inconsistency",
            audit_details=audit_warnings
        )

    # 2. Potential Loss 계산 로직 수행
    total_discrepancy_count = sum(1 for dp in input_data.data_points if dp.is_discrepancy)
    sum_weighted_factor = sum(dp.weight_factor for dp in input_data.data_points)

    # Potential Loss 계산: (불일치 개수 합산 * 가중치 평균 * 평균 금액)
    potential_loss = total_discrepancy_count * sum_weighted_factor * input_data.average_amount

    # 3. 리스크 레벨 결정 및 보고서 생성
    risk_level = _calculate_risk_level(potential_loss)

    return PotentialLossReport(
        potential_loss_usd=round(potential_loss, 2),
        risk_level=risk_level,
        validation_status="Success - Source Grounded",
        audit_details=audit_warnings + ["✅ 모든 핵심 데이터는 유효한 출처를 기반으로 검증되었습니다."]
    )

# 테스트용 Mock Data (실제 API 호출 전에 로직 확인용)
mock_data = AuditInputData(
    transaction_id="TX-20260528-001",
    data_points=[
        DataPoint(value=1, weight_factor=0.5, source_id="SRC-A100", is_discrepancy=True),
        DataPoint(value=3, weight_factor=1.2, source_id="SRC-B200", is_discrepancy=False),
        DataPoint(value=0.5, weight_factor=0.8, source_id="SRC-A100", is_discrepancy=True) # 중복 출처 예시
    ],
    average_amount=2000.0
)

# 예상 계산: Discrepancy Count (2) * Weighted Factor Sum (2.5) * Avg Amount (2000) = 10,000 USD
# 이 로직을 기반으로 API를 만듭니다.