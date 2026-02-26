# 📋 프로젝트 진행 체크리스트 (Detailed Status Table)

본 문서는 `SKN22-3rd-3Team` 프로젝트의 개발 현황을 **냉철하고 팩트 중심**으로 점검한 결과입니다.

**상태 범례**:
- ✅ **완료 (Done)**: 구현 및 코드 레벨 검증 완료.
- ⚠️ **부분 완료 (Partial)**: 구현은 되었으나 검증이 부족하거나 개선이 필요함.
- 🛑 **미진행 (Not Started)**: 기획 단계에 있거나 구현되지 않음.

---

| 구분 (Category) | 점검 항목 (Check Item) | 세부 검증 내용 (Validation Criteria) | 상태 |
|:--- |:--- |:--- |:---:|
| **1. 기획 (Overview)** | **핵심 가치 (Value Proposition)** | 단순 검색이 아닌 '나만의 맞춤형 집사(Butler)' 페르소나 구현 | ✅ |
| | | 사용자(초보/경력 집사)의 상황에 따른 차별화된 경험 제공 | ⚠️ |
| | **온보딩 (Onboarding)** | 거주환경/활동량/성향 데이터 수집 및 추천 로직 반영 | ✅ |
| | | 사용자 이탈을 막을 만큼 매력적인 UI/UX 제공 | 🛑 |
| | **평가지표 (KPI)** | 추천 정확도(Relevance) 또는 사용자 만족도(Engagement) 기준 수립 | 🛑 |
| | | **LangSmith 트레이스를 통한 라우팅 정확도 90% 달성 등 자동화 측정** | 🛑 |
| **2. 아키텍처 (Structure)** | **패키지 구조 (Package)** | `core`, `agents`, `retrieval`, `ui` 등 역할과 책임 분리 | ✅ |
| | | 순환 참조(Circular Dependency) 문제 해결 | 🛑 |
| | **리팩토링 (Refactoring)** | 하드코딩된 설정값의 환경변수(`.env`) 및 `config.py` 중앙화 | ✅ |
| | | 중복 로직(DB 연결 등)을 유틸리티/싱글톤으로 통합 | ✅ |
| | **테스트 전략 (Testing)** | 단위 테스트: 노드별(`head_butler`, `matchmaker`) 독립 동작 검증 | ✅ |
| | | 통합 테스트: 전체 그래프(`graph.py`) 흐름 연결 검증 (`verify_agents_e2e.py`) | ✅ |
| **3. 데이터 (Data Pipeline)** | **데이터 소스 (Source)** | 품종 데이터 확보 (TheCatAPI + Wikipedia, 67종) | ✅ |
| | | 케어 가이드 확보 (BemyPet Catlab, 1,153건) | ✅ |
| | | 유기묘 정보 연동 (국가동물보호정보시스템 OpenAPI) | ✅ |
| | **데이터 전처리 (Preprocessing)** | v1~v3 파이프라인 구축 (분류, 다중 라벨링, 페르소나 매핑) | ✅ |
| | | **한국어 형태소 분석 (Kiwi 적용)** 및 사전(도메인, 단어, 불용어, 동의어) 구축 | ✅ |
| | | 중복 데이터 제거 및 결측치(Null) 처리 | ✅ |
| | **데이터 검증 (Validation)** | `pydantic` 모델 기반 데이터 스키마(Schema) 엄격 검증 | ✅ |
| **4. 검색 (Retrieval)** | **임베딩 모델 (Embedding)** | **비용/성능을 고려한 모델 선정 근거 (`text-embedding-3-small` vs Others)** | ⚠️ |
| | **하이브리드 검색 (Hybrid)** | 벡터(Vector) + 키워드(BM25) 검색 적용 | ✅ |
| | | **RRF (Reciprocal Rank Fusion)** 기반 순위 재산정 | ✅ |
| | | Specialist 태그 기반 Pre-filtering 적용 | ✅ |
| | | Hit@3, MRR 등 검색 성능 지표 측정 | ✅ |
| | **파라미터 튜닝** | Context Window 효율성을 위한 `limit=3` 설정 근거 확보 | ✅ |
| **5. 데이터베이스 (DB)** | **스키마 설계 (Schema)** | MongoDB의 장점을 살린 비정형 데이터/메타데이터 수용 | ✅ |
| | | 컬렉션 분리 전략 (`breeds` vs `care_guides`) | ✅ |
| | **인덱싱 (Indexing)** | Atlas Search 인덱스(`default`, `vector_index`) 매핑 코드 일치 | ✅ |
| | | **Nori 형태소 분석기 (Atlas Search Analyzer) 적용** | 🛑 |
| | **보안 (Security)** | DB 접속 정보의 코드 분리 및 안전한 관리 (`.env`) | ✅ |
| **6. UI/UX (Frontend)** | **디자인 시스템** | Glassmorphism(유리 질감) 테마 적용 (`style.css`) | ⚠️ |
| | **사용자 경험 (UX)** | 로딩 화면(Splash Screen) 및 'Thinking...' 상태 시각화 | ✅ |
| | **투명성 (Transparency)** | AI 답변의 근거(Reasoning)를 보여주는 Debug UI 제공 | ✅ |
| | **세션 관리 (Session)** | 새로고침 시에도 대화 맥락이 유지되도록 `thread_id` 관리 | ✅ |
| **7. 에이전트 (Agentic)** | **LangGraph 설계** | Head Butler -> Expert -> End 계층 구조 확립 | ✅ |
| | | 그래프 토폴로지 연결 검증 (Graph Visualization) | ✅ |
| | **라우팅 (Routing)** | Few-Shot Prompting을 통한 문맥 기반 분류 | ✅ |
| | | 단순 키워드가 아닌 **'핵심 의도(Intent)'** 파악 정확도 개선 | ✅ |
| | **페르소나 (Persona)** | `Matchmaker`, `Physician` 등 전문가별 역할/데이터 격리 | ✅ |
| | **상태 관리 (State)** | `AgentState`를 통한 데이터 무손실 전달 | ✅ |
| **8. 운영 (Deployment)** | **이식성 (Portability)** | `.gitignore` 및 `requirements.txt` 의존성 관리 | ✅ |
| | **문서화 (Documents)** | `README.md` 만으로 실행 가능한 가이드 제공 | ✅ |
| | | 아키텍처 다이어그램 최신화 상태 유지 | ✅ |
| **9. 효율성 (Efficiency)** | **토큰 절약** | **Distillation(요약)** 전략으로 Head Butler 입력 비용 절감 | ✅ |
| | **비동기 처리** | `asyncio` 기반 Non-blocking 에이전트 실행 | ✅ |
| | **캐싱 (Caching)** | **Redis 등을 활용한 임베딩 검색 결과 캐싱** | 🛑 |
| **10. 안정성 (Robustness)** | **루프 방지** | Recursion Limit 및 명확한 종료 조건 설정 | ✅ |
| | **Fallback 라우팅** | 분류 실패 시 `general` 노드로 안전하게 연결 | ✅ |
| | **할루시네이션 방지** | 프롬프트 내 "Unknown Defense" 및 9단계 방어 기제 | ✅ |
| **11. 확장성 (Scalability)** | **멀티모달 (Vision)** | **이미지 인식(고양이 사진 분석) 기능 확장** | 🛑 |
| | **안전 가드레일** | 독극물/학대 등 유해 정보에 대한 필터링/경고 로직 | ✅ |
