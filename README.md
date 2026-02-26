# 🏰 ZIPSA: AI-Powered Cat Head Butler
> **"Every Butler Needs a Head Butler."**
> 집사들을 위한 맞춤형 **AI 수석 집사(Head Butler) 서비스**

---

## 1. 프로젝트 비전 (Project Vision)
**ZIPSA(집사)** 는 사용자의 라이프스타일과 주거 환경을 심층 분석하여 **최적의 묘종을 추천(Matching)** 하고, **입양 절차를 안내(Liaison)** 하며, 입양 후에는 **반려묘와의 갈등 해결(Peacekeeper)** 부터 **건강 관리(Physician)** 까지 전방위로 지원하는 **'Agentic RAG' 기반의 코칭 시스템**입니다. 단순한 챗봇을 넘어, 전문성을 가진 **4명의 전문가 팀(Specialists)** 이 협업하여 집사님의 고민을 해결해 드립니다.


| 메인 홈 (Home) | 채팅 (Chat) | 조회 (Search) |
| :---: | :---: | :---: |
| ![Home](docs/assets/UI_01.png) | ![Chat](docs/assets/UI_02.png) | ![Profile](docs/assets/UI_03.png) |

---

## 2. 목표 핵심 기능 (Core Features)

### 🧩 1. 맞춤형 매칭 (Lifestyle Matching)
- **정밀 분석**: 주거 형태(아파트/주택), 가족 구성원, 알러지 유무, 활동량 등을 고려하여 사용자를 분석합니다.
- **RAG 기반 추천**: 67종의 품종 데이터와 1,000건 이상의 양육 가이드를 기반으로 최적의 묘종을 매칭합니다.
- **Breed Filtering Policy**: "털 빠짐 방어", "조용한 성격" 등 사용자의 구체적인 요구사항을 데이터 수치와 매칭하여 필터링합니다.

### 🔭 2. 윤리적 입양 지원 (Ethical Adoption)
- **입양 가이드**: 입양 절차, 필수 서류, 초기 비용, 준비물 등 입양에 필요한 모든 정보를 안내합니다.
- **유기동물 조회**: **국가동물보호정보시스템 API**를 연동하여, 현재 보호 중인 고양이를 실시간으로 조회하고 소개합니다.

### ⚖️ 3. 행동 교정 및 갈등 해결 (Conflict Resolution)
- **행동 심리 상담**: 분리불안, 공격성, 배변 실수 등 문제 행동의 원인을 분석하고 솔루션을 제공합니다.
- **합사 가이드**: 다중묘 가정을 위해 스트레스를 최소화하는 단계별 합사 요령을 코칭합니다.

### 🩺 4. 생애주기 케어 (Lifecycle Care)
- **건강 모니터링**: 구토, 설사 등 이상 징후에 대해 메뉴얼과 대응 방법을 알려줍니다.
- **영양 관리**: 연령별, 묘종별 적합한 사료와 영양 관리 팁을 제공합니다.

---

## 3. 에이전트 구조 (Agent Structure)
ZIPSA 시스템은 **수석 집사(Head Butler)** 를 중심으로 **4명의 전문가(Specialists)** 가 협업하는 구조입니다.

| 에이전트 | 역할 (Role) | 주요 기능 |
| :--- | :--- | :--- |
| **🎩 Head Butler** | **Router & Exit Point** | 사용자 의도를 파악하여 적절한 전문가에게 연결하고, 최종 답변을 정리합니다. |
| **🧩 Matchmaker** | **품종 추천 전문가** | 라이프스타일 데이터를 분석하여 최적의 고양이를 추천합니다. |
| **🔭 Liaison** | **입양/연계 전문가** | 입양 절차를 안내하고, 유기동물 보호소 정보를 실시간으로 조회합니다. |
| **🏥 Physician** | **수의학 전문가** | 고양이의 건강 이상 징후를 파악하고 수의학적 조언을 제공합니다. |
| **🛡️ Peacekeeper** | **행동 교정 전문가** | 고양이의 행동 언어를 해석하고, 문제 행동 교정 및 합사 솔루션을 제시합니다. |

---

## 4. 기술 아키텍처 (Technical Architecture)

### 🛠️ Tech Stack
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3.x-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.x-FF9900?style=flat-square&logo=langgraph&logoColor=white)
![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-Vector%20Search-47A248?style=flat-square&logo=mongodb&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%7C%20GPT--4.1--nano-412991?style=flat-square&logo=openai&logoColor=white)



