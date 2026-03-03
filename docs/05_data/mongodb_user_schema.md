# MongoDB 유저 스키마 설계

## 1. 개요

RAG 데이터(`cat_library` DB)와 분리된 애플리케이션 전용 DB를 사용합니다.

| 항목 | 내용 |
|---|---|
| DB 이름 | `zipsa` (`AuthConfig.USER_DB_NAME`) |
| 환경 변수 | `MONGO_V3_URI` |

### 컬렉션 구조

```
zipsa
├── users                  # 유저 계정 (백엔드 /auth/sync 관리)
├── user_profiles          # 유저 커스텀 프로필 (1:1, 앱 관리)
├── user_cats              # 유저의 고양이 (1:N)
├── chat_sessions          # 채팅 세션 메타데이터 (1:N)
├── checkpoints            # LangGraph MongoDBSaver 체크포인트 (SDK 관리)
└── checkpoint_writes      # LangGraph MongoDBSaver 쓰기 로그 (SDK 관리)
```

> **인증 방식**: NextAuth.js는 OAuth 흐름(Google/Kakao/Naver 리다이렉트 및 토큰 교환)만 담당합니다.
> MongoDB Adapter는 사용하지 않으며, NextAuth 세션은 JWT 쿠키로 프론트에서 관리됩니다.
> 로그인 완료 후 프론트가 `POST /api/v1/auth/sync`를 호출해 백엔드가 `users` 컬렉션에 upsert하고 ZIPSA JWT를 발급합니다.

---

## 2. 컬렉션 스키마

### 2.1 `users`

`POST /api/v1/auth/sync` 호출 시 백엔드가 upsert합니다. `email`을 unique key로 사용합니다.

```json
{
  "_id": "ObjectId",
  "email": "string (unique, OAuth 이메일)",
  "name": "string (OAuth 표시 이름)",
  "image": "string (OAuth 프로필 이미지 URL) | null",
  "provider": "string (google | kakao | naver)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**인덱스**
- `email`: unique

---

### 2.2 `user_profiles`

앱 레이어의 커스텀 유저 데이터. `users._id`를 `user_id`로 참조합니다.
온보딩 완료(`POST /api/v1/users/me/profile`) 후 생성됩니다.

```json
{
  "_id": "ObjectId",
  "user_id": "string (ref: users._id)",

  "nickname": "string | null",
  "age": "int | null",
  "gender": "string (M | F | 미설정) | null",
  "contact": "string | null",
  "address": "string | null",
  "avatar_url": "string (OCI Object Storage 공개 URL) | null",

  "preferences": {
    "housing": "string (apartment | house | studio)",
    "activity": "string (low | medium | high)",
    "experience": "string (beginner | intermediate | expert)",
    "work_style": "string | null",
    "allergy": "bool",
    "has_children": "bool",
    "has_dog": "bool",
    "traits": ["string"],
    "companion": ["string"]
  },

  "onboarding_completed": "bool",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**인덱스**
- `user_id`: unique (1:1)

---

### 2.3 `user_cats`

유저 1명이 여러 마리를 등록할 수 있는 구조입니다.
냥심 번역기(`POST /api/v1/meme/analyze`) 결과를 `meme_text`에 저장합니다.

```json
{
  "_id": "ObjectId",
  "user_id": "string (ref: users._id)",

  "name": "string",
  "age_months": "int",
  "gender": "string (M | F | 미상)",
  "breed_name_ko": "string",
  "breed_name_en": "string",
  "profile_image_url": "string | null",
  "meme_text": "string (냥심 번역기 생성 텍스트) | null",

  "health": {
    "vaccinations": [
      {
        "label": "string (예: 종합백신 3차)",
        "date": "string (예: 2024-03-15)"
      }
    ]
  },

  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**인덱스**
- `user_id`: 일반 (유저별 고양이 목록 조회)

---

### 2.4 `chat_sessions`

채팅 세션 메타데이터를 관리합니다.
**메시지는 별도 컬렉션이 아닌 LangGraph `checkpoints`에 저장**됩니다.
`_id`를 문자열로 변환하여 LangGraph의 `thread_id`로 사용합니다.

```json
{
  "_id": "ObjectId",
  "user_id": "string (ref: users._id)",
  "thread_id": "string (= str(_id), LangGraph 체크포인트 연결 키)",

  "title": "string (첫 메시지 전송 시 자동 생성, 최대 30자) | null",
  "last_message": "string (UI 미리보기용) | null",
  "message_count": "int",

  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**인덱스**
- `user_id`: 일반 (유저별 세션 목록 조회, `updated_at` 내림차순)
- `thread_id`: unique (LangGraph 연결)

---

### 2.5 `checkpoints` / `checkpoint_writes` (LangGraph 관리)

`langgraph-checkpoint-mongodb` SDK(`MongoDBSaver`)가 자동으로 생성·관리합니다.
`thread_id` = `chat_sessions.thread_id`로 연결되며, 모든 메시지 히스토리는 여기에 저장됩니다.

- `checkpoints`: 스냅샷 (AgentState 전체)
- `checkpoint_writes`: 노드별 쓰기 로그

직접 조작하지 않으며, 세션 삭제 시 `checkpointer.adelete_thread(thread_id)`로 함께 정리합니다.

---

## 3. 컬렉션 관계도

```
users (1)
  ├── user_profiles (1)      user_id → users._id
  ├── user_cats (N)          user_id → users._id
  └── chat_sessions (N)      user_id → users._id
        ├── checkpoints (N)       thread_id → chat_sessions.thread_id  [LangGraph]
        └── checkpoint_writes (N) thread_id → chat_sessions.thread_id  [LangGraph]
```

---

## 4. 환경 변수

```
MONGO_V3_URI=mongodb+srv://...  # cat_library + zipsa DB 모두 동일 Atlas 클러스터
```

> `cat_library`(RAG 데이터)와 `zipsa`(유저 데이터)는 같은 클러스터, 다른 DB로 분리됩니다.

---

## 5. 관련 파일

- `src/core/config.py` — `AuthConfig.USER_DB_NAME = "zipsa"`
- `src/api/routers/auth.py` — `POST /auth/sync` (users upsert + JWT 발급)
- `src/api/routers/users.py` — `user_profiles` CRUD
- `src/api/routers/cats.py` — `user_cats` CRUD
- `src/api/routers/sessions.py` — `chat_sessions` CRUD + 체크포인트 조회
- `src/agents/graph.py` — `MongoDBSaver` 초기화 (lifespan)
