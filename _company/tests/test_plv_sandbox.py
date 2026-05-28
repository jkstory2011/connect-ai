import pytest
from datetime import date
# 로컬 스키마와 서비스 모듈을 임포트합니다.
from src.models.schemas import TransactionData, AuditFinding, PlvReportSchema
from src.services.plv_calculator import PotentialLossCalculator

@pytest.fixture(scope="module")
def calculator():
    """테스트를 위한 PLV Calculator 인스턴스를 제공합니다."""
    return PotentialLossCalculator()

# ======================================================
# 🧪 테스트 시나리오 정의 (최소 5개 케이스)
# ======================================================

def test_scenario_01_normal_low_risk(calculator):
    """[Low Risk] 모든 데이터가 정상적이고 리스크가 거의 없는 경우."""
    mock_data = TransactionData(
        transaction_id="TXN-GOOD-001", 
        customer_id="CUST-A", 
        amount_paid=500.0, 
        data_source="ERP_System", 
        transaction_date=date(2026, 5, 1)
    )
    mock_findings = [] # 발견된 리스크 없음

    report = calculator.calculate_plv(mock_data, mock_findings)
    
    # 검증 포인트: PLV가 매우 낮고, 위험 레벨이 LOW여야 함.
    assert report.risk_level == "LOW"
    assert report.potential_loss_value < 500 # 아주 작은 값이어야 함

def test_scenario_02_medium_warning_risk(calculator):
    """[Medium Risk/Risk Amber] 데이터 불일치가 발견되어 중간 수준의 리스크가 발생한 경우."""
    mock_data = TransactionData(
        transaction_id="TXN-WARN-002", 
        customer_id="CUST-B", 
        amount_paid=800.0, 
        data_source="CRM_System", 
        transaction_date=date(2026, 5, 10)
    )
    mock_findings = [
        AuditFinding(
            risk_trigger="데이터 불일치 (배송지 주소)", 
            process_failure_stage="주문 검증", 
            discrepancy_detail="원래 기록된 주소와 현재 시스템 주소가 다름." # 이 값이 계산에 사용됨
        )
    ]

    report = calculator.calculate_plv(mock_data, mock_findings)
    
    # 검증 포인트: PLV가 Medium 레벨 범위(3000 이상 10000 미만)로 잡혀야 함.
    assert report.risk_level == "MEDIUM"
    assert report.potential_loss_value >= 3000

def test_scenario_03_high_severe_risk(calculator):
    """[High Risk] 계약 위반 등 치명적인 리스크가 발생하여 최고 수준의 PLV가 추산된 경우."""
    mock_data = TransactionData(
        transaction_id="TXN-HIGH-003", 
        customer_id="CUST-C", 
        amount_paid=12000.0, 
        data_source="Legacy_System", 
        transaction_date=date(2026, 5, 15)
    )
    mock_findings = [
        AuditFinding( # 핵심 리스크 트리거를 포함하여 PLV 증폭
            risk_trigger="계약 위반 (가격 정책 미준수)", 
            process_failure_stage="최종 승인", 
            discrepancy_detail="할인율 초과 적용 의심." 
        ),
        AuditFinding(
            risk_trigger="데이터 불일치 (재고 수량)", 
            process_failure_stage="출고 검증", 
            discrepancy_detail="실제 재고와 시스템 기록의 차이 발생."
        )
    ]

    report = calculator.calculate_plv(mock_data, mock_findings)
    
    # 검증 포인트: PLV가 High 레벨 범위(10000 이상)로 잡혀야 함.
    assert report.risk_level == "HIGH"
    assert report.potential_loss_value >= 10000

def test_scenario_04_multiple_findings_consistency(calculator):
    """여러 개의 리스크 지점을 가진 경우, 모든 근거가 보고서에 기록되는지 확인."""
    mock_data = TransactionData(
        transaction_id="TXN-MULTI-004", 
        customer_id="CUST-D", 
        amount_paid=1500.0, 
        data_source="Hybrid_System", 
        transaction_date=date(2026, 5, 20)
    )
    mock_findings = [
        AuditFinding("A", "P1", "D1"), # 가짜 값 사용
        AuditFinding("B", "P2", "D2")
    ]

    report = calculator.calculate_plv(mock_data, mock_findings)
    
    # 검증 포인트: 발견된 감사 지점의 개수와 리포트 스키마에 모두 포함되어야 함.
    assert len(report.audit_findings) == 2
    assert report.source_grounding_report[1] in "Audit Step 2" # 로직 흐름 추적이 필수

def test_scenario_05_minimal_input(calculator):
    """최소한의 입력값만으로도 구조적 무결성을 유지하는지 확인."""
    mock_data = TransactionData(
        transaction_id="TXN-MIN-005", 
        customer_id="CUST-E", 
        amount_paid=1.0, 
        data_source="Minimal_Test", 
        transaction_date=date(2026, 5, 25)
    )
    mock_findings = [
        AuditFinding("A", "P1", "D1")
    ]

    report = calculator.calculate_plv(mock_data, mock_findings)
    
    # 검증 포인트: 로직은 실행되지만, PLV는 극히 낮거나 중간 정도여야 함 (경고 수준).
    assert report.risk_level != "LOW" # 최소한의 리스크가 감지되어야 함