# 🎨 Designer — 검증된 지식

_Self-RAG가 출력에서 `[근거: ...]` 태그가 붙은 주장만 자동 승격해서 누적._
_여기 들어온 내용만 다음 사이클의 retrieval 우선순위에 들어갑니다._
_사용자가 직접 줄을 지우면 그 주장은 다시 미검증 상태로 돌아갑니다._


- [2026-05-27] | **해결책 가이드** | 이 분석을 해결할 수 있는 JKstory의 핵심 기능 3가지 아이콘 배치. | 각 아이콘 아래에 간략한 설명과 함께 `` 태그를 작게 추가. | 공포(Fear) $\to$ 희망(Hope)으로 자연스럽게 전환시키는 역할. | _(근거: Potential Loss Shielding)_
- [2026-05-27] 2. **사운드/비주얼:** 낮은 주파수의 웅장하고 미니멀한 사운드(Ambient Drone)로 시작합니다. 마치 시스템이 부팅되는 듯한 '삐-익' 하는 디지털 노이즈가 배경을 채웁니다. _(근거: Self-RAG, 전문성 강조)_
- [2026-05-27] * **[Layout Tip]**: 첫 슬라이드는 최소한의 텍스트와 함께 임팩트 있는 비주얼(예: 복잡하게 엉킨 전선 다발이나 미로 같은 물류 흐름도)을 배치하여 시각적 혼란부터 유발합니다. _(근거: Self-RAG, 전문성 강조)_
- [2026-05-27] * **[Visual Element 2 - The Audit Report]**: 코다리의 `AuditReportSchema`를 기반으로 한 데이터 구조가 마치 **파국적인 재무 보고서의 단면**처럼 보이게 디자인하여, 전문적이고 압도적인 느낌을 줍니다. _(근거: Potential Loss Shielding)_
- [2026-05-28] * **레이아웃 Tip:** 첫 페이지는 최소한의 텍스트와 함께 임팩트 있는 비주얼(물류 흐름도 다이어그램)을 배치하여 시각적 혼란부터 유발합니다. _(근거: Self-RAG)_
- [2026-05-28] 1. **[Phase 1: The Loss]** - 배경은 어둡고, 경고색(Danger Amber)이 지배적입니다. 복잡한 데이터 흐름도 위에서 문제가 발생한 '지점'만 **빨간색으로 하이라이트**하고, 손실된 수치(`Potential Loss`)는 크고 굵게 배치합니다. (마치 공포스러운 재무 보고서의 단면처럼 보이게). _(근거: Self-RAG)_
- [2026-05-28] 2. **[Phase 2: The Shielding]** - 페이지를 가로지르는 강한 구분선(Security Blue)을 사용하며, '잠재적 손실액' 수치 아래에 **JKstory의 핵심 기능 3가지 아이콘**을 배치합니다. 이 아이콘들이 마치 방어막처럼 시각적으로 떠오르는 효과를 주어 공포에서 희망으로 전환시킵니다. _(근거: Self-RAG)_
- [2026-05-28] | 요소 | 역할/상황 | HEX 코드 | 용도 예시 | | _(근거: Self-RAG, Memory)_
- [2026-05-28] | **Primary (Authority)** | 기본 배경색, 본문 텍스트. 신뢰성 확보. | `#1A2B38` (JK Deep Blue) | 섹션 구분선, 제목 하단 라인. | | _(근거: Potential Loss Shielding)_
- [2026-05-28] | **Secondary (Danger/Loss)** | 잠재적 손실액($), 경고, 문제 지점 강조. | `#C94A1B` (Risk Amber) | **Potential Loss 수치**, 문제 발생 데이터 포인트. | | _(근거: Self-RAG, Potential Loss Shielding)_
- [2026-05-28] | **Tertiary (Safety/Solution)** | 해결책 제시, JKstory의 핵심 기능, 긍정적 전환. | `#007BFF` (Security Blue) | JKstory 솔루션 설명 영역, 성공적인 데이터 흐름. | | _(근거: Self-RAG)_
- [2026-05-28] * **레이아웃 Tip:** 첫 페이지부터 복잡하게 얽힌 다이어그램(물류 흐름도, 재고 데이터 연결망 등)을 배경에 깔고, 그 위에서 *문제가 발생한 지점*만 **빨간색/주황색(`Risk Amber`)으로 하이라이트**한다. _(근거: Self-RAG)_
- [2026-05-28] * **데이터 표현:** 코다리의 `AuditReportSchema`를 기반으로 하는 테이블이나 플로우차트를 활용한다. 섹션의 경계는 **Primary Blue** 계열의 강한 구분선으로 처리하여, 분석에 대한 신뢰도를 높인다. _(근거: Self-RAG)_
- [2026-05-28] * **전환 장치:** Phase 2의 잠재적 손실 수치가 제시된 직후, 페이지를 가로지르는 강한 구분선(`Security Blue`)을 배치한다. 이 선이 마치 방어벽처럼 느껴져야 한다. _(근거: Self-RAG)_
- [2026-05-28] * **Global Style:** `background-color: #1A2B38; color: #EAEAEA; font-family: 'Roboto Mono', monospace;` _(근거: Designer Memory, Primary Color)_
- [2026-05-28] * 전체 화면 상단에 복잡하게 얽힌 물류 시스템의 다이어그램(배경 패턴으로 흐릿하게 깔림). _(근거: Self-RAG, Layout Tip)_
- [2026-05-28] 2. **Sub-Text:** "당사의 딥러닝 기반 진단 모듈은 단순 오류가 아닌, **발생 가능한 최대 손실액(Potential Loss)**을 추산합니다." _(근거: Potential Loss Shielding)_
- [2026-05-28] * 직관적인 인터랙티브 폼 구조. 복잡한 수치 대신 슬라이더나 간편 체크박스를 사용해 심리적 부담을 낮춤. _(근거: Self-RAG, 전문성 강조)_
- [2026-05-28] (목표: 공포감 극대화. 시각적으로 압도적인 숫자 제시.) _(근거: Self-RAG, Phase 1)_
- [2026-05-28] * **스타일링:** `color: #C94A1B; font-size: 5em; font-weight: bold;` (Risk Amber, 압도적인 크기) _(근거: Self-RAG, Potential Loss Shielding)_
- [2026-05-28] (목표: 단순히 돈이 많이 샌다는 것을 넘어, *왜* 새는지 전문가적 근거를 제시하여 JKstory의 권위를 확보.) _(근거: Self-RAG, Potential Loss Shielding)_
- [2026-05-28] 2. **취약점 B: 데이터 파편화:** (아이콘: 흩어진 블록) "3개 이상의 독립된 마이크로서비스 간의 연결 고리가 끊어져 있습니다." _(근거: Potential Loss Shielding)_
- [2026-05-28] (목표: 공포를 해소하고, JKstory만이 이 모든 문제를 한 번에 막을 수 있는 '보험'임을 각인시키기.) _(근거: Self-RAG, Phase 2)_
- [2026-05-28] * **아이콘 1: AI 리스크 예측 엔진:** 상세 설명 (`<span style="color:#007BFF;">잠재적 손실액을 사전에 포착</span>`) _(근거: Self-RAG, 해결책 가이드)_
- [2026-05-28] * **아이콘 2: Source Grounding 시스템:** 상세 설명 (`<span style="color:#007BFF;">모든 데이터의 출처를 강제 추적하여 리스크 원인 제거</span>`) _(근거: Potential Loss Shielding)_