### 🧠 LangGraph 기반 Multi-Agent System
- **Stateful Orchestration**: `LangGraph`를 사용하여 대화의 상태(Context)를 유지하고 에이전트 간 협업을 제어합니다.
- **Dual-Model Strategy**:
    - **Router (`gpt-4.1-nano`)**: 의도 분류 및 제어 로직 전용 (비용 효율화).
    - **Basic (`gpt-4o-mini`)**: 텍스트 요약 및 최종 답변 생성 (성능 최적화).

### 📚 Knowledge Base (RAG)
- **Vector Store**: MongoDB Atlas Vector Search (`cat_library`).
- **Hybrid Search**: **Vector(의미)** + **Keyword(BM25)** 검색 결과를 **RRF(Reciprocal Rank Fusion)** 알고리즘으로 재정렬하여 정확도를 극대화했습니다.
- **Data Pipeline**: `TheCatAPI`, `Wikipedia`, `BemyPet` 데이터를 수집하여 전처리(Clean) → 임베딩(Embed) → 적재(Load)하는 자동화 파이프라인(V3)을 구축했습니다.

---

## 5. 디렉토리 구조 (Directory Structure)
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

---

## 6. 설치 및 실행 (Installation & Execution)
본 문서는 프로젝트 가동을 위한 **실제 실행 루틴(Execution Routine)**을 중심으로 기술합니다.

### 1단계: 환경 설정 (Setup)
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env 파일 생성)
# OPENAI_API_KEY=sk-...
# MONGO_V3_URI=mongodb+srv://...
# THECATAPI_API_KEY=...
# OPENAPI_API_KEY=... (공공데이터포털 디코딩 키)
```

> [!TIP]
> **LLM 모델 변경**: `src/core/config.py`의 `LLMConfig` 클래스에서 `ROUTER_MODEL`(분류용)과 `BASIC_MODEL`(생성용)을 변경할 수 있습니다. (기본값: `gpt-4.1-nano` / `gpt-4o-mini`)

### 2단계: 데이터 파이프라인 가동 (Data Pipeline V3)
원천 데이터 수집부터 검색 엔진 적재까지의 전체 자동화 공정입니다.

**Step 1. 원천 데이터 수집 (Crawl)**
```bash
python scripts/crawl/crawl_thecatapi.py  # 결과: data/raw/cat_breeds_thecatapi.json
python scripts/crawl/crawl_wiki.py       # 결과: data/raw/cat_breeds_wiki_info.json
python scripts/crawl/crawl_bemypet.py    # 결과: data/raw/bemypet_catlab.json
```

**Step 2. 데이터 통합 (Integration)**
```bash
# 묘종 마스터 데이터 통합 및 정규화
python scripts/process/preprocess_integrated_breeds.py  # 결과: data/cat_breeds_integrated.json
```

**Step 3. 도메인 사전 빌드 (Vocab)**
```bash
# 형태소 분석을 위한 고양이 전문 용어 사전 구축
python scripts/build_domain_dict.py      # 결과: src/core/tokenizer/domain_dictionary.txt
```

**Step 4. V3 파이프라인 실행 (Pipeline V3)**
```bash
# 1. 아티클 데이터 처리 (전처리 -> 임베딩 -> 적재)
python scripts/v3/run_preprocess.py      # 결과: data/v3/processed.json

