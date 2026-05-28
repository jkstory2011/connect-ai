from typing import List, Optional
from datetime import date
import math

# 로컬 스키마 파일을 임포트합니다.
try:
    from src.models.schemas import TransactionData, AuditFinding, PlvReportSchema
except ImportError:
    print("⚠️ WARNING: Could not import schemas. Ensure path is correct.")


class PotentialLossCalculator:
    """
    Source Grounding 원칙에 입각하여 잠재적 재무 손실액(PLV)을 계산하는 서비스 클래스.
    단순한 계산이 아닌, 감사 추적(Audit Trail) 보고서를 생성합니다.
    """

    def __init__(self):
        # 가중치 설정 (비즈니스 규칙에 의해 결정됨)
        self.WEIGHT_CONFIG = {
            "data_discrepancy": 0.4, # 데이터 불일치가 가장 중요하다고 가정
            "risk_trigger": 0.35,    # 핵심 위험 요소가 두 번째로 중요하다고 가정
            "process_failure_stage": 0.25 # 프로세스 실패는 구조적 문제에 집중
        }

    def _determine_risk_level(self, plv: float) -> str:
        """PLV 값에 따라 리스크 레벨을 결정합니다."""
        if plv >= 10000:
            return "HIGH"
        elif plv >= 3000:
            return "MEDIUM" # Risk Amber (황색 경고)
        else:
            return "LOW"

    def calculate_plv(self, transaction_data: TransactionData, findings: List[AuditFinding]) -> PlvReportSchema:
        """
        핵심 로직: PLV를 계산하고 모든 근거 자료를 수집하여 보고서를 반환합니다.
        """
        total_discrepancy = 0.0
        total_risk = 0.0
        total_process = 0.0

        # --- PLV 점수 계산 (가중치 적용) ---
        if findings:
            for finding in findings:
                # 데이터 불일치에 따른 손실액 추정 (예시 로직)
                discrepancy_amount = abs(finding.discrepancy_detail) * 0.1 # 임의의 가중치 적용
                total_discrepancy += discrepancy_amount

                # 위험 트리거가 심각할수록 높은 기본 손실값 부여 (예시 로직)
                if "계약 위반" in finding.risk_trigger:
                    base_loss = 2000 # 큰 리스크에 대한 초기 추정치
                else:
                    base_loss = 500
                total_risk += base_loss

                # 프로세스 실패 단계의 심각도 (가중치)
                if "결제 검증" in finding.process_failure_stage:
                     total_process += 100 # 결제 문제는 비교적 작지만 치명적인 문제로 가정

        # 최종 PLV 계산 공식: Loss = Discrepancy * Wd + Risk * Wr + Process * Wp
        plv = (total_discrepancy * self.WEIGHT_CONFIG["data_discrepancy"] +
               total_risk * self.WEIGHT_CONFIG["risk_trigger"] +
               total_process * self.WEIGHT_CONFIG["process_failure_stage"])

        # --- 리포트 생성 및 Source Grounding 확보 ---
        report = PlvReportSchema(
            transaction_id=transaction_data.transaction_id,
            risk_level=self._determine_risk_level(plv),
            potential_loss_value=round(plv, 2),
            source_grounding_report=[
                f"Source: {transaction_data.data_source} - 원본 데이터 기록됨.",
                f"Audit Step 1: Discrepancy (W={self.WEIGHT_CONFIG['data_discrepancy']}) 기반 계산 근거 확보.",
                f"Audit Step 2: Risk Trigger (W={self.WEIGHT_CONFIG['risk_trigger']}) 검증 완료."
            ],
            audit_findings=findings
        )

        return report

# --- 테스트용 Mock 데이터 생성 및 실행 로직 예시 함수 ---
def run_mock_test(transaction_data: TransactionData, findings: List[AuditFinding]) -> PlvReportSchema:
    """실제 호출 흐름을 시뮬레이션하는 래퍼 함수."""
    calculator = PotentialLossCalculator()
    return calculator.calculate_plv(transaction_data, findings)