# 와이어프레임 명세서

## 1. 개요

ZIPSA 서비스의 UI 구조와 화면 구성을 정의합니다.
실제 프로토타입(`UI_wireframe/`)을 기반으로 작성된 명세이며, Next.js App Router 구현의 설계 기준이 됩니다.

**참조**: `UI_wireframe/src/app/` — React 프로토타입 구현체

---

## 2. 화면 목록

| 화면 | 경로 | 인증 필요 |
|---|---|---|
| 랜딩 | `/` | 불필요 |
| 로그인 | `/auth/signin` | 불필요 |
| 온보딩 | `/onboarding` | 필요 |
| 채팅 | `/chat/[sessionId]` | 불필요 (게스트 허용) |
| 냥심 번역기 | `/meme` | 불필요 (게스트 허용) |
| 프로필 | `/profile` | 필요 |
| 내 고양이 목록 | `/profile/cats` | 필요 |
| 고양이 등록/수정 | `/profile/cats/new`, `/profile/cats/[catId]` | 필요 |

---

## 3. 공통 컴포넌트

### 3.1 Navbar

**파일**: `Navigation.tsx`

**미인증**

![Navbar 미인증](./images/comp_navbar_guest.png)

**인증**

![Navbar 인증](./images/comp_navbar_logged_in.png)

| 요소 | 위치 | 설명 |
|---|---|---|
| 햄버거 아이콘 | 좌측 | 클릭 시 Global Drawer 열림 |
| ZIPSA 로고 | 좌측 | 텍스트 |
| 새 채팅 버튼 | 우측 | 채팅 페이지에서는 숨김 |
| 로그인 버튼 | 우측 (미인증) | outline 스타일 |
| 아바타 드롭다운 | 우측 (인증) | 닉네임 + chevron-down |

---

### 3.2 프로필 드롭다운

**파일**: `Navigation.tsx` — 아바타 클릭 시 표시 (w-200px)

![프로필 드롭다운](./images/comp_profile_dropdown.png)

| 항목 | 이동 |
|---|---|
| 닉네임 + 이메일 (헤더, 클릭 불가) | — |
| 내 프로필 | `/profile` |
| 내 고양이 | `/profile/cats` |
| 로그아웃 | NextAuth signOut |

---

### 3.3 Global Drawer

**파일**: `GlobalDrawer.tsx` — 좌측 슬라이드인 (w-300px)

**미인증**

![Global Drawer 미인증](./images/comp_drawer_guest.png)

**인증** (세션 목록 스크롤 가능)

![Global Drawer 인증](./images/comp_drawer_logged_in.png)

| 영역 | 내용 |
|---|---|
| 헤더 | ZIPSA 로고 + × 닫기 + [새 채팅] 버튼 |
| 내비게이션 | 냥심 번역기, 품종 탐색 |
| 세션 목록 (인증) | 최근 대화 (스크롤), 행 호버 시 🗑 삭제 버튼 노출 |
| 빈 상태 (미인증) | "로그인하면 대화 기록이 저장돼요" + [로그인하기] |

세션 삭제: 🗑 클릭 → AlertDialog 확인 → `DELETE /api/v1/users/me/sessions/{sessionId}`

---

### 3.4 CatCard

**파일**: `CatCard.tsx` — `type: "breed" | "userCat" | "shelter"`

**BreedCatCard** (`type="breed"`, w-320px)

![BreedCatCard](./images/comp_catcard_breed.png)

**UserCatCard** (`type="userCat"`, w-240px)

![UserCatCard](./images/comp_catcard_usercat.png)

**RescueCatCard** (`type="shelter"`, w-320px)

![RescueCatCard](./images/comp_catcard_shelter.png)

---

### 3.5 Interactive Text Popover

**파일**: `BreedPopover.tsx` — AI 응답 내 품종명 (밑줄 텍스트) 클릭 시 표시

![BreedPopover](./images/comp_breed_popover_demo.png)

| 요소 | 내용 |
|---|---|
| 트리거 | underline decoration-2, 품종명 |
| 팝오버 위치 | 텍스트 위 (side="top"), w-280px |
| 내용 | 60px 썸네일 + 품종명 한/영 + 태그 chip + 한줄 요약 |
| 하단 | "자세히 보기" 링크 |

---

## 4. 페이지 명세

### 4.1 로그인 — `/auth/signin`

**파일**: `LoginPage.tsx` — 2컬럼 레이아웃 (50/50)

![로그인 페이지](./images/page_login.png)

| 요소 | 설명 |
|---|---|
| 좌측 | 고양이 일러스트 영역 (bg-gray-100) |
| 우측 | ZIPSA 로고 + 태그라인 + SSO 버튼 3개 |
| Google | white 배경, gray 테두리 |
| 카카오 | yellow-300 배경 |
| 네이버 | green-500 배경, white 텍스트 |

로그인 완료 시: 신규 → `/onboarding`, 기존 → `/chat`

---

### 4.2 온보딩 — `/onboarding`

**파일**: `OnboardingPage.tsx` — 상단 스텝퍼 + 중앙 컨텐츠 + 하단 이전/다음

