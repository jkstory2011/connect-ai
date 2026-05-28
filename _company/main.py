from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
import os

# 로컬 경로에서 PLV Calculator 임포트 (경로 확인 필요)
# 실제 프로젝트 구조에 맞게 수정이 필요할 수 있습니다.
try:
    from src.services.plv_calculator import PotentialLossCalculator
except ImportError as e:
    print(f"🚨 WARNING: Could not import plv_calculator. Ensure 'src' is in PYTHONPATH or adjust path.")
    # 개발 단계에서 임시로 Mock 클래스를 사용하거나, 정확한 경로를 찾아야 합니다.

app = FastAPI(title="JKstory Mini-Audit API", version="v1")

# 요청 바디 스키마 정의 (Source Grounding을 위한 데이터 구조)
class AuditRequest(BaseModel):
    """
    Mini-Audit 기능을 실행하기 위해 필요한 기본 데이터 세트.
    실제 운영 환경에서는 이 데이터를 받아와서 검증해야 합니다.
    """
    transaction_data: List[Dict]  # 예: [{"item_id": "A1", "quantity": 5, "unit_cost": 10}]
    source_documents: List[str]   # 근거가 되는 문서 ID 또는 경로 리스트 (Source Grounding)

class AuditResponse(BaseModel):
    """
    Audit 실행 결과. Potential Loss 값과 상세 경고 목록을 포함합니다.
    """
    potential_loss_value: float  # 산출된 잠재적 손실액 (PLV)
    risk_level: str               # 위험 등급 (Low/Medium/High)
    audit_report: Dict[str, any] # 상세 감사 보고서 내용

@app.post("/api/v1/mini-audit", response_model=AuditResponse)
async def run_mini_audit(request: AuditRequest):
    """
    요청받은 데이터를 기반으로 Potential Loss Value (PLV)를 계산하고,
    재무적 리스크 진단 보고서(Mini-Audit Report)를 생성합니다.
    """
    # 1. 로직 검증 및 초기화
    try:
        calculator = PotentialLossCalculator()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"PLV Calculator 초기화 실패: {e}")

    # 2. 핵심 계산 수행 (Potential Loss Quantification)
    try:
        # Source Grounding을 위해 모든 데이터를 전달합니다.
        plv_result = calculator.calculate_potential_loss(
            transaction_data=request.transaction_data,
            source_documents=request.source_documents
        )
    except Exception as e:
        print(f"Critical Error during PLV calculation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PLV 계산 중 내부 오류가 발생했습니다.")

    # 3. 응답 모델 구성
    return AuditResponse(
        potential_loss_value=plv_result['total_plv'],
        risk_level=plv_result['risk_level'],
        audit_report={
            "details": plv_result['report_details'],
            "data_consistency_issues": plv_result['inconsistencies']
        }
    )

# --- 💡 참고: 개발용 테스트 서버 실행 명령어 ---
# uvicorn main:app --reload