# 🗺️ ZIPSA Roadmap & Tasks (GitHub Issues)

본 문서는 프로젝트의 마일스톤(Roadmap)과 이를 달성하기 위한 구체적인 실행 계획(Tasks)을 통합 관리합니다.
**GitHub 이슈 등록 시, 각 항목의 제목을 이슈 제목으로 사용하세요.**

---

## 🚀 Phase 1: 챗봇 응답 고도화 및 통합 시나리오 검증 (Current)
> **목표**: 사용자 의도 파악(필터링) 정교화 및 3-Node 에이전트 시스템의 시나리오별 무결성 검증.

- [ ] **자연어 필터링 정책 고도화 (Breed Filtering Policy)**
    - 목표: 사용자의 자연어 표현을 숫자로 된 데이터 필터로 정확히 변환.
    - **Draft Policy (예시)**:
        - *Shedding*: "털 안 빠지는" -> `shedding_level <= 2`
        - *Energy*: "얌전한/아파트용" -> `energy_level <= 2`, "활발한" -> `energy_level >= 4`
        - *Friendly*: "초보/아이 있는 집" -> `child_friendly >= 4`
- [ ] **통합 테스트 시나리오 설계 및 실행**
    - **Plan**: 에이전트별 Happy/Bad Path, 멀티턴 대화 등을 포함한 상세 시나리오 문서(`test_plan.md`) 작성.
    - **Execution (필수 시나리오 예시)**:
        - `Liaison` (유기묘): "서울에 있는 렉돌 유기묘 알아봐줘. 입양 주의점도 알려줘." (Tool + RAG Hybrid 응답 검증)
        - `Matchmaker` (품종): "혼자 사는데 외로움 많이 타는 개냥이 추천해줘." (모순된 요구사항에 대한 논리적 추론 및 대안 제시 검증)
        - `Defense` (예외 처리): 프롬프트 인젝션 방어 및 제공 불가능한 서비스 정중한 거절.
    - *Note*: 두 에이전트의 목적과 UX가 섞이지 않도록 엄격히 분리 테스트 수행.

---

## 🎨 Phase 2: Full-Stack 아키텍처 구축 및 개인화 (Next.js + FastAPI)
> **목표**: 통합 API 서버(FastAPI)와 Frontend(Next.js)를 구축하여, 회원가입 기반의 개인화 서비스 및 UI/UX 완성.

### 2.1 Core Architecture & Backend Integration
- [ ] **MongoDB 통합 유저 데이터 (users) 컬렉션 스키마 문서화**
    - 가입 내역, 세션 키 연동 및 1:N 구조 (사용자 1명 -> N마리의 `UserCat`, N개의 `ChatSession`) 설계.
- [ ] **Pydantic 기반 통합 `User DTO` 모델 클래스 코어 구현**
    - 기존 `user_profile.py`의 제약 조건/선호도 데이터를 `preferences` 속성으로 흡수하는 통합 클래스 작성.
- [ ] **통합 인터페이스 및 프론트/백엔드 명세서 정의**
    - **API 명세서**: FastAPI 통신을 위한 RESTful Endpoint(URL, Request/Response 스키마 등) 규칙 설계 및 문서화.
    - **Page 명세서**: Next.js App Router 기반의 페이지 경로(Routes), 화면별 요구사항, 상태 관리 흐름 정의.
- [ ] **FastAPI 코어 서버 및 LangServe 라우팅 엔드포인트 세팅**
    - `LangServe`를 활용하여 에이전트 그래프(`graph.py`)를 즉시 통신 가능한 REST API 형태로 서빙.
- [ ] **대화 히스토리 Trimming 및 Token Management 로직 구현**
    - 턴당/세션당 최대 토큰 제한(`max_tokens`) 제어 및 장기 대화 안정성 확보 로직 선행 구현.
- [ ] **프론트-백엔드 연동을 위한 LangSmith 기본 로깅 세팅**
    - 현재 프로젝트에 연동된 `LangSmith` Tracing 환경을 유지하여 기능 개발 중 발생하는 버그 및 에이전트 동작 추적.
