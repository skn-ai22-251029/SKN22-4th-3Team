# Page 명세서

## 1. 개요

Next.js App Router 기반 ZIPSA 프론트엔드의 페이지 구조, 화면별 요구사항, 상태 관리 흐름을 정의합니다.

---

## 2. App Router 경로 구조

```
/
├── login                            # 소셜 로그인 페이지
├── auth
│   ├── callback                     # OAuth 콜백 처리
│   └── error                        # 인증 오류 페이지
├── onboarding                       # 온보딩 (프로필 미완료 시 필수)
├── chat                             # 새 채팅 → 세션 생성 후 리다이렉트
│   └── [id]                         # 채팅 세션
├── my-cats                          # 내 고양이 목록
│   ├── new                          # 고양이 등록
│   └── [id]                         # 고양이 상세/수정
├── meme                             # 냥심 번역기 (Vision AI)
└── profile                          # 내 프로필 설정
```

**API Routes**

```
/api/auth/[...nextauth]              # NextAuth OAuth 핸들러 (SDK 자동)
```

---

## 3. 접근 제어 (Middleware)

보호 경로: `/chat/:path*`, `/onboarding/:path*`, `/profile/:path*`, `/my-cats/:path*`, `/meme/:path*`

```
미인증 → 보호 경로 접근 시 NextAuth 기본 동작 (로그인 페이지 리다이렉트)
인증 완료 → 정상 접근
```

`/login`은 NextAuth의 커스텀 `signIn` 페이지로, 인증된 사용자 접근 시 NextAuth가 `/chat`으로 리다이렉트합니다.

---

## 4. 화면별 요구사항

---

### 4.1 로그인 — `/login`

**목적**: NextAuth.js SSO 로그인 진입점

**UI 구성**
- ZIPSA 로고 + 서비스 소개 문구
- 소셜 로그인 버튼: Google, Kakao, Naver

**완료 후 흐름**
1. NextAuth OAuth 콜백 → `POST /api/v1/auth/sync` 호출 (ZIPSA JWT 발급)
2. 온보딩 미완료(`user_profiles` 없음) → `/onboarding`
3. 온보딩 완료 → `/chat`

**관련 이슈**: #25, #26

---

### 4.2 온보딩 — `/onboarding`

**목적**: 맞춤 추천을 위한 집사 환경 정보 수집 (최초 1회)

**UI 구성** (단계별 진행)

| 단계 | 항목 |
|---|---|
| 1 | 닉네임 입력 |
| 2 | 거주 형태 선택 (아파트 / 주택 / 원룸) |
| 3 | 일상 활동량 선택 (정적 / 보통 / 활동적) |
| 4 | 고양이 양육 경험 (초보 / 경력 / 베테랑) |
| 5 | 동거인 선택 (어린 아이 / 강아지 / 혼자 / 가족) |
| 6 | 알레르기 여부, 원하는 고양이 성향 태그 선택 |

**완료 후 흐름**
- `POST /api/v1/users/me/profile` 호출
- `/chat`으로 이동

**관련 이슈**: #27

---

### 4.3 채팅 — `/chat/[id]`

**목적**: AI 집사(ZIPSA)와 고양이 품종 매칭 및 케어 상담

**UI 구성**

```
┌─────────────────────────────────────────────────┐
│  [GlobalDrawer 사이드바]   [채팅 영역]           │
│  - 세션 히스토리           - 메시지 스트리밍     │
│  - 새 채팅 버튼            - 인터랙티브 텍스트   │
│                            [결과 패널]           │
│                            - CatCard (최대 3종)  │
│                            - RAG 출처 문서       │
│                            - 유기묘 정보 카드    │
│  ────────────────────────────────────────────── │
│                       [채팅 입력창]              │
└─────────────────────────────────────────────────┘
```

**기능 요구사항**

