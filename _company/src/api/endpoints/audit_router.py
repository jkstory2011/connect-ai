from fastapi import APIRouter, HTTPException, status
from src.models.data_schema import AuditInputData, PotentialLossReport
from src.services.potential_loss_service import calculate_potential_loss

# 라우터 정의: API 엔드포인트의 역할 분리 (Single Responsibility Principle)
router = APIRouter(prefix="/v1/audit", tags=["Risk Assessment"])

@router.post("/calculate-potential-loss", response_model=PotentialLossReport, summary="잠재적 재무 손실액 측정 및 리스크 진단")
async def calculate_pl(data: AuditInputData):
    """
    입력된 데이터를 기반으로 Potential Loss를 계산하고 리스크 보고서를 생성합니다.
    Source Grounding 원칙에 따라 데이터 유효성을 검증하며, 그 결과를 반환합니다.
    """
    try:
        report = calculate_potential_loss(data)
        return report
    except Exception as e:
        # 예상치 못한 시스템 오류 발생 시 처리 (Fail-safe Mechanism)
        print(f"🚨 Critical Error during PL calculation: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="잠재적 손실액 계산 중 시스템 오류가 발생했습니다. 로그를 확인해주세요."
        )

# 테스트용 파일 구조 (별도 실행 권장)