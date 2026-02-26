# 🏰 ZIPSA: AI-Powered Cat Head Butler
> **"Every Butler Needs a Head Butler."**
> 집사들을 위한 반려묘 입양 및 케어 지원 챗봇

---

## 1. Project Vision (비전)
**ZIPSA(집사)**는 초보 및 예비 '집사(고양이 반려인)'를 위한 **AI 수석 집사 서비스**입니다.
사용자의 라이프스타일과 환경을 심층 분석하여 가장 적합한 묘종을 추천하고(Matching), 입양 절차를 안내하며(Liaison), 입양 후에는 **반려묘 간의 관계 개선(Peacekeeper)부터 건강 관리(Physician) 등 케어까지** 전방위로 지원하는 것을 목표로 하는 **'Agentic RAG' 기반의 코칭 시스템**입니다. 단순한 챗봇을 넘어, 전문성을 가진 **전문가 팀(Specialists)**이 협업하여 사용자의 고민을 해결합니다.

---

## 2. Core Features (핵심 기능)

### 🧩 1. Lifestyle Matching (맞춤형 매칭)
- **사용자 분석**: 주거 환경(아파트/주택), 가족 구성원, 알러지 유무, 활동량 등을 고려한 정밀 분석.
- **RAG 기반 추천**: 67종의 고양이 품종 데이터와 수천 건의 양육 가이드를 기반으로 최적의 묘종 매칭.
- **Breed Filtering Policy**: "털 빠짐", "활동량" 등 사용자의 구체적인 요구사항을 데이터 수치와 매칭하는 필터링 기반 추천 적용.
- **파양 방지**: 단순 외모가 아닌, '함께 살 수 있는' 반려묘를 추천하여 파양률을 낮춥니다.

### 🔭 2. Ethical Adoption (입양/구조 연계)
- **입양 안내**: 입양 절차, 서류, 비용, 준비물 등 일반 입양 정보를 RAG 기반으로 제공.
- **구조동물 조회**: 국가동물보호정보시스템 API를 통해 보호 중인 고양이 정보를 실시간 조회.
- **보호소 연계**: 지역별 보호소 정보 및 연락처 안내.

### ⚖️ 3. Conflict Resolution (반려묘 간 관계 개선)
- **행동/심리 상담**: 분리불안, 공격성 등 문제 행동에 대한 행동학적 원인 및 솔루션 제공.
- **합사 가이드**: 다중묘 가정을 위한 단계별 합사 요령 및 스트레스 관리법 안내.

### 🩺 4. Lifecycle Care (생애주기 케어)
- **건강 모니터링**: 구토, 배변 등 이상 징후 발생 시 초기 대응 가이드(Triage) 제공.
- **영양 관리**: 연령별/묘종별 사료 및 영양학적 조언.

---

## 3. Agent Structure (AI 에이전트 구조)
ZIPSA 시스템은 **수석 집사(Head Butler)**를 중심으로 4개의 전문가 노드로 구성되어 있습니다.
Head Butler가 유일한 Exit Point이며, 전문가 노드는 구조화 JSON(`specialist_result`)으로 결과를 반환하고 반드시 Head Butler로 복귀합니다.

### 🎩 Head Butler (수석 집사 / Router & Exit Point)
- **역할**: 사용자 의도를 LLM Structured Output으로 분류(`matchmaker`, `liaison`, `care`, `general`)하여 라우팅. 일반 질문은 직접 응답. 전문가 복귀 시 specialist_result를 후처리하여 최종 응답 생성.
- **위치**: `src/agents/head_butler.py`

### 🧩 Matchmaker (품종 추천 전문가)
- **역할**: 라이프스타일 기반 품종 추천 (RAG: `specialist="Matchmaker"`, `categories="Breeds"` 필터).
- **위치**: `src/agents/matchmaker.py`

### 🔭 Liaison (입양/구조 전문가)
- **역할**: 입양 절차/서류/비용 안내 (RAG: `specialist="Liaison"`), 구조동물 조회 (Tool).
- **Tool**: `search_abandoned_animals` — 국가동물보호정보시스템 유기동물 조회 API (`src/agents/tools/animal_protection.py`)
- **위치**: `src/agents/liaison.py`

### 🏥 Care Team (건강 & 행동 통합 전문가)
- **역할**: LLM 분류로 Physician(의료) / Peacekeeper(행동)을 내부 판단 후 해당 specialist 태그로 RAG 검색. 페르소나 프롬프트 기반 응답 생성.
- **위치**: `src/agents/care_team.py`