# 2. 묘종 데이터 통합 처리 (정책 기반 필터링 + 이미지 매칭)
python scripts/process_breeds_v3.py      # 결과: MongoDB cat_library.care_guides
```

### 3단계: 애플리케이션 실행 (Application)
```bash
streamlit run src/ui/app.py
```

---

## 7. 실험 및 벤치마크 (Notebooks)
`src/notebooks/` 디렉토리의 Jupyter Notebook을 통해 각 모듈의 성능을 검증할 수 있습니다.

- **검색 성능 평가 (Retrieval Evaluation)**:
  - **[`analysis_retriever_comparison.ipynb`](src/notebooks/analysis_retriever_comparison.ipynb)**: BM25/Vector/Hybrid 모델 성능 비교.
  - **[`analysis_hybrid_metrics.ipynb`](src/notebooks/analysis_hybrid_metrics.ipynb)**: Hybrid Search (RRF) 상세 분석 (Hit@K, MRR).
- **정성 평가 (Advanced Evaluation)**:
  - **[`analysis_llm_judge.ipynb`](src/notebooks/analysis_llm_judge.ipynb)**: LLM(Judge)을 활용한 검색 품질 및 답변 정확도 평가.
- **단위 테스트 (Unit Test)**:
  - **[`tokenizer_experiment.ipynb`](src/notebooks/tokenizer_experiment.ipynb)**: Kiwi 형태소 분석기 및 도메인 사전 성능 실험.
  - **[`agent_prompt_experiment.ipynb`](src/notebooks/agent_prompt_experiment.ipynb)**: 전문가 에이전트 페르소나 및 프롬프트 최적화 테스트.

---

## 8. 문서 인덱스 (Index)
프로젝트에 대한 더 자세한 내용은 `docs/` 디렉토리의 아래 문서들을 참고하세요.

### 📜 협업 가이드 (Collaboration)
- **[01. Coding Convention](docs/03_convention_and_guides/01_coding_convention.md)**: 코드 스타일 및 컨벤션
- **[02. Git Process](docs/03_convention_and_guides/02_git_process.md)**: 브랜치 전략 및 커밋 규칙
- **[03. PR Guide](docs/03_convention_and_guides/03_pr_guide.md)**: PR 템플릿 및 리뷰 프로세스
- **[04. Env & Secrets](docs/03_convention_and_guides/04_env_secrets.md)**: 환경변수 및 보안 가이드

### 🏗️ 아키텍처 (Architecture)
- **[01. Project Structure](docs/02_system_architecture/01_structure.md)**: 디렉토리 구조 설명
- **[02. LangGraph Architecture](docs/02_system_architecture/02_langgraph_arch.md)**: 에이전트 그래프 상세 설계

### 📁 기타 문서
- **[docs/01_project/overview.md](docs/01_project/overview.md)**: 프로젝트 개요 및 상세 기획
- **[docs/07_report/checklist.md](docs/07_report/checklist.md)**: 프로젝트 진행 상황 체크리스트
- **[docs/07_report/roadmap_backlog.md](docs/07_report/roadmap_backlog.md)**: 향후 로드맵 및 백로그

---

## 9. 회고 (Retrospective)

### 임도형
- 프로젝트 RAG 구조, 전처리, UI 코드 진행
- 도메인 전문가가 있어야한다는 중요성을 깨달았고, 타겟 유저에 대해 적절한 설문조사가 선행되어야 더 질 좋은 프로젝트가 될 것 같습니다!

### 최민호
- 도메인 시장 조사, UI 도안, 자료 조사 및 테스트 진행
- 시장 확신: 국내 반려묘 개체 수의 가파른 증가와 일본식 '네코노믹스' 현상 재현을 수치로 확인하며 고양이 특화 서비스의 충분한 시장성을 확신했습니다.

기술 혁신: 규칙 기반 시스템의 한계를 넘어 LLM의 가변성과 멀티모달 통합(울음소리, 이미지 분석)이 가져올 사용자 경험의 파괴적 혁신을 설계했습니다.

신뢰 자산: RAG(검색 증강 생성) 기술을 통해 검증된 수의학 정보를 결합하여 서비스의 신뢰도와 전문성을 확보하는 것이 핵심 성공 요인임을 재확인했습니다.

다음프로젝트를 통해 유저입장에 app을 구현하기 위한 고민을 해봅시다!

### 정세환
- 프롬프트 엔지니어링, 프롬프트 구조 제안 및 가드레일/안정성 테스트 진행
- LLM을 활용해 챗봇 서비스를 만드는 과정이 눈에 보여서 즐거웠고, 파인튜닝의 중요성을 직접 체감할 수 있는 경험이었습니다.

### 문승준
- 프로젝트 점검 체크리스트, API 조사 및 명세, 프롬프트 테스트 진행
- 다들 정말 적극적으로 참여하셨고, 특히 프롬프트의 가드레일 테스트 시 정말 창의적인 방향으로 오작동할 수 있다는 점을 검토하시는 것을 보고서 굉장히 큰 인상을 받았습니다. 단순히 공부가 부족한 것과 별개로 사고방식 자체가 제가 많이 경직되었다는 것을 느꼈어요. 여러모로 견문을 넓힐 수 있는 좋은 기회였다고 생각합니다.
