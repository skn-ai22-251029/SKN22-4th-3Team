# Page 명세서

## 1. 개요

Next.js App Router 기반 ZIPSA 프론트엔드의 페이지 구조, 화면별 요구사항, 상태 관리 흐름을 정의합니다.

---

## 2. App Router 경로 구조

```
/
├── (auth)
│   └── auth/signin                  # NextAuth 로그인
├── onboarding                       # 온보딩 (프로필 미완료 시 필수)
├── chat                             # 새 채팅 (세션 생성 후 리다이렉트)
│   └── [sessionId]                  # 채팅 세션
├── profile                          # 내 프로필 설정
│   └── cats
│       ├── new                      # 고양이 등록
│       └── [catId]                  # 고양이 상세/수정
└── breeds                           # 품종 탐색 (공개)
```

**API Routes**

```
/api/auth/[...nextauth]              # NextAuth 핸들러 (SDK 자동)
```

---

## 3. 접근 제어 (Middleware)

```
미인증                → /chat, /breeds, /meme 접근 가능 (게스트 모드)
미인증                → /onboarding, /profile 접근 시 /auth/signin으로 리다이렉트
인증 + 온보딩 미완료  → /onboarding으로 리다이렉트
인증 + 온보딩 완료   → 정상 접근
```

**게스트 채팅 제한**
- 세션 저장 없음 (히스토리 미제공)
- user_profile 없으므로 개인화 추천 미적용
- 채팅창 하단 넛지: "로그인하면 내 환경에 맞는 품종을 추천해드려요"

`/auth/signin`은 인증된 사용자 접근 시 `/chat`으로 리다이렉트.

---

## 4. 화면별 요구사항

---

### 4.1 로그인 — `/auth/signin`

**목적**: NextAuth.js SSO 로그인 진입점

**UI 구성**
- ZIPSA 로고 + 서비스 소개 문구
- 소셜 로그인 버튼: Google, Kakao, Naver
- 약관 동의 안내

**진입 조건**: 미인증

**완료 후 흐름**
- 온보딩 미완료 → `/onboarding`
- 온보딩 완료 → `/chat`

**관련 이슈**: #25

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

### 4.3 채팅 — `/chat/[sessionId]`

**목적**: AI 집사(ZIPSA)와 고양이 품종 매칭 및 케어 상담

**UI 구성**

```
┌─────────────────────────────────────────────────┐
│  [사이드바]               [채팅 영역]            │
│  - 세션 히스토리          - 메시지 스트리밍      │
│  - 새 채팅 버튼           - 인터랙티브 텍스트    │
│                           [결과 영역]            │
│                           - CatCard (최대 3종)   │
│                           - RAG 출처 문서        │
│  ─────────────────────────────────────────────  │
│                      [채팅 입력창]               │
└─────────────────────────────────────────────────┘
```

**기능 요구사항**

