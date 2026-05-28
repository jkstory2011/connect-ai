import pytest
from fastapi.testclient import TestClient
from src.api.endpoints import audit_router
from src.models.data_schema import AuditInputData, DataPoint

# FastAPI 테스트 클라이언트 설정
client = TestClient(audit_router.router)

def test_successful_calculation():
    """[Test Case 1] 모든 데이터가 유효하고 Source Grounding이 완벽할 때의 정상 계산 로직 검증."""
    # 성공 시나리오: 불일치 2개, 가중치 합계 3.0, 평균 금액 1000 -> 예상 PL: 6000 USD (Medium/High)
    valid_data = AuditInputData(
        transaction_id="TEST-SUCCESS",
        data_points=[
            DataPoint(value=2, weight_factor=1.5, source_id="SRC-A123", is_discrepancy=True),
            DataPoint(value=1, weight_factor=0.8, source_id="SRC-B456", is_discrepancy=False),
            DataPoint(value=3, weight_factor=0.7, source_id="SRC-C789", is_discrepancy=True)
        ],
        average_amount=1000.0
    )
    response = client.post("/calculate-potential-loss", json=valid_data.model_dump())
    assert response.status_code == 200
    report = response.json()
    # 예상 값: (2 * 1.5 + 1 * 0.8 + 3 * 0.7) / 3 * 1000 ? -> 코어 로직의 합산 방식을 따름
    # 실제 코드 기반 예측: Discrepancy Count (2) * Weighted Factor Sum (3.0) * Avg Amount (1000) = 6000 USD
    assert report["potential_loss_usd"] >= 5900 and report["potential_loss_usd"] <= 6100 # 부동소수점 오차 허용
    assert "Medium" in report["risk_level"] or "High" in report["risk_level"]
    assert "Source Grounded" in report["validation_status"]

def test_source_grounding_failure():
    """[Test Case 2] Source ID가 누락되거나 유효하지 않을 때의 실패 처리 검증."""
    # 실패 시나리오: Source ID 중 하나에 최소 길이 미달 (Source Grounding 위반)
    invalid_data = AuditInputData(
        transaction_id="TEST-FAIL-SOURCE",
        data_points=[
            DataPoint(value=1, weight_factor=0.5, source_id="S", is_discrepancy=True), # 🚨 위반 지점
            DataPoint(value=3, weight_factor=1.2, source_id="SRC-B456", is_discrepancy=False)
        ],
        average_amount=1000.0
    )
    response = client.post("/calculate-potential-loss", json=invalid_data.model_dump())
    assert response.status_code == 200 # API 자체는 성공적으로 응답하지만, 로직상 실패를 반환해야 함
    report = response.json()
    # Source Grounding 위반 시 Potential Loss는 0에 가깝거나 유효하지 않은 값으로 처리되어야 합니다.
    assert report["potential_loss_usd"] == 0.0 or "Error" in report["risk_level"]
    assert "Source Grounding 위반" in "".join(report["audit_details"])

def test_data_type_failure():
    """[Test Case 3] 필수 필드가 누락되거나 데이터 타입이 잘못되었을 때 FastAPI 레벨의 검증 테스트."""
    # 평균 금액(average_amount) 필수 값 (gt=0.0) 위반 시도
    invalid_input = {
        "transaction_id": "TEST-FAIL-TYPE",
        "data_points": [
            {"value": 1, "weight_factor": 1.0, "source_id": "SRC-OK", "is_discrepancy": False}
        ],
        "average_amount": -50.0 # 부정 값
    }
    response = client.post("/calculate-potential-loss", json=invalid_input)
    assert response.status_code == 422 # FastAPI Validation Error Code