스텝퍼: 완료(✓ 채운 원) / 현재(빈 원, 굵은 테두리) / 미도달(회색 원)

**Step 1 — 나 소개**: 닉네임 텍스트 입력

![온보딩 Step 1](./images/page_onboarding_1.png)

**Step 2 — 우리 집**: 거주 형태 카드 선택 + 집 비우는 시간 pill 선택

![온보딩 Step 2](./images/page_onboarding_2.png)

**Step 3 — 함께 사는**: 동거인 Yes/No + 조건부 chip + 알레르기 Yes/No

![온보딩 Step 3](./images/page_onboarding_3.png)

**Step 4 — 고양이 취향**: 생활 패턴 카드 + 양육 경험 pill + 원하는 성향 다중 chip

![온보딩 Step 4](./images/page_onboarding_4.png)

완료 시: `POST /api/v1/users/me/profile` → `/chat` 이동

---

### 4.3 채팅 — `/chat/[sessionId]`

**파일**: `ChatPage.tsx` — 전체 높이 고정, 2컬럼

![채팅 페이지](./images/page_chat.png)

| 컬럼 | 너비 | 내용 |
|---|---|---|
| 채팅 | flex-1 | 헤더(세션 제목) + 메시지 목록 + 입력창 |
| 결과 패널 | 520px 고정 | 참고 출처 + 품종 탭 + CatCard |

**메시지**: 사용자(우, gray-200) / AI(좌, white + "Z" 아바타)

**결과 패널**: RAG 출처 카드 → 품종 탭(최대 3개) → 탭 선택에 따라 BreedCatCard 교체

**게스트 모드**: 입력창 위 로그인 유도 넛지 배너 표시

---

### 4.4 냥심 번역기 — `/meme`

**파일**: `MemeGenerator.tsx` — Navbar + 2컬럼 중앙 정렬

![냥심 번역기](./images/page_meme.png)

| 컬럼 | 내용 |
|---|---|
| 좌측 | 420×420px 드래그앤드롭 업로드 박스 + 첨언 입력(최대 100자) + [분석 시작] |
| 우측 | 폴라로이드 카드(rotate 2deg) — 사진 + 밈 텍스트 + [내 고양이로 등록] [공유] |

---

### 4.5 프로필 — `/profile`

**파일**: `ProfileSettings.tsx` — 단일 컬럼 (max-w-720px)

![프로필 설정](./images/page_profile.png)

**기본 정보**: 닉네임 / 나이 / 성별(세그먼트) / 연락처 / 주소(Kakao 우편번호 API)

**양육 환경**: 거주 형태 / 활동량 / 경험 / 집 비우는 시간 / 동거인 / 알레르기 / 원하는 성향

저장: `PUT /api/v1/users/me/profile`

---

### 4.6 내 고양이 — `/profile/cats`

**파일**: `MyCatsPage.tsx` — 3열 카드 그리드 (max-w-960px)

![내 고양이](./images/page_my_cats.png)

등록된 고양이: UserCatCard (수정 → `/profile/cats/[catId]`)
마지막 카드: 점선 테두리 "고양이 추가하기" → `/profile/cats/new`

---

### 4.7 랜딩 — `/`

**파일**: `Hero.tsx`, `HowItWorks.tsx`, `AITeam.tsx`, `Features.tsx`, `ViralFeature.tsx`, `ChatPreview.tsx`, `FinalCTA.tsx`

![랜딩 페이지](./images/page_landing.png)

| 순서 | 섹션 |
|---|---|
| 1 | Hero — 헤드라인 + 통계(67종/4인팀/파양률) + CTA |
| 2 | How It Works — 3단계 프로세스 |
| 3 | AI 전문가 팀 — 4인 에이전트 카드 |
| 4 | Features — 2×2 기능 카드 |
| 5 | 냥심 번역기 소개 |
| 6 | 채팅 인터페이스 미리보기 |
| 7 | Final CTA |

---

## 5. 인터랙션 정의

| 인터랙션 | 트리거 | 동작 |
|---|---|---|
| Drawer 열기 | Navbar 햄버거 클릭 | 좌측 슬라이드인 |
| 세션 삭제 | 행 호버 → 🗑 클릭 | AlertDialog 확인 → DELETE API |
| 채팅 탭 전환 | 품종 탭 클릭 | 하단 CatCard 교체, 활성 탭 하단선 |
| 온보딩 진행 | 다음/이전 버튼 | 스텝 ±1, 1단계 이전 버튼 숨김 |
| 동거인 조건부 표시 | "혼자 사시나요?" 아니오 선택 | chip 선택 영역 노출 |
| 주소 검색 | [주소 검색] 버튼 | Kakao 우편번호 모달 → 자동 입력 |

---

## 6. 관련 문서

| 문서 | 경로 |
|---|---|
| App Router 경로 | `docs/06_feature/app_router_spec.md` |
| 요구사항 정의서 | `docs/06_feature/requirements_spec.md` |
| API 명세 | `docs/04_api/zipsa_openapi.yaml` |
| 프로토타입 소스 | `UI_wireframe/src/app/` |
