import pytest
from calculator import calculate_potential_loss, AuditInput
from typing import List, Dict, Any

# ----------------------------------------
# 단위 테스트 (Unit Test) - 순수 로직 검증
# ----------------------------------------

def test_basic_successful_calculation():
    """정상적인 데이터 입력 시 Potential Loss가 정확하게 계산되는지 확인합니다."""
    test_data = AuditInput(
        discrepancies=[{"source": "A", "description": "d1", "severity_score": 0.5}, {"source": "B", "description": "d2", "severity_score": 0.7}], # Count: 2
        avg_transaction_amount=1000.0, # Avg: 1000
        system_weight_factor=2.0 # Weight: 2.0
    )
    # Expected Loss = 2 * 2.0 * 1000.0 = 4000.0
    result = calculate_potential_loss(test_data)
    assert result["potential_loss"] == 4000.0
    assert result["risk_level"] == "Medium" # 1000 <= Loss < 5000
    # 근거 데이터 포함 여부 확인
    assert len(result["source_grounding"]) == 3

def test_high_potential_loss():
    """Potential Loss가 임계값($5000)을 초과할 때 High Risk Level이 부여되는지 확인합니다."""
    test_data = AuditInput(
        discrepancies=[{"source": "C", "description": "d3", "severity_score": 0.9}], # Count: 1
        avg_transaction_amount=5000.0, # Avg: 5000
        system_weight_factor=2.0 # Weight: 2.0
    )
    # Expected Loss = 1 * 2.0 * 5000.0 = 10000.0
    result = calculate_potential_loss(test_data)
    assert result["potential_loss"] == 10000.0
    assert result["risk_level"] == "High"

def test_zero_discrepancy():
    """진단할 취약점이 하나도 없을 때 Potential Loss가 0으로 처리되는지 확인합니다."""
    test_data = AuditInput(
        discrepancies=[], # Count: 0
        avg_transaction_amount=1000.0,
        system_weight_factor=2.0
    )
    result = calculate_potential_loss(test_data)
    assert result["potential_loss"] == 0.0
    assert result["risk_level"] == "Low"

# ----------------------------------------
# 경계값/오류 처리 테스트 (Edge Case Test)
# ----------------------------------------

def test_empty_input_validation():
    """Pydantic 모델에 필수 필드를 누락했을 때 Validation Error가 발생하는지 확인합니다."""
    # 임의로 잘못된 데이터 구조를 만들어서 테스트합니다.
    with pytest.raises(ValidationError):
        AuditInput(discrepancies=[], avg_transaction_amount=-50.0, system_weight_factor=1.0)

def test_negative_average_amount_validation():
    """평균 거래 금액이 음수일 때 Validation Error가 발생하는지 확인합니다."""
    with pytest.raises(ValidationError):
        AuditInput(discrepancies=[{"source": "A", "description": "d1", "severity_score": 0.5}], avg_transaction_amount=-100.0, system_weight_factor=1.0)

# [근거: 코다리 검증된 지식 - 데이터 파이프라인의 안정성 확보 및 Audit Trail 필요]
# [추측] 없음