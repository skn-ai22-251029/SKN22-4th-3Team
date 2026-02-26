# 🎭 Service Personas & Roles (페르소나 상세)

ZIPSA 서비스는 LangGraph 기반의 **4-Node Agent System**을 따르며, 각 페르소나는 특정 소스 코드 파일에 정의된 **Node** 및 **RAG Strategy**와 매핑됩니다.

> [!NOTE]
> 모든 에이전트의 구체적인 지시 사항(System Prompt)과 페르소나는 `src/core/prompts/prompts.yaml`에서 동적으로 관리됩니다.

---

## 🎩 1. The Head Butler (총괄 수석 집사)
> **"집사님, 무엇을 도와드릴까요? 전문가를 호출하겠습니다."**

- **Role**: 사용자 의도(Intent)를 LLM Structured Output으로 분류하고 전문가 노드(`matchmaker`, `liaison`, `care`)로 라우팅하는 Router이자 그래프의 **유일한 Exit Point**.
- **Responsibility**:
    - 대화의 맥락 파악 및 초기 응대 (General Chat → 직접 응답 후 종료).
    - 사용자 프로필(Housing, Activity, Traits) 컨텍스트 주입.
    - 전문가 노드 복귀 시 `specialist_result`(구조화 JSON)를 후처리 → 페르소나 톤 반영 + 마무리 멘트 → `__end__`.
- **Source Code**:
    - 📄 [src/agents/head_butler.py](../../src/agents/head_butler.py)
    - **Node**: `head_butler_node`

---

## 🧩 2. Matchmaker (품종 추천 전문가)
> **"집사님의 라이프스타일에 딱 맞는 묘종을 추천해 드립니다냥!"**

- **Specialist Key**: `"Matchmaker"` (RAG Metadata), `categories: "Breeds"` 필터
- **Role**: 주거 환경, 활동량, 성향 데이터를 기반으로 최적의 품종을 추천.
- **Logic**: Hybrid Search (Vector + Breeds Metadata Filtering)
- **완료 후**: `specialist_result` → `head_butler`로 복귀
- **Source Code**:
    - 📄 [src/agents/matchmaker.py](../../src/agents/matchmaker.py)
    - **Node**: `matchmaker_node`

---

## 🔭 3. Liaison (입양/구조 전문가)
> **"새 가족을 찾아주는 일이라니, 정말 멋진 집사다냥!"**

- **Specialist Key**: `"Liaison"` (RAG Metadata, 222건)
- **Role**: 입양 절차, 서류, 비용, 준비물 등 일반 입양 정보 안내. 구조동물 실시간 조회.
- **Logic**: Hybrid Search (Vector + Liaison specialist 태그) + Tool Call
- **Tool**: `search_abandoned_animals` — 국가동물보호정보시스템 유기동물 조회 API
- **Tool Call 흐름**: Liaison → Tools → Liaison → `head_butler`
- **완료 후**: `specialist_result` → `head_butler`로 복귀
- **Source Code**:
    - 📄 [src/agents/liaison.py](../../src/agents/liaison.py)
    - 📄 [src/agents/tools/animal_protection.py](../../src/agents/tools/animal_protection.py)
    - **Node**: `liaison_node`

---

## 🏥 4. Care Team (건강 & 행동 통합 전문가)
Care Team은 단일 노드 내에서 LLM Structured Output으로 Physician / Peacekeeper를 판단하고, 해당 페르소나와 specialist 태그로 RAG 검색 후 구조화 JSON을 반환합니다.

### 🩺 Physician (주치의/건강 관리)
> **"건강은 조기 예방이 최우선이다냥. 증상을 말씀해 주세요."**
- **Specialist Key**: `"Physician"`
- **Role**: 구토, 설사, 식욕 부진 등 질병 증상을 분석하고 대처법 및 영양 가이드 제공.
- **Logic**: LLM 분류 → Physician specialist 태그로 RAG 검색.

### ⚖️ Peacekeeper (평화 유지군/행동 교정)
> **"고양이들 간의 다툼이나 문제 행동에는 이유가 있다냥."**
- **Specialist Key**: `"Peacekeeper"`
- **Role**: 합사 갈등, 배변 실수, 공격성 등 행동학적 문제 원인 분석 및 해결책 제시.
- **Logic**: LLM 분류 → Peacekeeper specialist 태그로 RAG 검색.

**완료 후**: `specialist_result` → `head_butler`로 복귀

- **Source Code**:
    - 📄 [src/agents/care_team.py](../../src/agents/care_team.py)
    - **Node**: `care_team_node`
