# ZIPSA Roadmap

프로젝트 로드맵 및 실행 계획입니다. 완료된 작업은 [completed_work.md](./completed_work.md)를 참조하세요.

---

## Phase 1: 챗봇 MVP

> 사용자 의도 파악 정교화 및 에이전트 시스템 무결성 검증

### 1.1 완료 항목

LangGraph 에이전트, Hybrid RAG, 데이터 파이프라인, UI 등 → [completed_work.md](./completed_work.md) 참조

### 1.2 개선 필요 항목

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | 자연어 필터링 정책 정의 | 사용자 표현 → MongoDB 쿼리 필터 변환 규칙 |
| ⬜ | 필터 모듈 구현 | `src/agents/filters/breed_criteria.py` 신규 작성 |
| ⬜ | 통합 테스트 시나리오 | 에이전트별 Happy/Bad Path, 멀티턴 대화 검증 |
| ⬜ | 프롬프트 인젝션 방어 테스트 | 악의적 입력 탐지 및 정중한 거절 검증 |

---

## Phase 2: Full-Stack 아키텍처 구축

> 통합 API 서버(FastAPI)와 Frontend(Next.js) 구축, 회원 기반 개인화 서비스

### 2.1 Backend Integration

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | MongoDB 유저 스키마 문서화 | users, UserCat(1:N), ChatSession(1:N) 구조 설계 |
| ⬜ | User DTO 통합 모델 | 기존 `user_profile.py` → `preferences` 속성으로 흡수 |
| ⬜ | API 명세서 정의 | FastAPI RESTful Endpoint (URL, Request/Response 스키마) |
| ⬜ | Page 명세서 정의 | Next.js App Router 경로, 화면별 요구사항, 상태 관리 흐름 |
| ⬜ | FastAPI + LangServe 세팅 | `graph.py`를 REST API로 서빙 |
| ⬜ | 토큰 관리 로직 | 턴당/세션당 max_tokens 제한, 히스토리 trimming |
| ⬜ | LangSmith 로깅 세팅 | 프론트-백엔드 연동 환경에서 버그/에이전트 동작 추적 |
| ⬜ | PII 마스킹 처리 | LangSmith 전송 전 민감정보(전화번호, 주소) 마스킹 |
| ⬜ | 상태 관리 아키텍처 | Streamlit 제거 → Vercel AI SDK 호환, 대화 상태 관리 전략 |
| ⬜ | Graceful Fallback | LLM/검색 API 장애 시 기본 응답 메시지 반환 |

### 2.2 Auth & Onboarding

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | NextAuth.js SSO 연동 | Google, Kakao, Naver 소셜 로그인 |
| ⬜ | Backend Sync | 프론트 인증 → 유저 식별자 → FastAPI → DB 동기화 |
| ⬜ | 온보딩 UI | 기존 터미널 `onboarding.py` → 웹 폼 전환 (주거형태, 알레르기 등) |
| ⬜ | 프로필 완성 API | 초기 프로필 → User Entity 규격 PATCH 전송 |

### 2.3 Core UI Components

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | CatCard 통합 모델링 | Abandoned, Recommend, UserCat → `BaseCatCard` 상속 구조 |
| ⬜ | CatCard React 컴포넌트 | 이미지, 핵심 태그, 요약 카드 형태 UI |
| ⬜ | Interactive Text | LLM 응답 내 고양이 이름 호버 → 카드 팝오버 노출 |
| ⬜ | ChatSession 스키마 | ChatSession(방) + ChatMessage(메시지) 계층 구조 |
| ⬜ | Session API & DTO | `SessionListResponse`, `SessionDetailResponse` 명세 |
| ⬜ | 채팅 히스토리 UI | 과거 대화 사이드바(Drawer), `chat/[id]` 라우팅 |

### 2.4 Viral Feature

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | 냥심 번역기 UI | `/meme` 페이지, 폴라로이드 짤 형태 렌더링 |
| ⬜ | Vision AI 연동 | 고양이 사진 분석 → 시니컬한 밈 텍스트 생성 |
| ⬜ | UserCat 1-Click 등록 | 밈 결과물 → 내 프로필에 등록 버튼 |

---

## Phase 3: 배포 및 운영

> MVP 런칭을 위한 인프라 구축 및 서비스 안정성 확보

### 3.1 Infrastructure

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | Docker Compose | App(FastAPI) + Redis 컨테이너화 |
| ⬜ | Redis 활용 | (1) 세션 메모리 (2) 반복 쿼리 캐싱 (3) Rate Limiting 상태 |
| ⬜ | OCI 배포 | Oracle Cloud ARM Ampere A1 (Always Free, 2GB+ RAM) |
| ⬜ | GitHub Actions CI | PR 생성 → pytest 자동 수행 |
| ⬜ | GitHub Actions CD | Main 병합 → OCI 자동 빌드/배포 |

### 3.2 Operations

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | Rate Limiting | FastAPI slowapi + Cloudflare WAF (DDoS/Abuse 방지) |
| ⬜ | 피드백 루프 | 주간 리뷰: 하위 평점 답변 분석 → 프롬프트 개선 → 재배포 |

---

## Phase 4: 플랫폼 확장 (Future)

> 서비스 안착 후 소셜 플랫폼 전환

### 4.1 Social Features

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | 캣스타그램 스키마 | UserCat 내 `List[Photo]` 시계열 누적 저장 구조 |
| ⬜ | 이미지 CDN/Object Storage | 클라우드 이미지 저장소 구축 (트래픽 수익 확보 후) |

### 4.2 Data & AI Ops

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | KPI 대시보드 | LangSmith 기반 E2E Latency, Token Usage, Error Rate 추적 |
| ⬜ | 라우팅 정확도 테스트 | 95% 목표, pytest 연동 커스텀 데이터셋 |

---

## Continuous Improvement

| 상태 | 작업 | 설명 |
|:---:|------|------|
| ⬜ | 테스트 커버리지 | 핵심 노드 함수 pytest 70% 이상 |
| ⬜ | 태그 싱크 검증 | DB 태그 ↔ 에이전트 하드코딩 태그 일치 확인 (일일 배치) |

---

**Last Updated**: 2026-02-26