> [!TIP]
> 각 페르소나의 상세 역할과 동작 방식은 **[personas.md](./personas.md)** 문서를 참조하세요.

---

## 4. Technical Architecture (아키텍처)
본 프로젝트는 **LangGraph 기반 4-Node Agent System** 패턴을 채택했습니다.

- **Orchestration**: `LangGraph`를 이용한 상태 관리(Stateful) 및 에이전트 라우팅. Head Butler가 유일한 Exit Point.
- **Dual-Model Strategy (Cost Optimization)**:
  - **Router (`gpt-4.1-nano`)**: 의도 분류 및 구조화된 판단(JSON) 전용. 초경량/고비용 효율.
  - **Basic (`gpt-4o-mini`)**: 텍스트 요약(RAG Context Distillation) 및 최종 응답 생성.
- **Knowledge Base (RAG)**:
    - **Vector Store**: MongoDB Atlas Vector Search (`cat_library`).
    - **Retrieval**: Hybrid Search (Vector + Keyword/BM25 + RRF Re-ranking + Dynamic Metadata Filtering).
    - **Data Source**: TheCatAPI(품종), Wikipedia(상세), BemyPet(케어 가이드).
- **Interface**: Streamlit 기반의 인터랙티브 채팅 UI.
- **Environment**: Python 3.11+ (Conda `skn-third-proj`).
- **Data Pipeline**:
  - **V3 Pipeline**: `src/pipelines/v3/` (Decoupled 3-Stage Process)
    1. **Preprocessor**: Text Cleaning & Tokenization -> `processed.json`
    2. **Embedder**: OpenAI Embedding Generation -> `embedded.pkl`
    3. **Loader**: MongoDB Ingestion (`cat_library`)

> [!IMPORTANT]
> 시스템의 시각적 구조도와 데이터 흐름은 **[architecture_graph.md](./architecture_graph.md)**를 확인하세요.

---

## 5. Directory Structure
```
skn-third-proj/
├── data/                       # 데이터 저장소 (Raw, Processed, V3 Embeddings)
├── docs/                       # 프로젝트 문서 (기획, 아키텍처, 개발일지, 발표자료)
├── scripts/                    # 유틸리티 스크립트 (크롤링, 전처리, 테스트)
├── src/                        # 메인 소스 코드
│   ├── agents/                 # LangGraph 에이전트 및 워크플로우 정의
│   │   ├── tools/              # 외부 API 연동 도구 (유기동물 조회 등)
│   │   ├── care_team.py        # 케어 팀(의료/행동) 에이전트
│   │   ├── graph.py            # 에이전트 그래프(Workflow) 구성
│   │   ├── head_butler.py      # 수석 집사 (메인 라우터)
│   │   ├── liaison.py          # 입양/연계 전문가
│   │   ├── matchmaker.py       # 매치메이커 (품종 추천)
│   │   └── state.py            # LangGraph 상태(State) 정의
│   ├── core/                   # 프로젝트 핵심 설정 및 공통 모듈
│   │   ├── models/             # DTO (Pydantic 데이터 모델)
│   │   ├── prompts/            # 프롬프트 관리 (YAML 로드/매니저)
│   │   ├── tokenizer/          # 형태소 분석기 리소스 (사용자 사전, 불용어)
│   │   └── config.py           # 환경변수 로드 및 설정 관리
│   ├── embeddings/             # 임베딩 생성 로직 (Factory 패턴)
│   ├── notebooks/              # 데이터 분석 및 실험용 주피터 노트북
│   ├── pipelines/              # 데이터 파이프라인 (전처리, 임베딩, 적재)
│   ├── retrieval/              # 검색 엔진 (Hybrid Search, RRF)
│   │   ├── bm25_retriever.py   # 키워드 검색기
│   │   ├── hybrid_search.py    # 하이브리드 검색 및 RRF 로직
│   │   └── vector_retriever.py # 벡터 검색기
│   ├── ui/                     # Streamlit 프론트엔드 애플리케이션
│   │   ├── components/         # UI 컴포넌트 (HTML/CSS 렌더링)
│   │   ├── app.py              # 메인 애플리케이션 진입점
│   │   └── utils.py            # UI 전용 유틸리티 (세션, 스트리밍)
│   └── utils/                  # 범용 유틸리티 (로깅, 텍스트 처리 등)
└── .env                        # 환경변수 (API Key, DB URI)
```
