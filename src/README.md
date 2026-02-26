# 💻 Source Code (`src/`)

에이전틱 RAG(Retrieval-Augmented Generation) 시스템의 핵심 로직과 엔진 아키텍처가 구현되어 있습니다.

---

## 📂 모듈별 상세 아키텍처

### 1. [agents/](./agents) (지능형 에이전트 시스템)
LangGraph를 이용한 계층형 전문가 조직을 정의합니다.
- **`graph.py`**: 서비스 내 모든 대화 흐름의 토폴로지 및 상태 전이 로직 정의.
- **`head_butler.py`**: 사용자 의도 분석 및 최적 전문가(`matchmaker`, `care`, `liaison`) 배정. 일반 질문은 직접 응답. 전문가 결과를 사용자 친화적 응답으로 합성.
- **`matchmaker.py`**: 품종 추천 전문가. 10건 RAG 검색 후 LLM이 상위 3건을 선별하는 **Agentic Selection** 방식.
- **`care_team.py`**: 건강(의료)과 행동(교정) 상담을 통합한 단일 노드. 키워드 기반 내부 모드 전환.
- **`liaison.py`**: 입양/구조 정보 전문가. 국가동물보호정보시스템 API 도구 호출 및 RAG 기반 입양 가이드 제공.
- **`state.py`**: 전체 그래프에서 공유되는 `AgentState` 데이터 구조 정의 (`messages`, `user_profile`, `router_decision`, `specialist_result`, `recommendations`, `rag_docs`).
- **`filters/`**:
  - **`breed_criteria.py`**: Breed Filtering Policy 구현. 사용자 질문을 수치형 메타데이터 필터로 변환.
- **`tools/`**:
  - **`animal_protection.py`**: 국가동물보호정보시스템 API 연동 Tool (`search_abandoned_animals`). 시도/시군구별 유기묘 검색.
  - **`region_codes.py`**: 시도(17개) 및 시군구 코드 정적 딕셔너리. API 호출 시 지역명→코드 변환.
  - **`shelter_codes.py`**: 보호소 코드 매핑.

### 2. [pipelines/](./pipelines) (데이터 제조 공정)
V1, V2, V3 각 파이프라인 세대별로 독립적인 모듈 구조를 갖습니다.
- **구조**: `classifier.py`, `embedder.py`, `loader.py`, `preprocessor.py`, `schemas.py`
- **v3**: 현재 서비스 공정으로, 비동기 병렬 처리 및 구조적 임베딩을 통한 고속 적재 수행.

### 3. [retrieval/](./retrieval) (지능형 검색 엔진)
- **`hybrid_search.py`**: **RRF(Reciprocal Rank Fusion)** 알고리즘을 구현하여 벡터 검색 유사도와 BM25 키워드 정합성을 통합 산출. 동적 메타데이터 필터링 지원.

### 4. [core/](./core) (핵심 자산 및 설정)
프로젝트 전반에 걸쳐 사용되는 중앙 집중화된 리소스를 관리합니다. **[상세 문서 보기](./core/README.md)**

#### 4.1. Configuration & Settings
- **`config.py`**: 정책 기반 환경 설정(`ZipsaConfig`) 및 DB/모델 관리. `LLMConfig`를 포함하여 **Dual-Model Strategy**(`Nano`+`Mini`)를 제어합니다.

#### 4.2. Prompts (중앙 집중식 프롬프트 관리)
- **`prompts/`**:
  - **`prompts.yaml`**: 모든 에이전트의 페르소나 및 시스템 프롬프트 정의.
  - **`prompt_manager.py`**: 프롬프트의 동적 로딩 및 실시간 업데이트 엔진 (Singleton).

#### 4.3. Models (데이터 구조 및 DTO)
- **`models/`**:
  - **`user_profile.py`**: 사용자 프로필 DTO (타입 안정성, Hard Constraint 추출).
  - **`cat_card.py`**: UI 카드(`CatCardRecommendation`, `CatCardStats`) 렌더링 스키마. Matchmaker 전용.

#### 4.4. Tokenizer (도메인 특화 형태소 분석)
- **`tokenizer/`**:
  - **`domain_dictionary.txt`**: Kiwi 형태소 분석기용 사용자 사전 (~1,100개 핵심 용어).
  - **`extra_nouns.txt`**: 사전 빌드 시 참조하는 추가 명사 소스.
  - **`synonyms.json`**: 묘종 명칭 및 특성어 확장을 위한 동의어 정규화 사전.
  - **`stopwords.txt`**: 한국어 검색 제외어 리스트.

