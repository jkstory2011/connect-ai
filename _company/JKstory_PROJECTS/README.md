# JKstory 표준 프로젝트 폴더 구조 및 디자인 시스템 V2.0 적용 가이드

## 🎯 목표: 작업 과정과 결과물의 완벽한 분리
이 구조는 모든 콘텐츠 제작의 '진실의 원본(Source of Truth)'을 보존하는 것을 목표로 합니다. 코다리의 기술 파이프라인은 이 폴더 구조 내에서 작동합니다.

---

### ✨ 1. 프로젝트 루트 디렉토리 (`[프로젝트 이름]`)
*   **위치:** `JKstory_PROJECTS/[프로젝트 이름]/`
*   **역할:** 해당 콘텐츠에 관련된 모든 자산(영상, 이미지, 스크립트, 디자인 가이드)을 담는 최상위 컨테이너.

### ✨ 2. 필수 하위 디렉토리 구조 (The 4 Pillars)

| 폴더명 | 역할 (What goes here?) | 포함되는 산출물 유형 | 관리 주체 (Owner) |
| :--- | :--- | :--- | :--- |
| `01_Source_Assets` | **[입력 자산]** 원본 데이터, 스크립트, 레퍼런스. 수정 금지. | 📄 Final Script (Markdown), 🎥 Raw Footage (.mp4), 🎤 Source Audio Files (.wav), 🖼️ Moodboard Images. | Writer/CEO |
| `02_Design_System` | **[규격 및 가이드]** 브랜드가 정의하는 모든 시각적 규칙과 컴포넌트. | 🎨 Style Guide (PDF), 🖌️ Color Palette (HEX Code List), 📐 Component Mockups (FIGMA Link). | Designer |
| `03_Working_Drafts` | **[진행 중 작업물]** 반복적으로 수정되는 임시 결과물, 스토리보드. | 🖼️ Thumbnail V1-V5 (JPG), 🎬 Rough Cuts (.mp4), 📊 Data Viz Mockups (PPTX/PNG). | Designer/Leo |
| `04_Final_Output` | **[최종 아카이브]** 모든 검토가 완료된 최종 결과물만 보관. **(Read-Only)** | ✅ Final Video (.mp4 H.264), 🖼️ Master Thumbnail (JPG), 📝 Metadata Sheet (JSON). | All Agents (Final Check) |

---