- [ ] **개인정보 보호(PII) 마스킹 처리 구현**
    - **PII Masking**: LangSmith 전송 전 민감정보(전화번호, 주소 등) 마스킹 처리 (Privacy).
- [ ] **프론트엔드 연동을 위한 상태 관리 및 통신 아키텍처 수립**
    - Streamlit 제거 후 **Next.js (React)** 전환에 따른 Vercel AI SDK 호환 및 대화 상태 관리 전략 수립.
- [ ] **API 통신 장애 대응(Graceful Fallback) 에러 핸들링 로직 구현**
    - LLM/검색 API 통신 실패 및 타임아웃 발생 시 서버가 죽지 않고 프론트엔드에 미리 정의된 "기본 응답 메세지"를 반환.

### 2.2 Global Auth & Onboarding Flow
- [ ] **프론트엔드: NextAuth.js 기반 SSO 인증 아키텍처 연동**
    - **SSO Login**: 프론트엔드 **NextAuth.js**가 전담하며, **Google, 카카오, 네이버** 기반 소셜 로그인으로 구현.
    - **Backend Sync**: 프론트에서 소셜 로그인 인증을 통과시킨 유저의 식별자를 백엔드(FastAPI)로 전달하여 DB와 동기화하는 로직 연결.
- [ ] **프론트엔드: 신규 유저 온보딩(Onboarding) 프로필 설정 UI**
    - **Forms**: 기존 터미널 기반 `onboarding.py` 기능을 웹 폼으로 전환 (주거형태, 알레르기 등 수집).
    - **Integration**: 수집된 초기 프로필 정보를 백엔드의 `User Entity` 규격에 맞게 전송(PATCH)하여 프로필 완성.

### 2.3 Core App UI & Components
- [ ] **통합 CatCard UI 컴포넌트 설계 및 DTO 개편**
    - **Modeling**: 유기동물(`Abandoned`), 품종추천(`Recommend`), **사용자 반려묘(`UserCat`)** 데이터의 공통 속성 통합 (`BaseCatCard` 상속 구조).
    - **UI Definition**: 텍스트 위주 정보를 시각적 카드(이미지, 핵심 태그, 요약) 형태로 변환하기 위한 공통 React Component 설계.
    - **Interactive Text**: LLM 응답 내 고양이 이름 호버 시 해당 Data Model과 연동된 카드 팝오버 노출 기능.
- [ ] **채팅 세션(Chat History) DTO 및 사이드바 UI 설계**
    - **DB Schema**: `ChatSession`(방)과 `ChatMessage`(메시지 내역) 계층 구조 설계 (MongoDB).
    - **API & DTO**: `SessionListResponse` (과거 대화 목록), `SessionDetailResponse` (특정 대화 내역 전체 로드) 명세 작성.
    - **UI Definition**: 과거 대화 내역 사이드바(Drawer) 및 라우팅(`chat/[id]`) 기능을 갖춘 레이아웃 컴포넌트 개발.

### 2.4 Viral Marketing & User Hook
- [ ] **'건방진 냥심 번역기' (Meme Generator) 모달/렌더링 UI 개발**
    - 챗봇 내부가 아닌, 독립된 웹 페이지(`/meme` 등) 모달. 사용자가 업로드한 고양이를 인스타그램용 '폴라로이드 짤(Meme)' 형태로 시각화.
- [ ] **Vision AI 연동 및 시니컬 텍스트 생성 API 구축**
    - 고양이 사진(표정, 자세, 주변 상황)을 분석하여 도도하고 시니컬한 시점의 유머러스한 밈 텍스트(속마음) 생성 로직.
- [ ] **생성 결과물 기반의 `UserCat` 프로필 1-Click 업데이트 연동**
    - 밈 결과물 확인 후 **"이 건방진 냥이를 내 프로필(`UserCat`)에 등록할까요?"** 버튼 클릭 시, 대표 사진과 밈 텍스트를 함께 DB에 저장.

---

## 🏗️ Phase 3: 운영 환경 구축 및 보안 안정화 (Launch Ops)
> **목표**: MVP 런칭을 위한 인프라 구축 및 서비스 안정성 확보.

