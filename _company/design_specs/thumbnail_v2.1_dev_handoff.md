# 🎨 JKstory Thumbnail Design System V2.1 (Developer Handoff)

**목표:** [3PL 물류] 리스크 관리 콘텐츠에 최적화된, 자동화 파이프라인 구동을 위한 최종 시각적 요구사항 명세서.
**버전:** 2.1 (Dev Ready)
**기준 스크립트:** '데이터 불일치' 및 '잠재적 손실액(Potential Loss)' 강조.

---

## I. 🖼️ 기본 레이아웃 구조 (Global Layout & Structure)
*   **비율:** 16:9 (YouTube Thumbnail 표준)
*   **배경 원칙:** 복잡한 물류/데이터 흐름 다이어그램을 배경 패턴으로 사용하되, 전반적으로 어둡고 신뢰감 있는 분위기 유지. [근거: Self-RAG]
*   **전체 구성 요소 (Layering):**
    1.  **L0 (Background Layer):** 희미한 물류/데이터 연결망 다이어그램 패턴. `#1A2B38` 계열의 Dark Mode 배경.
    2.  **L1 (Impact Area - Loss):** 가장 중요한 메시지(잠재적 손실액)를 배치하는 전면 영역. 경고색(`Risk Amber`) 사용 필수.
    3.  **L2 (Solution/Core Message):** JKstory의 해결책 및 핵심 가치 제안을 배치하는 중앙 영역. 신뢰색(`Security Blue`) 사용 필수.
    4.  **L3 (Text Overlay):** 제목, 서브 헤드라인 등 텍스트 레이어. 최소한의 정보만 크고 임팩트 있게 처리.

## II. 📊 데이터-비주얼 매핑 규칙 (Data-to-Visual Mapping)
썸네일은 **반드시 다음 JSON 스키마에 포함된 데이터를 기반으로** 요소를 활성화해야 합니다. 단순하게 정보를 나열하는 것이 아니라, 수치가 *위험*을 의미할 때 경고색을 입혀야 합니다.

| 데이터 필드 (Schema Key) | 유형/조건 | 시각적 요소 | 스타일링 규칙 | [근거: Potential Loss Shielding] |
| :--- | :--- | :--- | :--- | :--- |
| `Potential_Loss` | **필수** / 금액 > 0 | 거대한 숫자 (`$XXk`)와 경고 아이콘(🚨) | **폰트:** Impact/Oswald. **색상:** `#C94A1B` (Risk Amber). **크기:** 전체 레이아웃의 30% 이상 차지하도록 압도적으로 배치. | Self-RAG, Potential Loss Shielding |
| `Data_Inconsistency_Count` | 필수 / Count > 0 | 빨간색 하이라이트된 '틈' 다이어그램 (`❌`) | **위치:** 배경 흐름도의 특정 지점(L0)에 배치. 강한 경고 느낌 부여. | Self-RAG, Potential Loss Shielding |
| `Core_Solution_Icon` | 필수 / Icon 존재 여부 | JKstory 핵심 기능 3가지 아이콘 배열 (AI, Source Grounding 등) | **배치:** 잠재적 손실액 바로 아래 (L2). 이 아이콘들이 방어막처럼 보이게 디자인. | Self-RAG, Phase 2 |
| `SEO_Keyword` | 선택 / 키워드 존재 여부 | 서브 헤드라인에 활용 ('3PL 리스크 관리', '데이터 불일치') | **폰트:** Roboto Mono (기술적 느낌). **색상:** `#007BFF` (Security Blue)로 강조. | Self-RAG, 专业性 강조 |
| `Main_Headline` | 필수 / 제목 텍스트 | 가장 큰 메인 타이틀 (`혹시 매년 OOO만원을 버리고 계신가요?`) | **색상:** `#EAEAEA`. **배치:** 상단 중앙(L3). | - |

## III. ✨ 컴포넌트별 세부 구현 명세 (Component Specifics)

### 1. Loss Display Component (`Potential_Loss`)
*   **기능:** 데이터 스크립트가 `$XX,XXX` 값을 읽어와야 함.
*   **연출:** 단순히 숫자를 보여주는 것을 넘어, 마치 **‘재무 보고서의 파국적인 단면’**처럼 보이도록 디자인해야 합니다. (Audit Report Schema 레퍼런스 활용) [근거: Self-RAG]
*   **트리거 로직:** `Potential_Loss` 값이 높을수록, 해당 숫자의 크기(Font Size)와 폰트의 두께(Font Weight)가 비례하여 증가해야 합니다.

### 2. Transition Layer (공포 $\to$ 희망 전환 장치)
*   **위치:** Loss Display Component 바로 아래 또는 좌측에 배치.
*   **구현 방식:** 잠재적 손실액(`Risk Amber`)이 제시된 직후, 배경의 복잡한 물류 다이어그램 위를 **강력하고 명확한 시각적 구분선(Security Blue)**이 가로지르며 '방어벽'처럼 보이게 애니메이션 처리되어야 합니다. [근거: Self-RAG]
*   **목표:** 공포감을 극대화하는 지점에서, JKstory가 해결책임을 각인시키는 전환점 역할을 수행해야 함.

## IV. 💻 자동화 파이프라인 구동 체크리스트 (Developer Checklist)
1.  [ ] **Input Check:** `thumbnail_data_schema_v1.json` 파일의 필수 필드(Potential\_Loss, Data\_Inconsistency\_Count 등)가 누락되었는지 확인한다.
2.  [ ] **Styling Check:** 모든 경고 요소는 `#C94A1B`로 통일하고, 해결책 요소는 `#007BFF`로 통일하는지 검증한다.
3.  [ ] **Layout Check:** Loss → Transition $\to$ Solution의 흐름이 시각적으로 막힘없이 연결되는지 최종 테스트를 거친다.

---
**[기술 참고 사항]**
*   **Font Family (추천):** Oswald, Roboto Mono (전문적/디지털 느낌 강화)
*   **Color Codes:** Primary: `#1A2B38`, Danger: `#C94A1B`, Solution: `#007BFF`