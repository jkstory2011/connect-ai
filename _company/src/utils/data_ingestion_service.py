from typing import List, Dict, Any
import uuid
from datetime import datetime
# 필요한 경우, 실제 데이터 모델을 임포트할 수 있습니다. (지금은 스키마 전처리만 목표)

class IngestionFailure(Exception):
    """데이터 인제스천 과정에서 발생하는 구조적 오류를 위한 커스텀 예외."""
    pass

def generate_source_grounding_url(data_source: str, record_id: str) -> str:
    """
    주어진 데이터 출처와 레코드 ID를 기반으로 표준화된 고유 URL을 생성합니다.
    실제 시스템에서는 이 함수가 S3 버킷 경로 또는 DB의 Primary Key를 받아야 합니다.
    """
    return f"https://jkstory-source/{data_source}/{record_id}"

def process_raw_data(
        raw_records: List[Dict[str, Any]], 
        data_sources: Dict[str, str], 
        calculation_params: Dict[str, float]
) -> Dict[str, Any]:
    """
    외부에서 가져온 원본 데이터를 PLV 계산 서비스가 요구하는 구조(RawDataInputSchema)로 전처리합니다.

    Args:
        raw_records: {record_id: ..., data: ...} 형태의 로우 데이터 리스트.
        data_sources: 출처 이름과 매칭되는 딕셔너리. 예: {"ERP": "erp-api", "CRM": "crm-db"}
        calculation_params: 초기 계산 파라미터 (가중치 등).

    Returns:
        PLV Calculator가 소비할 준비가 된 구조화된 데이터 딕셔너리.
    Raises:
        IngestionFailure: 전처리 과정에서 필수 정보가 누락되었을 경우 발생.
    """
    if not raw_records or not data_sources:
        raise IngestionFailure("전처리를 위해 원본 레코드와 출처 매핑이 모두 필요합니다.")

    structured_records = []
    
    for record in raw_records:
        record_id = str(record.get('id', str(uuid.uuid4()))) # ID가 없으면 UUID 생성
        source_name = record.get('source') # 원본 데이터에 출처 정보가 포함되어 있다고 가정

        if not source_name or source_name not in data_sources:
            raise IngestionFailure(f"레코드 {record_id}의 출처 '{source_name}'를 찾을 수 없습니다.")

        # 1. Source Grounding URL 생성 (가장 중요)
        source_api_key = data_sources[source_name] # API/DB 이름으로 매핑하여 URL에 사용
        grounding_url = generate_source_grounding_url(source_api_key, record_id)

        # 2. 데이터 페이로드 구조화 (실제 비즈니스 로직을 담는 부분)
        structured_records.append({
            "record_id": record_id,
            "value": record.get('amount', 0.0), # 예시 필드: 금액
            "description": record.get('desc', 'N/A'), # 예시 필드: 설명
            "source_url": grounding_url, # Source Grounding URL 명시
        })

    # 최종 Output 구조 반환 (RawDataInputSchema 형태)
    return {
        "transaction_id": "T-" + str(uuid.uuid4())[:8], # 임시 거래 ID
        "raw_records": structured_records,
        "calculation_parameters": calculation_params
    }

# 테스트를 위한 Mock Data 및 실행 예시 (이 부분은 실제로 사용자가 테스트할 코드)
if __name__ == '__main__':
    print("--- Ingestion Service Test Start ---")
    
    # 1. Mock 원본 데이터 (실제 API 호출 결과라고 가정)
    mock_raw_data = [
        {'id': 101, 'source': 'ERP', 'amount': 50000.0, 'desc': '물류비'},
        {'id': 102, 'source': 'CRM', 'amount': 15000.0, 'desc': '마케팅 비용'}
    ]

    # 2. Mock 출처 매핑 (어떤 이름이 어떤 API를 가리키는지)
    mock_data_sources = {
        "ERP": "erp-system/api",
        "CRM": "crm-db/query"
    }

    # 3. Mock 계산 파라미터
    mock_params = {"weight_factor": 0.5, "base_rate": 1.0}

    try:
        structured_data = process_raw_data(
            mock_raw_data, 
            mock_data_sources, 
            mock_params
        )
        print("\n✅ 성공적으로 구조화된 데이터 (PLV Calculator 입력용):")
        import json
        print(json.dumps(structured_data, indent=2))

    except IngestionFailure as e:
        print(f"\n❌ 전처리 실패: {e}")