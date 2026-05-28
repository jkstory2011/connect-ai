from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import uuid
# 가상의 워커 큐 연결 라이브러리 (실제 환경에 맞게 수정 필요)
# from celery_worker import submit_job

# 로컬 개발을 위해 임시로 정의합니다. 실제로는 Redis/RabbitMQ와 연동됩니다.
def mock_submit_job(data):
    """Mock: 작업을 워커 큐에 등록하는 함수."""
    job_id = str(uuid.uuid4())
    print(f"--- [MOCK] Job {job_id} Submitted to Worker Queue.")
    return job_id

app = FastAPI(title="Mini-Audit API Gateway")

@app.post("/audit/start", response_model=JobStatusResponse)
async def start_mini_audit(input_data: dict):
    """
    사용자로부터 데이터를 받아 비동기 Mini-Audit 워크플로우를 시작합니다.
    데이터 유효성 검증을 먼저 수행하여 실패 시 즉시 피드백합니다.
    """
    try:
        # 1. 스키마 기반 데이터 검증 (가장 중요)
        validated_data = AuditInputData(**input_data)

        # 2. 워커에 작업 제출 (비동기 처리 시작)
        job_id = mock_submit_job(validated_data) # 실제로는 submit_job(validated_data) 호출

        return JobStatusResponse(job_id=job_id, status="Processing")

    except ValidationError as e:
        # 유효성 검증 실패 시 구체적인 에러 메시지 반환
        raise HTTPException(status_code=400, detail=f"입력 데이터 스키마 오류 발생. {e.errors()}")
    except Exception as e:
        print(f"An unexpected error occurred in API Gateway: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

# 참고: 실제 구현 시, 워커의 결과를 조회하는 /audit/status 엔드포인트도 필요합니다.