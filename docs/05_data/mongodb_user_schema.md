# MongoDB 유저 스키마 설계

## 1. 개요

RAG 데이터(`cat_library` DB)와 분리된 애플리케이션 전용 DB를 사용합니다.

| 항목 | 내용 |
|---|---|
| DB 이름 | `zipsa_app` |
| 환경 변수 | `MONGO_APP_URI` |

### 컬렉션 구조

```
zipsa_app
├── users                  # 유저 계정 (NextAuth 관리 - 수정 금지)
├── accounts               # OAuth 계정 (NextAuth 관리)
├── sessions               # 세션 토큰 (NextAuth 관리)
├── verification_tokens    # 이메일 인증 (NextAuth 관리)
├── user_profiles          # 유저 커스텀 프로필 (1:1, 앱 관리)
├── user_cats              # 유저의 고양이 (1:N)
├── chat_sessions          # 채팅 세션 메타데이터 (1:N)
├── chat_messages          # 채팅 메시지 (1:N)
└── checkpoints            # LangGraph MongoDBSaver 체크포인트 (SDK 관리)
```

---

## 2. 컬렉션 스키마

### 2.1 `users` (NextAuth 관리)

NextAuth.js MongoDB adapter가 자동으로 생성·관리합니다. **직접 수정하지 않습니다.**

```json
{
  "_id": "ObjectId",
  "name": "string (OAuth 표시 이름)",
  "email": "string (unique)",
  "image": "string (OAuth 프로필 이미지 URL)",
  "emailVerified": "datetime | null"
}
```

**NextAuth 연관 컬렉션** (SDK 자동 관리)
- `accounts`: OAuth 계정 정보 (provider, providerAccountId, tokens)
- `sessions`: 세션 토큰
- `verification_tokens`: 이메일 인증 토큰

---

### 2.2 `user_profiles`

앱 레이어의 커스텀 유저 데이터. NextAuth `users._id`를 참조합니다.
온보딩 완료 후 생성되며, 기능 확장 시 이 컬렉션에 필드를 추가합니다.

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (ref: users._id)",

  "nickname": "string",
  "age": "int | null",
  "gender": "string (M | F | 미설정) | null",
  "contact": "string | null",
  "address": "string | null",

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

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (ref: users._id)",

  "name": "string",
  "age_months": "int",
  "gender": "string (M | F | 미상)",
  "breed_name_ko": "string (67종 리스트 기준)",
  "breed_name_en": "string",
  "profile_image_url": "string | null",

  "health": {
    "vaccinations": [
      {
        "type": "string (예: 종합백신 3차)",
        "date": "datetime"
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

채팅 세션 메타데이터를 관리합니다. 메시지는 `chat_messages`에 분리 저장합니다.
`_id`를 문자열로 변환하여 LangGraph의 `thread_id`로 사용합니다.

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (ref: users._id)",
  "thread_id": "string (= str(_id), LangGraph 체크포인트 연결 키)",

  "title": "string (첫 메시지 기반 자동 생성)",
  "last_message": "string (UI 미리보기용)",
  "message_count": "int",

  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**인덱스**
- `user_id`: 일반 (유저별 세션 목록 조회)
- `thread_id`: unique (LangGraph 연결)

---

### 2.5 `chat_messages`

메시지를 세션과 분리하여 저장합니다. AI 메시지의 경우 품종 카드·RAG 출처를 함께 저장합니다.

```json
{
  "_id": "ObjectId",
  "session_id": "ObjectId (ref: chat_sessions._id)",

  "role": "string (human | ai)",
  "content": "string",

  "recommendations": [
    {
      "name_ko": "string",
      "name_en": "string",
      "image_url": "string",
      "summary": "string",
      "tags": ["string"],
      "stats": {}
    }
  ],
  "rag_docs": [
    {
      "title": "string",
      "subtitle": "string",
      "source": "string",
      "url": "string"
    }
  ],

  "created_at": "datetime"
}
```

> `recommendations`, `rag_docs`는 AI 메시지에만 존재하며 없으면 빈 배열로 저장합니다.

**인덱스**
- `session_id`: 일반 (세션별 메시지 조회)
- `session_id` + `created_at`: 복합 (시간순 정렬 조회)

---

### 2.6 `checkpoints` (LangGraph 관리)

`langgraph-checkpoint-mongodb` SDK가 자동으로 생성·관리합니다.
`thread_id` = `chat_sessions.thread_id`로 연결됩니다.

직접 조작하지 않으며, LangGraph `MongoDBSaver` 초기화 시 자동 구성됩니다.

---

## 3. 컬렉션 관계도

```
users (1) [NextAuth 관리]
  ├── user_profiles (1)     user_id → users._id  [앱 관리]
  ├── user_cats (N)         user_id → users._id
  └── chat_sessions (N)     user_id → users._id
        ├── chat_messages (N)    session_id → chat_sessions._id
        └── checkpoints (N)      thread_id → chat_sessions.thread_id
```

---

## 4. 환경 변수 추가

`.env.example`에 아래 항목 추가 필요:

```
MONGO_APP_URI=mongodb+srv://...  # zipsa_app DB 연결 문자열
```

> `cat_library` DB와 동일한 Atlas 클러스터를 사용하되 DB를 분리합니다.

---

## 5. 관련 파일

- `src/utils/mongodb.py` — `get_app_db()` 메서드 추가 예정
- `src/core/models/user_profile.py` — `profile` 필드와 매핑
- `src/agents/graph.py` — `MemorySaver` → `MongoDBSaver` 교체 예정 (#16)
