# potential_loss_service.py
"""
Mini-Audit 솔루션의 핵심 비즈니스 로직을 담는 서비스 계층입니다.
Potential Loss Value (PLV) 계산과 리스크 등급 분류를 담당합니다.

[원칙] 이 파일은 Pure Function 기반으로 설계되어, 테스트 용이성과 재사용성이 극대화됩니다.
"""

from typing import Dict, Any, TypedDict, List
import datetime

# =============================================================================
# 1. 데이터 스키마 정의 (TypedDict: API 입력 및 출력 구조 명확화)
# =============================================================================

class AuditInputData(TypedDict):
    """API 요청으로 받을 핵심 리스크 지표 데이터."""
    l_trade_discrepancy_count: int  # 무역 거래 데이터 불일치 건수
    l_esg_discrepancy_count: int   # ESG 보고서 데이터 불일치 건수
    l_data_discrepancy_count: int # 일반 데이터(운영) 불일치 건수
    avg_transaction_amount: float  # 평균 거래 금액 (계산의 기준이 되는 값)

class AuditReportSchema(TypedDict):
    """API가 최종적으로 반환해야 하는 표준화된 감사 보고서 스키마."""
    plv: float                        # 계산된 총 잠재적 손실액
    risk_level: str                   # 리스크 등급 (Low/Medium/High)
    summary: str                      # 요약 메시지 및 조치 권고 사항
    detailed_breakdown: List[Dict[str, Any]] # 각 지표별 상세 분석 결과

class PotentialLossCalculator:
    """PLV 계산 로직을 담당하는 핵심 클래스."""
    
    # 가중치는 비즈니스 의사결정 로그에 따라 확정된 상수입니다. (L_Trade > L_ESG > L_Data)
    WEIGHTS = {
        "l_trade": 0.4, # 무역 관련 리스크가 가장 높다고 가정
        "l_esg": 0.35,  # ESG는 규제 위험이 크므로 높은 가중치 부여
        "l_data": 0.25  # 일반 데이터 오류도 중요하지만 상대적으로 낮게 책정
    }

    @staticmethod
    def calculate_plv(inputs: AuditInputData) -> AuditReportSchema:
        """
        입력된 리스크 지표를 기반으로 Potential Loss Value (PLV)와 리스크 레벨을 계산합니다.
        
        Args:
            inputs: L_Trade, L_ESG, L_Data 불일치 건수 및 평균 거래액이 포함된 딕셔너리.

        Returns:
            AuditReportSchema 형식의 구조화된 보고서 데이터.
        """
        # 1. 필수 입력값 검증 (Guard Clause)
        if inputs['avg_transaction_amount'] <= 0:
            raise ValueError("평균 거래 금액(avg_transaction_amount)은 0보다 커야 합니다.")

        # 2. PLV 계산 로직 (핵심 비즈니스 로직)
        l_trade = inputs['l_trade_discrepancy_count']
        l_esg = inputs['l_esg_discrepancy_count']
        l_data = inputs['l_data_discrepancy_count']

        # Loss = (지표별 불일치 건수 * 가중치) * 평균 금액
        plv = (
            (l_trade * PotentialLossCalculator.WEIGHTS["l_trade"]) + 
            (l_esg * PotentialLossCalculator.WEIGHTS["l_esg"]) + 
            (l_data * PotentialLossCalculator.WEIGHTS["l_data"])
        ) * inputs['avg_transaction_amount']

        # 3. 리스크 레벨 및 요약 결정 로직
        if plv >= 20000:
            risk_level = "HIGH"
            summary = f"🚨 심각한 잠재적 손실 위험 감지 (PLV: {plv:,.0f}원). 즉시 모든 프로세스를 일시 중단하고 전문가의 재무 감사(Audit)를 받아야 합니다."
        elif plv >= 5000:
            risk_level = "MEDIUM" # Risk Amber Level
            summary = f"⚠️ 중간 수준의 잠재적 손실 위험 감지 (PLV: {plv:,.0f}원). 데이터 소스(Source Data)를 즉시 재검증하고, 원인 분석을 통해 리스크 지표를 최소화해야 합니다."
        else:
            risk_level = "LOW"
            summary = f"✅ 잠재적 손실 위험은 낮습니다 (PLV: {plv:,.0f}원). 정기적인 모니터링을 유지하며, 개선할 수 있는 지표를 찾아보세요."

        # 4. 상세 보고서 구성
        detailed_breakdown = [
            {"source": "L_Trade", "discrepancy_count": l_trade, "weighted_factor": PotentialLossCalculator.WEIGHTS["l_trade"], "contribution": l_trade * PotentialLossCalculator.WEIGHTS["l_trade"] * inputs['avg_transaction_amount']},
            {"source": "L_ESG", "discrepancy_count": l_esg, "weighted_factor": PotentialLossCalculator.WEIGHTS["l_esg"], "contribution": l_esg * PotentialLossCalculator.WEIGHTS["l_esg"] * inputs['avg_transaction_amount']},
            {"source": "L_Data", "discrepancy_count": l_data, "weighted_factor": PotentialLossCalculator.WEIGHTS["l_data"], "contribution": l_data * PotentialLossCalculator.WEIGHTS["l_data"] * inputs['avg_transaction_amount']},
        ]

        return AuditReportSchema(
            plv=round(plv, 2),
            risk_level=risk_level,
            summary=summary,
            detailed_breakdown=detailed_breakdown
        )


