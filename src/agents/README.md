# 🤖 Intelligent Agents (`src/agents/`)

LangGraph 기반의 4-Node Agent System을 구현한 모듈입니다. 사용자 의도를 심층 분석하고, 각 분야의 전문가(Specialist) 에이전트들이 협업하여 최적의 솔루션을 제공합니다.

---

## 🏗️ Architecture

### 4-Node System
1. **Head Butler (수석 집사)**: 라우터(Router)이자 유일한 접점(Exit Point)입니다.
2. **Specialist Group**:
   - **Matchmaker**: 품종 추천 전문가.
   - **Liaison**: 입양/구조 전문가.
   - **Care Team**: 건강/행동 통합 전문가.

### Dual-Model Strategy
비용 효율성과 성능 최적화를 위해 **이원화된 LLM 전략**을 사용합니다. 모든 에이전트는 두 모델을 동시에 로드하여 상황에 맞게 사용합니다.

| 모델 역할 | 모델명 (Config) | 사용처 | 특징 |
| :--- | :--- | :--- | :--- |
| **Router** | `gpt-4.1-nano` | 의도 분류, Tool 결정, 구조화된 출력(JSON) | 초경량, 고속, 저비용 |
| **Basic** | `gpt-4o-mini` | 텍스트 요약(Distillation), 대화 생성, 최종 응답 | 범용, 준수한 작문 능력 |

---

## 📂 Agent Details

### 1. Head Butler (`head_butler.py`)
- **역할**: 오케스트레이터. 사용자의 첫 질문을 받아 적절한 전문가에게 라우팅하고, 전문가의 보고서를 받아 사용자가 이해하기 쉬운 톤으로 최종 답변을 작성합니다.
- **주요 로직**:
  - `RouterDecision` (LCEL Structured Output): `llm_router` 사용.
  - `POSTPROCESS_PROMPT`: `llm_basic` 사용. 전문가 JSON 데이터를 자연스러운 대화로 변환.

### 2. Matchmaker (`matchmaker.py`)
- **역할**: 사용자 라이프스타일(주거, 알러지 등)과 선호도를 분석하여 최적의 고양이 품종을 추천합니다.
- **주요 로직**:
  - **Intent Classification**: `LOOKUP`(단순 조회) vs `RECOMMEND`(환경 기반 추천) 분류 (`llm_router`).
  - **Agentic Selection**: 10건의 RAG 검색 결과 중, LLM이 상위 3건을 논리적으로 선별 (`llm_router`).
  - **Context Distillation**: 선택된 품종 정보를 요약 (`llm_basic`).

### 3. Liaison (`liaison.py`)
- **역할**: 입양 절차를 안내하고, 실시간 구조동물 정보를 조회합니다.
- **주요 로직**:
  - **Tool Binding**: `search_abandoned_animals` 도구 호출 여부 결정 (`llm_router`).
  - **RAG Search**: 입양 가이드 문서 검색 및 요약 (`llm_basic`).

### 4. Care Team (`care_team.py`)
- **역할**: 의료(Physician)와 행동(Peacekeeper) 문제를 통합적으로 다룹니다.
- **주요 로직**:
  - **Internal Routing**: 질문 내용을 분석하여 `physician` 또는 `peacekeeper`로 세부 분류 (`llm_router`).
  - **Persona Conversion**: 분류 결과에 따라 적절한 페르소나(주치의 비서/행동 전문가) 로드.

---

## 🛠️ Tools (`tools/`)

### `animal_protection.py`
- **기능**: 국가동물보호정보시스템(Animal Protection Management System)의 유기동물 조회 API를 래핑한 LangChain Tool입니다.
- **특징**: `region_codes.py`를 참조하여 자연어 지역명(예: "서울 마포구")을 행정구역 코드로 자동 변환하여 검색합니다.

---

## 🔄 State Management (`state.py`)

`AgentState` TypedDict를 통해 그래프 내의 데이터 흐름을 관리합니다.
- **`messages`**: 대화 기록 (BaseMessage 리스트).
- **`user_profile`**: 사용자 정보 (UserProfile 객체).
- **`specialist_result`**: 전문가 노드가 반환하는 구조화된 JSON (페르소나, RAG 문서, 요약 정보 포함).