- 스트리밍 응답: `POST /api/v1/chat/stream` (SSE)
- 세션 목록 사이드바: `GET /api/v1/users/me/sessions`
- 메시지 히스토리: `GET /api/v1/users/me/sessions/{sessionId}/messages`
- 인터랙티브 텍스트: 품종명 호버/클릭 시 간이 카드 팝업 (#31)
- CatCard 우측 패널: 추천 품종 최대 3종, 레이더 차트 포함 (#30)
- `/chat` 접근 시 자동으로 새 세션 생성 후 `/chat/[sessionId]`로 리다이렉트

**관련 이슈**: #30, #31, #34

---

### 4.4 채팅 히스토리 사이드바

**목적**: 이전 세션 탐색 및 전환

**UI 구성**
- 세션 제목 (첫 메시지 기반 자동 생성) + 날짜
- 세션 클릭 → `/chat/[sessionId]`로 이동
- 세션 삭제 버튼 (`DELETE /api/v1/users/me/sessions/{sessionId}`)
- 새 채팅 버튼 → 세션 생성 후 이동

**관련 이슈**: #34

---

### 4.5 프로필 — `/profile`

**목적**: 집사 정보 및 고양이 정보 관리

**UI 구성**
- 닉네임, 나이, 성별, 연락처, 주소 수정 폼
- 양육 환경 선호 수정 (온보딩 항목과 동일)
- 저장: `PUT /api/v1/users/me/profile`
- 내 고양이 목록 링크 → `/profile/cats`

---

### 4.6 고양이 목록 — `/profile/cats`

**목적**: 등록된 고양이 확인 및 관리

**UI 구성**
- 고양이 카드 리스트 (User Cat Card, Type B)
- 고양이 추가 버튼 → `/profile/cats/new`
- 카드 클릭 → `/profile/cats/[catId]`

---

### 4.7 고양이 등록/수정 — `/profile/cats/new`, `/profile/cats/[catId]`

**목적**: 고양이 정보 등록 및 수정

**UI 구성**
- 이름, 나이(개월), 성별, 묘종(67종 자동완성), 프로필 사진 업로드
- 예방접종 기록 (종류 + 날짜, 복수 추가 가능)
- 등록: `POST /api/v1/users/me/cats`
- 수정: `PUT /api/v1/users/me/cats/{catId}`
- 삭제: `DELETE /api/v1/users/me/cats/{catId}`

묘종 자동완성: `GET /api/v1/breeds?q={검색어}` (#31 Interactive Text 연계)

**관련 이슈**: #37

---

### 4.8 품종 탐색 — `/breeds`

**목적**: 67종 품종 전체 열람 (로그인 불필요)

**UI 구성**
- 검색바 (`?q=` 파라미터)
- 품종 카드 그리드 (CatCard Type A)
- 카드 클릭 → 상세 팝업 또는 `/breeds/[breedId]`

**API**: `GET /api/v1/breeds`

---

## 5. 상태 관리 흐름 개요

> 구현 상세는 #23 참고

### 5.1 인증 상태

- `next-auth/react` `useSession()` — 전역 인증 상태
- 서버 컴포넌트에서는 `getServerSession()` 사용
- JWT에서 `user_id`, `email` 추출 → FastAPI 요청 헤더(`Authorization: Bearer`)에 포함

### 5.2 페이지별 주요 상태

| 페이지 | 서버 상태 (fetch) | 클라이언트 상태 |
|---|---|---|
| `/onboarding` | — | 폼 단계, 입력값 |
| `/chat/[sessionId]` | 세션 메시지 목록 | 스트리밍 버퍼, 추천 카드, RAG 문서 |
| 사이드바 | 세션 목록 | 선택된 세션 ID |
| `/profile` | 프로필 정보 | 수정 폼 임시값 |
| `/profile/cats` | 고양이 목록 | — |
| `/profile/cats/[catId]` | 고양이 상세 | 수정 폼 임시값 |

### 5.3 데이터 흐름

```
NextAuth Session (user_id, email)
    │
    ├── 서버 컴포넌트 (RSC)  → 초기 데이터 fetch (프로필, 세션 목록, 고양이 목록)
    │
    └── 클라이언트 컴포넌트
            ├── Chat: SSE 스트리밍 수신 → messages 상태 업데이트
            ├── CatCard: recommendations 상태 → 우측 패널 렌더링
            └── 폼: 로컬 상태 → API 호출 → 서버 상태 갱신(revalidate)
```

### 5.4 URL 기반 상태

- 현재 세션: `/chat/[sessionId]` — URL로 공유 가능
- 품종 검색: `/breeds?q=검색어`
- 그 외 UI 상태(모달, 확장 여부)는 클라이언트 로컬 상태

---

## 6. 관련 이슈

| 이슈 | 내용 |
|---|---|
| #19 | FastAPI + LangServe 초기 세팅 |
| #23 | 상태 관리 아키텍처 수립 |
| #25 | NextAuth.js SSO 연동 |
| #27 | 온보딩 UI 개발 |
| #30 | CatCard React 컴포넌트 개발 |
| #31 | Interactive Text 기능 구현 |
| #34 | 채팅 히스토리 UI 개발 |
| #37 | UserCat 1-Click 등록 기능 |