- 스트리밍 응답: `POST /api/v1/chat/stream` (SSE)
- 세션 목록 사이드바: `GET /api/v1/users/me/sessions`
- 메시지 히스토리: `GET /api/v1/users/me/sessions/{id}/messages`
- CatCard 패널: 추천 품종 최대 3종, 레이더 차트 포함 (#30)
- 유기묘 카드: Liaison 에이전트 응답 시 RescueCatCard 표시 (#29)
- `/chat` 접근 시 자동으로 새 세션 생성 후 `/chat/[id]`로 리다이렉트

**Zustand 전역 상태**
- 세션 목록, 현재 세션 ID, 스트리밍 메시지 버퍼, 추천 카드, RAG 문서, 유기묘 정보

**관련 이슈**: #30, #32, #33, #34

---

### 4.4 채팅 히스토리 사이드바 (GlobalDrawer)

**목적**: 이전 세션 탐색 및 전환

**UI 구성**
- 세션 제목 (첫 메시지 기반 자동 생성, 최대 30자) + 날짜
- 세션 클릭 → `/chat/[id]`로 이동
- 세션 삭제 버튼 (`DELETE /api/v1/users/me/sessions/{id}`)
- 새 채팅 버튼 → 세션 생성 후 이동

**관련 이슈**: #34

---

### 4.5 냥심 번역기 — `/meme`

**목적**: 고양이 사진 업로드 → GPT-4o-mini Vision → 시니컬한 밈 텍스트 생성

**UI 구성** (2-column 레이아웃)

- **좌측**: 이미지 업로드 영역 (drag & drop + click), 추가 컨텍스트 입력, 분석 시작 버튼
- **우측**: 폴라로이드 카드 결과 (이미지 + 밈 텍스트 + 품종/나이 뱃지)
- "내 고양이로 등록" AlertDialog: 이름 입력 + breed/age 자동 채움 → `POST /api/v1/users/me/cats`

**API**: `POST /api/v1/meme/analyze` (multipart/form-data)

**관련 이슈**: #35, #36, #37

---

### 4.6 내 고양이 목록 — `/my-cats`

**목적**: 등록된 고양이 확인 및 관리

**UI 구성**
- UserCatCard 리스트 (이름, 품종, 나이, 프로필 이미지, 냥심 한 마디)
- 고양이 등록하기 버튼 → `/my-cats/new`
- 카드 "수정하기" → `/my-cats/[id]`

**API**: `GET /api/v1/users/me/cats`

**관련 이슈**: #30, #31

---

### 4.7 고양이 등록 — `/my-cats/new`

**목적**: 새 고양이 정보 등록

**UI 구성**
- 이름(필수), 나이(개월), 성별, 품종명(한/영), 프로필 이미지, 냥심 한 마디, 예방접종 기록

**API**: `POST /api/v1/users/me/cats`

**관련 이슈**: #37

---

### 4.8 고양이 수정 — `/my-cats/[id]`

**목적**: 고양이 정보 수정

**UI 구성**
- 프로필 이미지: 클릭해서 업로드 (`POST /api/v1/users/me/cats/upload-image`)
- 냥심 한 마디: textarea (최대 200자)
- 예방접종 기록 추가/삭제
- 저장: `PUT /api/v1/users/me/cats/{id}`
- 삭제: `DELETE /api/v1/users/me/cats/{id}`

**관련 이슈**: #37

---

### 4.9 프로필 — `/profile`

**목적**: 집사 정보 수정

**UI 구성**
- 닉네임, 나이, 성별, 연락처, 주소 수정 폼
- 양육 환경 선호 수정 (온보딩 항목과 동일)
- 저장: `PUT /api/v1/users/me/profile`

---

## 5. 상태 관리 흐름 개요

### 5.1 인증 상태

- `next-auth/react` `useSession()` — OAuth 세션 (프론트 전용)
- ZIPSA JWT (`zipsa_token`) — localStorage 저장, FastAPI 요청 헤더에 포함
- `POST /api/v1/auth/sync` — 로그인 완료 시 ZIPSA JWT 발급

### 5.2 전역 상태 (Zustand)

| 스토어 | 관리 상태 |
|---|---|
| `useSessionStore` | 세션 목록, 현재 세션 ID |
| `useChatStore` | 스트리밍 버퍼, 메시지 목록, 추천 카드, RAG 문서, 유기묘 정보 |

### 5.3 페이지별 주요 상태

| 페이지 | 서버 상태 (fetch) | 클라이언트 상태 |
|---|---|---|
| `/onboarding` | — | 폼 단계, 입력값 |
| `/chat/[id]` | 세션 메시지 목록 | 스트리밍 버퍼, 추천 카드, RAG 문서, 유기묘 카드 |
| GlobalDrawer | 세션 목록 | 선택된 세션 ID |
| `/meme` | — | 업로드 이미지, 분석 결과 |
| `/my-cats` | 고양이 목록 | — |
| `/my-cats/[id]` | 고양이 상세 | 수정 폼 임시값 |
| `/profile` | 프로필 정보 | 수정 폼 임시값 |

### 5.4 URL 기반 상태

- 현재 채팅 세션: `/chat/[id]` — URL로 공유 가능

---

## 6. 관련 이슈

| 이슈 | 내용 |
|---|---|
| #25 | NextAuth.js SSO 연동 |
| #26 | Backend Auth 레이어 (JWT 검증, /auth/sync) |
| #27 | 온보딩 UI |
| #29 | RescueCatCard 및 user_cats CRUD |
| #30 | CatCard React 컴포넌트 |
| #32 | Chat/Session API |
| #33 | LangGraph MongoDBSaver 연동 |
| #34 | 채팅 히스토리 사이드바 |
| #35 | 냥심 번역기 UI |
| #36 | Vision AI 연동 |
| #37 | UserCat 1-Click 등록 |
