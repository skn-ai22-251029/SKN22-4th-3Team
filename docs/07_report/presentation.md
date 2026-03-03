# ZIPSA (집사) — 발표 자료

> 전 프로젝트에서 구축한 LangGraph 멀티에이전트 AI를 실제 웹 서비스로 만든 과정
> SKN22-4th-3Team | 2026.02.26 ~ 2026.03.03 (6일 스프린트)

---

## 1. 이번 발표의 초점

전 프로젝트에서 **LangGraph 멀티에이전트 + Hybrid RAG** 코어를 완성했습니다.
이번 프로젝트는 그 AI 시스템을 **실제로 쓸 수 있는 웹 서비스**로 전환하는 것이 목표였습니다.

```
전 프로젝트          이번 프로젝트
─────────────        ──────────────────────────────────────
LangGraph 에이전트   Next.js 프론트엔드
Hybrid RAG      →   FastAPI REST API + SSE 스트리밍
MongoDB Atlas        인증 (Google SSO + JWT)
                     채팅 세션 영속성 (MongoDBSaver)
                     냥심 번역기 (Vision AI)
                     랜딩 페이지
```

---

## 2. 팀 구성

| 역할 | GitHub | 주요 기여 |
|------|--------|-----------|
| 메인 개발 | limdo (leemdo) | 웹 전체 설계 및 구현 |
| 팀원 | minho8234 | 테스트 시나리오, 랜딩 페이지 기획 |
| 팀원 | fleshflamer-commits (MoonSJ) | 보안 테스트, 랜딩 페이지 기획 |

**총 PR 35개 · 이슈 41개 · 6일**

---

## 3. 전체 웹 아키텍처

```
Browser
  │  Google OAuth 로그인
  ▼
Next.js (App Router)         ← 프론트엔드
  │  NextAuth.js 세션
  │  Zustand 전역 상태
  │
  │  REST + SSE 스트리밍
  ▼
FastAPI                      ← 백엔드
  │  JWT 인증 미들웨어
  │  /api/v1/*
  │
  ├─ LangGraph 에이전트  ─── MongoDB Atlas (Vector + BM25)
  │  (전 프로젝트 코어)
  │
  └─ MongoDB                 ← 유저 데이터 + 세션 + 체크포인트
       users / chat_sessions / checkpoints / user_cats
```

### 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | Next.js 14 (App Router) · NextAuth.js · Zustand · Tailwind CSS · shadcn/ui · react-markdown |
| 백엔드 | FastAPI · Python 3.11+ · Motor (async MongoDB) |
| 인증 | Google OAuth 2.0 → NextAuth.js → JWT (커스텀 동기화) |
| 스트리밍 | Server-Sent Events (SSE) |
| 세션 영속 | LangGraph MongoDBSaver |
| Vision AI | gpt-4o-mini Vision (냥심 번역기) |
| 외부 API | 국가동물보호정보시스템 (구조동물 실시간 조회) |

---

## 4. 인증 흐름

NextAuth.js의 Google OAuth와 FastAPI JWT를 어떻게 연결했는지가 핵심입니다.

```
1. 사용자가 "Google로 로그인" 클릭
        ↓
2. NextAuth.js → Google OAuth 인증
        ↓
3. NextAuth.js signIn 콜백 →  POST /api/v1/auth/sync
   { google_id, email, name, avatar_url }
        ↓
4. FastAPI: users 컬렉션 upsert + JWT 발급 (24h)
   응답: { access_token, user_id }
        ↓
5. JWT를 NextAuth.js session.zipsa_token 에 저장
        ↓
6. 이후 모든 API 요청: Authorization: Bearer {jwt}
   FastAPI get_current_user 의존성으로 검증
```

**포인트**: NextAuth.js는 OAuth 플로우만 담당하고, 실제 유저 데이터는 FastAPI가 자체 MongoDB에 관리합니다. NextAuth MongoDB Adapter는 사용하지 않습니다.

---

## 5. SSE 스트리밍 채팅 시스템

### 5-1. 왜 SSE인가?

LangGraph 에이전트는 응답 생성에 수초가 걸립니다. REST로 기다리면 UX가 나쁘기 때문에 **토큰이 생성될 때마다 즉시 전송**하는 SSE 방식을 선택했습니다.