### 3.1 Infrastructure & Deployment
- [ ] **도커(Docker) 컨테이너 분리 환경 구축**
    - **Containerization**: App(FastAPI) + Redis 컨테이너화 (`docker-compose`).
    - **DB (MongoDB)**: Vector Search 기능 사용을 위해 로컬 컨테이너 대신 **클라우드(MongoDB Atlas)** 연동 구성 유지.
    - **Redis 사용처**: (1) 대화 세션별 Memory(대화 이력) 읽기/쓰기, (2) **반복 쿼리 캐싱(Cache)을 통한 응답 속도 최적화**, (3) Rate Limiting(트래픽 제어) 상태 저장.
- [ ] **클라우드 실서버 배포 (OCI - Oracle Cloud Infrastructure)**
    - RAM 용량(최소 2GB 이상 요구) 확보를 위해 AWS 프리티어 대신 **OCI Always Free (ARM Ampere A1)** 인스턴스 프로비저닝.
    - 도커 이미지를 ARM 아키텍처에 맞게 빌드 및 실서버 배포 실행.
- [ ] **GitHub Actions 기반 CI/CD 파이프라인 자동화**
    - **CI Flow**: 새로운 PR 생성 시 모든 테스트(`pytest`) 모듈 자동 수행.
    - **CD Flow**: `Main` 병합 시 OCI 서버에 변경사항 자동 빌드 및 배포 트리거 동작.

### 3.2 Traffic Control & Service Operations
- [ ] **트래픽 관리 및 레이트 리미팅(Rate Limiting) 적용**
    - **Rate Limiting**: FastAPI `slowapi` 및 Cloudflare WAF 설정을 통한 DDoS/Abuse 방지.
- [ ] **사용자 피드백 루프 및 개선 프로세스 정립**
    - 주간 리뷰: 하위 평점(👎) 답변 분석 -> 프롬프트 개선 -> 재배포 프로세스 정립.

---

## 🚀 Phase 4: 커뮤니티 확장 및 플랫폼화 (Future Vision)
> **목표**: 서비스 안착 및 트래픽 수익화 이후, 고양이 사진 기록을 중심으로 한 소셜 플랫폼('캣스타그램')으로의 Pivoting 및 대규모 구조 개편

### 4.1 Social Features & Storage Scaling
- [ ] **'캣스타그램' 기반 사진 누적 아카이빙 (List[Photo]) 스키마 마이그레이션**
    - **Data Migration**: 초기 1마리 1대표사진 정책(덮어쓰기)에서 탈피하여, `UserCat` 내 다중 사진(Meme 포함) 히스토리를 시계열로 누적 저장하는 `List[Photo]` 구조로 확장.
    - **Infrastructure Requirement**: 막대한 이미지 CDN/Object Storage 비용을 감당할 수 있는 트래픽 수익(BM) 구조가 마련된 이후 실행.

### 4.2 Data & AI Ops
- [ ] **LangSmith 기반 KPI 운영 대시보드 고도화 및 모니터링**
    - 누적된 트래픽 로그를 바탕으로 E2E Latency, Token Usage, Error Rate 등 본격적인 대용량 서비스 운영 KPI 추적 대시보드 고도화.
- [ ] **Routing Accuracy 자동 테스트셋 정교화**
    - 라우터의 의도 파악 및 분기 정확도(95% 이상 목표)를 정기적으로 검증하는 커스텀 데이터셋(`pytest` 연동) 구축 및 파이프라인 연동.

---

## 🛠️ Continuous Improvement (운영 유지보수)
- [ ] **핵심 로직 테스트 코드 의무화 정책 수행**
    - 통합 테스트뿐 아니라, 각 에이전트의 노드 함수(`def matchmaker_node(...)` 등) 단위에서 입출력 검증(`pytest`)을 70% 이상 달성.
- [ ] **DB-에이전트 태그 싱크로나이저 자동화 배치 (Scripting)**
    - MongoDB 실제 데이터 내에 존재하는 태그 목록과 `care_team.py` 등에서 라우터가 식별하는 하드코딩 태그 리스트 간 불일치(Mismatch)를 매일 1회 체크하여 경고를 띄우는 자동 검증 봇 로직 작성.

---
**Last Updated**: 2026-02-24
