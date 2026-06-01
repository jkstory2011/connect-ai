# 🎨 JKstory 디자인 시스템 V2.0 통합 명세서 (Tech Spec)

**버전:** 1.0.0
**작성자:** Designer Agent
**최종 검토:** Developer Agent (예정)
**목표:** 자동화 파이프라인에 즉시 투입 가능한 시각적 컴포넌트의 속성(Attributes), 상태값(States), 그리드 기반 가이드라인을 정의하여, 디자인 의도를 코드로 변환하는 최종 지침서.

---

## ⚙️ I. 글로벌 시스템 설정 (Global Variables)
자동화 과정에서 사용되는 모든 기본 값과 제어 가능한 변수를 정의합니다.

| 속성명 | 키(Key) | 값(Value) | 설명 및 용도 예시 | 근거 |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Color** | `--color-primary` | `#1A2B38` (JK Deep Blue) | 기본 배경, 섹션 구분선, 신뢰성 요소. | Self-RAG |
| **Secondary Color** | `--color-secondary` | `#007BFF` (Security Blue) | 해결책 제시 영역, 성공적인 데이터 흐름 강조. | Self-RAG |
| **Danger/Loss Color** | `--color-danger` | `#C94A1B` (Risk Amber) | 잠재적 손실액($), 문제 발생 지점(Highlight). 경고색으로 사용 필수. | Self-RAG, Potential Loss Shielding |
| **Font Family** | `--font-family` | `'Roboto Mono', monospace` | 기술적 전문성 및 데이터 기반 톤앤매너 유지. | Self-RAG |
| **Global BG Color** | `--bg-color` | `#1A2B38` | 모든 콘텐츠의 기본 배경색 (Dark Mode). | Self-RAG, Global Style |
| **Text Color** | `--text-color` | `#EAEAEA` | 기본 본문 텍스트 색상. | Self-RAG |

## 📐 II. 그리드 및 레이아웃 시스템 (Grid & Layout)
모든 컴포넌트는 12컬럼 그리드를 기반으로 하며, 여백(Padding/Margin)은 스케일링 비율을 사용합니다.

*   **Standard Padding:** `padding: [size] * 4px` (Minimum 64px)
*   **Main Content Width:** 최대 1280px 제한. 중앙 정렬 필수.
*   **Visual Hierarchy Rule:** 가장 중요한 정보(Potential Loss, 해결책 수치)는 반드시 **컬럼 폭의 60% 이상을 차지하는 크고 굵은 타이포그래피(`font-size: 4rem+`)로 처리**해야 합니다.

## 🧩 III. 핵심 컴포넌트 사양 (Component Specs)
자동화 파이프라인에 의해 생성되는 필수 UI 요소들의 구체적 속성입니다.

### 1. Potential Loss 강조 섹션 (`PotentialLossBlock`)
*   **목표:** 공포감 극대화 및 시각적 충격도(Visual Impact) 제공.
*   **필수 컴포넌트:** 대형 수치 표시기 (Big Number Display), 경고 배지 (Warning Badge).
*   **속성 정의:**
    *   `--data-value`: 실제 손실액을 입력받는 파라미터 (예: $12.3M)
    *   `--color`: **강제 `#C94A1B` 사용**. 다른 색상 사용 금지.
    *   `--font-size`: 최소 `4rem`, 최대 `8rem`까지 스케일링 가능하도록 정의.
    *   `--visual-effect`: 배경에 깜빡이는 디지털 노이즈 효과(`[Animation: Flicker]`)를 적용하여 긴급성을 부여해야 합니다.

### 2. 데이터 플로우 다이어그램 (`DataFlowDiagram`)
*   **목표:** 복잡한 시스템의 흐름과 구조적 취약점을 시각화합니다.
*   **구조:** 노드(Node)와 연결선(Edge)으로 구성됩니다.
    *   **노드 상태 1 (정상):** 배경색: `#1A2B38`, 테두리: `--color-primary`.
    *   **노드 상태 2 (취약점/오류):** 배경색: 어둡게 처리, 테두리: **`--color-danger`**. 노드 중앙에 오류 원인(`Potential Loss`)을 간략히 표시해야 합니다.
    *   **연결선:** 흐름의 방향성을 나타내는 화살표(Arrow)를 사용하며, 취약점 구간의 연결선은 끊어져 있거나 빨간색 점선(`Dashed Red Line`)으로 처리합니다.

### 3. 해결책 제시 컴포넌트 (`SolutionBlock`)
*   **목표:** 공포 $\to$ 희망 전환 장치 역할 수행.
*   **구분선 (The Shield):** 섹션 시작과 끝을 가로지르는 **`--color-secondary`** 계열의 강한 구분선을 반드시 배치합니다. 이 선은 '방어막'처럼 느껴져야 합니다.
*   **아이콘/설명:** JKstory 핵심 기능을 3개(최대)까지 나열하며, 각 아이콘 아래에는 `--text-color` 대신 **`--color-secondary`를 배경으로 하는 작은 박스(`Badge`)** 안에 상세 설명이 포함되어야 합니다.

## ✅ IV. 자동화 파라미터 및 제약사항 (Automation Constraints)
자동화된 썸네일/웹페이지 생성 시, 다음 규칙을 강제 적용합니다.

1.  **가독성 최우선:** 모든 텍스트는 `monospace` 계열의 폰트를 사용하여 데이터 분석 보고서 같은 전문성을 유지해야 합니다.
2.  **정보 밀도:** 페이지당 최소한의 설명으로 최대의 정보를 전달할 수 있도록, 배경에 복잡하고 흐릿한 다이어그램(물류 시스템/데이터 연결망)을 패턴으로 배치합니다. (전문성 확보).
3.  **CTA 버튼:** 항상 `Secondary Color`와 대비되는 강렬한 색상 조합을 사용하며, 텍스트는 '리스크 진단 시작'과 같은 긴급성을 유발하는 문구여야 합니다.

---