### 5-2. 스트림 이벤트 구조

```
POST /api/v1/chat/stream  →  text/event-stream

data: {"type": "token",           "content": "서울"}
data: {"type": "token",           "content": " 강동구"}
...
data: {"type": "rescue_cats",     "data": [{animal_id, breed, ...}]}
data: {"type": "recommendations", "data": [{name_ko, image_url, ...}]}
data: {"type": "rag_docs",        "data": [{title, source, url}]}
data: [DONE]
```

- `token`: 텍스트 청크 → 말풍선에 실시간 append
- `rescue_cats` / `recommendations`: 우측 패널 카드 업데이트
- `rag_docs`: 참고 출처 패널 업데이트

**포인트**: LangGraph `astream_events v2`에서 `router_classification` 태그로 내부 LLM 호출을 필터링해 최종 응답 토큰만 스트리밍합니다.

### 5-3. 프론트엔드 스트림 처리

```typescript
for await (const event of streamChat(token, sessionId, text, profile)) {
  if (event.type === "token")        fullContent += event.content;
  if (event.type === "rescue_cats")  setRescueCats(event.data);
  if (event.type === "recommendations") setRecommendations(event.data);
}
// 완료 후 messages 배열에 추가
```

---

## 6. 채팅 세션 영속성 (MongoDBSaver)

### 구조

```
chat_sessions 컬렉션       checkpoints 컬렉션
─────────────────────      ───────────────────────────────
_id (= thread_id)          thread_id  (← session_id)
user_id                    전체 messages 배열
title (첫 메시지 자동 생성)  recommendations, rescue_cats
last_message               rag_docs, user_profile
message_count              ...AgentState 전체
updated_at
```

- `chat_sessions`: 사이드바에 보여줄 메타데이터
- `checkpoints`: LangGraph MongoDBSaver가 관리하는 에이전트 상태 전체
- thread_id = session_id로 동일하게 유지 → 대화 맥락 자동 복원

### 세션 재진입 시

```
GET /users/me/sessions/{id}/messages
  → app.aget_state(thread_id)  ← MongoDB에서 체크포인트 복원
  → messages 필터링
    · ToolMessage 제외 (raw JSON 방지)  ← 이번 버그픽스
    · content 없는 AIMessage 제외 (tool call용)
  → ChatMessageResponse 반환 (rescue_cats 포함)
```

---

## 7. 주요 페이지 & 컴포넌트

### 7-1. 온보딩 (`/profile`)

- 신규 로그인 시 자동 리다이렉트
- 주거 환경 · 활동량 · 동거인 · 알레르기 설문
- 완료 후 `/chat`으로 이동, `user_profile`이 에이전트 컨텍스트에 주입됨

### 7-2. 채팅 페이지 (`/chat/[id]`)

```
┌─────────────────────────────┬────────────────────────┐
│  채팅 영역                   │  우측 패널             │
│                             │                        │
│  [Z] AI 말풍선               │  참고 출처 (rag_docs)  │
│      react-markdown 렌더링  │                        │
│      BreedPopover 인라인    │  ┌──────────────────┐  │
│                             │  │  CatCard         │  │
│  [사용자] 말풍선             │  │  or              │  │
│                             │  │  RescueCatCard   │  │
│  [스트리밍 중 로딩 점점]      │  └──────────────────┘  │
│                             │                        │
│  [입력창]  [전송]            │  탭: 추천품종 / 구조묘  │
└─────────────────────────────┴────────────────────────┘
```

- **BreedPopover (Interactive Text)**: AI 응답 내 품종명을 클릭하면 팝업으로 간단 정보 표시 → 우측 패널 해당 카드로 포커스
- **react-markdown**: AI 응답의 굵기·목록·링크·구분선 렌더링
- **GlobalDrawer**: 좌측 슬라이딩 세션 히스토리

### 7-3. 내 고양이 (`/my-cats`)

- `UserCatCard` 그리드 — 이름, 품종, 나이, 밈 텍스트, 이미지
- 고양이 등록 방법 2가지:
  1. 직접 등록 폼
  2. 냥심 번역기 결과에서 1-Click 등록

### 7-4. 냥심 번역기 (`/meme`)