### 5. [ui/](./ui) (사용자 인터페이스)
Streamlit + Jinja2 HTML 템플릿 기반의 커스텀 UI 시스템입니다.
- **`app.py`**: 메인 엔트리포인트. 온보딩(커스텀 컴포넌트) → 채팅(2컬럼 레이아웃) 페이지 전환.
- **`utils.py`**: `astream_events v2` 기반 실시간 스트리밍 유틸리티. `router_classification` 태그 필터링으로 내부 JSON 노출 차단.
- **`components/`**: Jinja2 HTML 템플릿 모음.
  - **`base.html`**: 글로벌 CSS 변수 및 디자인 토큰, Streamlit 기본 크롬 숨김.
  - **`layout_header.html`**: 헤더 + 스플래시 스크린 통합 레이아웃.
  - **`header_view.html`**: 고정 헤더 (프로필 요약 캡슐, 팀 정보 팝업).
  - **`cat_card.html`**: 포켓몬 스타일 품종 카드 (Matchmaker 결과 전용).
  - **`rag_document.html`**: RAG 출처 문서 카드.
  - **`reasoning_view.html`**: 에이전트 추론 과정 실시간 표시.
  - **`chat_elements.html`**: 플레이스홀더 및 로딩 상태.
  - **`onboarding/`**: Streamlit 커스텀 컴포넌트 (postMessage 브릿지).
- **`renderers/`**: HTML 렌더링 모듈.
  - **`cat_card.py`**: 품종 카드 Jinja2 렌더러.
  - **`rag_doc.py`**: RAG 출처 문서 렌더러.
  - **`reasoning.py`**: 스트리밍 추론 과정 렌더러.

### 6. [utils/](./utils) (공통 유틸리티)
- **`text.py`**: Kiwi 형태소 분석기를 이용한 도메인 사전 기반 토큰화 및 클리닝.
- **`mongodb.py`**: v1, v2, v3 클러스터별 비동기 DB 매니저.

### 7. [notebooks/](./notebooks) (실험실)
- 토크나이저 최적화, 검색 성능 벤치마킹, 에이전트 프롬프트 실험용 Jupyter Notebook 보관.
- **`agent_prompt_experiment.ipynb`**: 에이전트 프롬프트 및 라우팅 로직 테스트.
- **`debug_langgraph.ipynb`**: LangGraph 전이 로직 및 상태 관리 디버깅.
- **`retriever_experiment.ipynb`**: 하이브리드 검색 성능 벤치마킹.
- **`tokenizer_experiment.ipynb`**: Kiwi 토크나이저 및 도메인 사전 효과 검증.

---

## 🔑 Key Architectural Highlights

### 4-Node Agent System (Head Butler + 3 Specialists)
- **Head Butler**: 최상위 라우터 겸 응답 합성기. `matchmaker`, `care`, `liaison`, `general` 4방향 분류.
- **Matchmaker**: 품종 추천 전문가. 10건 RAG 검색 → LLM Agentic Selection으로 상위 3건 선별.
- **Care Team**: 건강(의료) + 행동(교정) 통합 전문가. RAG 기반 응답 생성.
- **Liaison**: 입양/구조 정보 전문가. 국가동물보호정보시스템 API Tool + RAG 입양 가이드.

### Breed Filtering Policy
- **Location**: `agents/filters/breed_criteria.py`
- **Purpose**: "털 안 빠지는", "조용한" 등의 자연어 요구사항을 `filter_shedding <= 2` 같은 수치형 필터로 변환.
- **Strategy**: 명시적 질문(Query)을 우선하여 프로필 컨텍스트가 검색을 과도하게 제한하지 않도록 설계.

### Streaming & Tag-based Filtering
- **`astream_events v2`**: LLM 토큰 스트리밍으로 실시간 응답 표시.
- **`router_classification` 태그**: 내부 라우팅/분류용 structured output JSON이 사용자에게 노출되지 않도록 차단.

### Unified V3 Collection
- **Storage**: 아티클과 품종 데이터를 `cat_library.care_guides` 단일 컬렉션에 통합.
- **Differentiation**: `categories`, `specialists`, `filter_*` 필드로 구분 및 동적 필터링.
