# 📄 Documentation (`docs/`)

본 디렉토리는 프로젝트의 비전 기획부터 기술적 설계 규격, 파이프라인 전략 및 실무 가이드를 관리하는 통합 문서 보관소입니다.

---

## 📂 디렉토리 및 핵심 파일 명세

### 1. [01_project](./01_project) (비전 및 구조)
- **`overview.md`**: 전담 전문가 에이전트 시스템(ZIPSA)의 기획 의도와 핵심 가치 제언.
- **`personas.md`**: `Head Butler`, `Matchmaker`, `Physician` 등 4대 전문가 페르소나의 행동 강령 및 역할 정의.

### 2. [02_system_architecture](./02_system_architecture) (시스템 아키텍처)
- **`01_structure.md`**: 프로젝트 디렉토리 구조 및 핵심 모듈 설명.
- **`02_langgraph_arch.md`**: LangGraph 기반의 Multi-Agent 아키텍처 및 데이터 흐름 다이어그램.

### 3. [03_convention_and_guides](./03_convention_and_guides) (협업 가이드)
- **`01_coding_convention.md`**: Python 코드 스타일 및 명명 규칙.
- **`02_git_process.md`**: Git 브랜치 전략 및 커밋 컨벤션.
- **`03_pr_guide.md`**: Pull Request 작성 및 리뷰 가이드.
- **`04_env_secrets.md`**: 환경 변수 및 시크릿 관리 보안 지침.

### 4. [04_api](./04_api) (외부 연동 규격)
- **`thecatapi_spec.md` / `thecatapi-oas.yaml`**: TheCatAPI 기반 묘종 데이터 수집 인터페이스 정의.
- **`openapi_spec.md`**: 국가동물보호정보시스템 V2 API 명세 (유기동물 조회 등).

### 5. [05_data](./05_data) (데이터 전략)
- **`v3_pipeline_strategy_report.md`**: 검색 품질을 위한 **구조적 임베딩(Structured Embedding)** 전략 보고서.
- **`data_preprocessing_report_v3.md`**: V3 데이터 정제 및 메타데이터 추출 결과.

### 6. [06_feature](./06_feature) (기능 명세)
- **`auth_profile_spec.md`**: 사용자 인증 및 반려묘 프로필 관리 로딕 상세.
- **`cat_card_spec.md`**: 묘종 검색 결과 시각화(Cat Identity Card) 컴포넌트 규격.

### 7. [07_report](./07_report) (성과 관리)
- **`checklist.md`**: 프로젝트 완성도 자가 점검 및 11개 영역별 피드백 리스트.
- **`roadmap_backlog.md`**: 향후 고도화 로드맵 및 기능 백로그.