# =============================================================================
# 2. API 인터페이스 (FastAPI/Flask를 상정하여 Wrapper 구현)
# =============================================================================

def calculate_plv_endpoint(data: AuditInputData) -> Dict[str, Any]:
    """
    실제 FastAPI 엔드포인트에서 호출될 메인 함수입니다. 
    데이터 유효성 검증과 로직 실행을 담당합니다.
    
    Args:
        data: API 요청 본문(Body)으로 들어온 AuditInputData 객체.

    Returns:
        API 응답 형식의 Dictionary.
    """
    try:
        # 1. 핵심 계산 로직 호출
        report = PotentialLossCalculator.calculate_plv(data)
        
        # 2. 성공적인 결과 반환 (HTTP 200 OK에 해당)
        return {
            "status": "success",
            "message": "잠재적 손실액 계산을 완료했습니다.",
            "audit_report": report
        }

    except ValueError as e:
        # 3. 입력값 유효성 검사 실패 처리 (HTTP 400 Bad Request에 해당)
        return {
            "status": "error",
            "message": f"입력 데이터 오류: {e}",
            "audit_report": None
        }
    except Exception as e:
        # 4. 시스템 오류 처리 (HTTP 500 Internal Server Error에 해당)
        print(f"🚨 치명적 시스템 에러 발생: {e}") # 로깅 필요 지점
        return {
            "status": "error",
            "message": "서버에서 알 수 없는 오류가 발생했습니다. 관리자에게 문의해주세요.",
            "audit_report": None
        }

# =============================================================================
# 테스트 코드 (실제 사용 시에는 삭제하거나 별도 test/ 폴더로 분리)
# =============================================================================

if __name__ == '__main__':
    print("--- [테스트 1] 정상적인 Medium 리스크 시나리오 ---")
    test_data_medium: AuditInputData = {
        "l_trade_discrepancy_count": 5,  # 적정 수준의 무역 오류
        "l_esg_discrepancy_count": 10,   # 비교적 많은 ESG 오류 (중요)
        "l_data_discrepancy_count": 3,   # 일반 데이터는 약간 부족
        "avg_transaction_amount": 500.0 # 평균 거래액 500원
    }
    result = calculate_plv_endpoint(test_data_medium)
    print("결과:", result['audit_report'])

    print("\n--- [테스트 2] High 리스크 시나리오 (데이터 불일치 과다 발생) ---")
    test_data_high: AuditInputData = {
        "l_trade_discrepancy_count": 20,  # 대규모 오류
        "l_esg_discrepancy_count": 15,   # 심각한 ESG 위반
        "l_data_discrepancy_count": 10,  # 일반 데이터도 과다
        "avg_transaction_amount": 200.0 # 평균 거래액 200원
    }
    result = calculate_plv_endpoint(test_data_high)
    print("결과:", result['audit_report'])

    print("\n--- [테스트 3] 실패 시나리오 (유효성 검증 실패) ---")
    test_data_fail: AuditInputData = {
        "l_trade_discrepancy_count": 1,
        "l_esg_discrepancy_count": 1,
        "l_data_discrepancy_count": 1,
        "avg_transaction_amount": 0.0 # 오류 유발 지점
    }
    result = calculate_plv_endpoint(test_data_fail)
    print("결과:", result)

# END OF FILE