```
사진 업로드 (drag & drop)
  + 선택적 텍스트 힌트
        ↓
POST /api/v1/meme/analyze
  → 이미지 base64 → gpt-4o-mini Vision
  → JSON 구조화 응답: { meme_text, breed_guess, age_guess }
  → 이미지 static/meme/{uuid}.jpg 저장
        ↓
폴라로이드 결과 카드
  밈 텍스트 (italic) + 품종/나이 뱃지
        ↓
"내 고양이로 등록" → AlertDialog
  breed_guess, age_guess 자동 파싱 채움
  → POST /users/me/cats → /my-cats 리다이렉트
```

---

## 8. Zustand 전역 상태 관리

```typescript
interface ZipsaStore {
  profile: UserProfile | null;   // 온보딩 프로필 (채팅 컨텍스트로 전달)
  sessions: ChatSession[];       // 사이드바 세션 목록
  addSession / updateSession / removeSession
}
```

- 페이지 새로고침 시 세션 목록은 `GET /users/me/sessions`로 재조회
- `profile`은 스트리밍 요청 시 `user_profile`로 에이전트에 주입

---

## 9. 랜딩 페이지

| 섹션 | 구현 포인트 |
|------|------------|
| **Hero** | 슬로건 · 통계 배지 · CTA |
| **DemoSection** | 실제 `CatCard` / `RescueCatCard` 컴포넌트를 목업 데이터로 렌더링. 탭 전환으로 두 시나리오 시연 |
| **Features** | 집사 일지 Journey 카드 (준비·인연·만남·동행 4단계) |
| **HowItWorks** | 3단계 프로세스 |
| **MemePreview** | 냥심 번역기 정적 목업 (폴라로이드) |
| **FinalCTA** | 마무리 슬로건 |
| **FloatingButtons** | `/meme` FAB (amber) + 스크롤 탑 버튼 |

---

## 10. 버그픽스 — 겪었던 문제들

### 채팅 말풍선에 raw JSON 표시

**원인**: LangGraph 체크포인트의 `messages` 배열에는 `ToolMessage`(국가동물보호정보시스템 API 응답 JSON)도 포함됩니다. `list_messages`에서 `isinstance(msg, HumanMessage) else "ai"`로 ToolMessage를 AI 메시지로 취급해 버렸습니다.

**수정**: `ToolMessage` 및 content 없는 `AIMessage` 필터링 추가.

### Head Butler가 JSON을 응답에 포함

**원인**: `specialist_result`의 `tool_output` (raw JSON 문자열)이 LLM 프롬프트에 그대로 전달되어, LLM이 JSON을 응답에 포함시켰습니다.

**수정**: 프롬프트 생성 시 `tool_output` 키 제외 + rescue_cats 응답 규칙 추가.

### 채팅 세션 타이틀이 마지막 메시지로 덮어쓰임

**원인**: `updateSession()`이 매 메시지마다 `title: text`를 넘겨 Zustand 스토어의 타이틀을 계속 갱신. 로그아웃 후 재진입 시 서버 저장 값(첫 메시지)과 달랐습니다.

**수정**: `messages.length === 0`일 때만 title 업데이트.

---

## 11. 개발 현황

| 구분 | 수치 |
|------|------|
| 기간 | 2026.02.26 ~ 2026.03.03 (6일) |
| 총 PR | 35개 (100% Merged) |
| 완료 이슈 | 35개 |
| 미완료 이슈 | 6개 (Docker · OCI 배포 · CI/CD · Redis · Rate Limiting) |

미완료 항목은 모두 **배포 인프라** 관련입니다. 도메인(`zipsa.leemdo.com`) 및 OCI 서버는 준비되어 있고, Docker Compose·GitHub Actions 파이프라인만 미완성입니다.

---

## 12. 시연 시나리오

1. **로그인** — Google SSO → `/auth/sync` → JWT 발급
2. **온보딩** — 프로필 설정 (1인 가구, 조용한 환경)
3. **품종 추천** — "조용한 고양이 추천해줘" → CatCard + BreedPopover
4. **구조묘 입양** — "서울 강동구 보호 중인 고양이 있어?" → RescueCatCard
5. **냥심 번역기** — 사진 업로드 → 폴라로이드 밈 → 내 고양이 등록

---

*develop branch @ 2026-03-03 · PR #58 ~ #79*
