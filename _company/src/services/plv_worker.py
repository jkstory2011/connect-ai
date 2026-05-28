import time
from typing import Dict, Any
from datetime import datetime
from ..models.schemas import AuditInputData, PLVResult, LossComponent, AuditReport

def _calculate_potential_loss(discrepancy_count: int, weight_factor: float) -> float:
    """[핵심 로직] 데이터 불일치 건수와 가중치를 기반으로 손실액을 계산합니다. (Source Grounding 핵심)"""
    # 예시 수식: Loss = Discrepancy Count * Weight Factor * Avg Amount
    return discrepancy_count * weight_factor * 100 # 임의의 평균 금액 적용

def _perform_source_grounding(input_data: AuditInputData) -> (bool, List[str]):
    """[핵심 로직] 필수 원본 증빙 자료 누락 여부와 일관성을 검증합니다. Source Grounding의 핵심입니다."""
    missing_sources = []
    is_passed = True

    # Mock Check: 모든 required_source_ids가 실제로 시스템에 존재하는지 확인하는 로직을 시뮬레이션
    for source_id in input_data.required_source_ids:
        if not source_id.startswith("SOURCE-"): # 가상의 규칙 체크
            missing_sources.append(f"Source ID '{source_id}'는 필수 증빙 자료가 아닐 수 있습니다.")
            is_passed = False

    return is_passed, missing_sources

def run_mini_audit_workflow(input_data: AuditInputData) -> AuditReport:
    """
    Mini-Audit의 전체 워크플로우를 수행하는 메인 함수. (비동기 워커가 호출할 진입점)
    """
    start_time = datetime.now()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mini-Audit Worker 시작: {input_data.transaction_id}")

    # 1. Source Grounding 검증 (최우선 단계)
    is_grounded, grounding_warnings = _perform_source_grounding(input_data)
    audit_trail = [f"[{datetime.now()}] Stage 1: Source Grounding Check Complete."]

    # 2. 잠재적 손실액 (PLV) 계산
    plv_components: List[LossComponent] = []
    total_plv = 0.0

    # A. 데이터 불일치 기반 PLV 계산
    discrepancy_count = len([k for k, v in input_data.source_data.items() if not str(v).isdigit()]) # 예시 로직
    plv_disc = _calculate_potential_loss(discrepancy_count, 0.4)
    total_plv += plv_disc
    plv_components.append(LossComponent(loss_type="DataDiscrepancy", calculated_value=plv_disc))
    audit_trail.append(f"[{datetime.now()}] Stage 2: Data Discrepancy PLV 계산 완료 (값: {plv_disc:.2f}).")

    # B. ESG 위반 기반 PLV 계산 (Mock)
    esg_weight = 0.35
    plv_esg = discrepancy_count * esg_weight * 100 # 동일 로직 재사용 가정
    total_plv += plv_esg
    plv_components.append(LossComponent(loss_type="ESGViolation", calculated_value=plv_esg))
    audit_trail.append(f"[{datetime.now()}] Stage 2: ESG Violation PLV 계산 완료 (값: {plv_esg:.2f}).")

    # 3. 위험 등급 결정 및 최종 보고서 생성
    risk_level = "Low"
    if total_plv >= 5000:
        risk_level = "High" # 재무적 위기감 극대화
    elif total_plv >= 1000:
        risk_level = "Medium"

    final_plv_result = PLVResult(
        total_plv=round(total_plv, 2),
        risk_level=risk_level,
        loss_breakdown=plv_components
    )

    # 최종 보고서 객체 생성
    report = AuditReport(
        report_id=uuid.uuid4(),
        input_data_schema_checked=True, # 이 시점에서 항상 True로 가정
        source_grounding_check_passed=is_grounded,
        plv_result=final_plv_result,
        audit_trail=audit_trail + [f"[{datetime.now()}] Stage 3: 최종 보고서 생성 완료. 위험 등급: {risk_level}"]
    )

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mini-Audit Worker 성공적으로 종료.")
    return report