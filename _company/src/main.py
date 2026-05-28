from fastapi import FastAPI
from src.api.v1 import plv_router
# Celery 초기화 로직은 환경설정에 따라 별도로 분리해야 합니다.
app = FastAPI(title="JKstory PLV Audit API", description="Potential Loss Value (PLV) 분석 및 재무적 리스크 추산 서비스")

@app.get("/")
def read_root():
    return {"status": "OK", "service": "JKstory PLV Audit Engine Running"}

# 라우터 마운트: 핵심 API 엔드포인트를 여기에 붙입니다.
app.include_router(plv_router, prefix="/api/v1")