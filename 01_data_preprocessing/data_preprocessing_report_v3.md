# 데이터 전처리 보고서 (V3 Clean - 최신)

**버전**: `v3` (Clean Policy)
**데이터베이스**: `cat_library` (MongoDB Atlas)
**도메인 사전**: `src/core/tokenizer/domain_dictionary.txt` (~1,100개 용어)

---

## 1. 데이터셋 통계

| 출처 | 원본 건수 | 처리 건수 | 상태 |
| :--- | :---: | :---: | :--- |
| **BemyPet Catlab** (기사) | 1,153 | 1,153 | ✅ 완료 |
| **Cat Breeds** (품종) | 67 | 67 | ✅ 완료 |
| **합계** | 1,220 | **1,205** (DB 기준) | ✅ 완료 |

---

## 2. 컬렉션 & 스키마

### 📚 기사 컬렉션
- **네임스페이스**: `cat_library.care_guides`
- **UID 형식**: `guide_00000` (표준화)

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `uid` | `str` | 표준화 ID (예: `guide_00123`) |
| `title_refined` | `str` | LLM이 생성한 검색 최적화 제목 |
| `text` | `str` | 정제된 본문 텍스트 |
| `summary` | `str` | 전문 요약 (1문장) |
| `keywords` | `List[str]` | 핵심 키워드 (3~5개) |
| `intent_tags` | `List[str]` | 의도 태그 (예: `Emergency`, `Daily Care`) |
| `categories` | `List[str]` | 주제 분류 (영문 표준) |
| `specialists` | `List[str]` | 전문가 페르소나 매핑 (영문) |
| `embedding` | `List[float]` | OpenAI 임베딩 (1536차원) |
| `tokenized_text` | `str` | Kiwi 도메인 사전 기반 토큰화 텍스트 |

### 🐈 품종 컬렉션 (통합 저장)
- **네임스페이스**: `cat_library.care_guides` (기사와 단일 컬렉션)
- **원본**: `data/v3/cat_breeds_integrated.json`
- **이미지**: TheCatAPI CDN URL 매핑 완료
- **필터링**: `filter_shedding`, `filter_energy` 등 17개 수치 필터 필드 포함

---

## 3. 분류 체계 (V3 표준)

### Categories (주제 분류) — DB 실측 기준

| 카테고리 | 한국어 | 건수 |
| :--- | :--- | ---: |
| `Behavior` | 행동/심리 | 381 |
| `Care` | 양육/관리 | 379 |
| `Health` | 건강/질병 | 341 |
| `General Info` | 상식/정보 | 189 |
| `Product` | 제품/용품 | 185 |
| `Nutrition` | 영양/식단 | 158 |
| `Living` | 생활/환경 | 91 |
| `Breeds` | 품종 | 67 |
| `Legal/Social` | 법률/사회 | 15 |
| `Farewell` | 이별/상실 | 6 |

> 다중 라벨이므로 합계는 총 문서 수(1,205)를 초과합니다.

### Specialists (전문가 매핑) — DB 실측 기준

| 전문가 | 역할 | 건수 |
| :--- | :--- | ---: |
| `Physician` | 건강/영양/의료 | 475 |
| `Peacekeeper` | 행동/갈등/교정 | 333 |
| `Liaison` | 입양/구조 | 222 |
| `Matchmaker` | 품종 추천/매칭 | 83 |
| `General Info` | 일반 정보 | 4 |

---

## 4. 도메인 사전 & 토큰화

### 사용자 사전
- **경로**: `src/core/tokenizer/domain_dictionary.txt`
- **총 용어 수**: 1,085개 (상위 1000 명사 + 67 품종명 + 의학 용어)
- **특징**:
  - **복합어 지원**: `벤토나이트`, `스크래쳐`, `아비시니안`
  - **불용어 처리**: 검색 품질을 위한 강화된 필터링

### 토큰화 성능 비교

| 사례 | 기본 토크나이저 | V3 커스텀 토크나이저 |
| :--- | :--- | :--- |
| **복합어** | `벤토` + `나이트` | `벤토나이트` (✅) |
| **품종명** | `메인` + `쿤` | `메인쿤` (✅) |
| **은어** | `맛` + `동산` | `맛동산` (✅) |

---

## 5. 인덱스 설정

**벡터 인덱스 (`vector_index`)**:
```json
{
  "fields": [
    { "numDimensions": 1536, "path": "embedding", "similarity": "cosine", "type": "vector" },
    { "path": "categories", "type": "filter" },
    { "path": "specialists", "type": "filter" },
    { "path": "filter_shedding", "type": "filter" },
    { "path": "filter_energy", "type": "filter" }
  ]
}
```

---

## 6. 파이프라인 아키텍처 (3단계 분리 구조)

V3 파이프라인은 `src/pipelines/v3/`에 위치한 3단계 분리 프로세스를 사용합니다.

### Stage 1: 전처리 (`preprocessor.py`)
- **입력**: 원본 JSON (`data/raw/bemypet_catlab.json`)
- **처리**: 텍스트 정제, UID 생성, Kiwi 도메인 사전 토큰화, LLM 메타데이터 추출
- **출력**: `data/v3/processed.json` (텍스트 전용, 벡터 미포함)
- **장점**: 임베딩 비용 없이 텍스트 처리를 빠르게 반복 가능

### Stage 2: 임베딩 (`embedder.py`)
- **입력**: `processed.json`
- **처리**: OpenAI `text-embedding-3-small`로 구조화 임베딩 생성
- **임베딩 대상**: `[Categories][Specialists] Title | Keywords | Summary` (본문 text 제외)
- **출력**: `data/v3/embedded.pkl` (Python Pickle)
- **장점**: 임베딩을 별도 저장하여 DB 재적재 시 API 호출 불필요

### Stage 3: 적재 (`loader.py`)
- **입력**: `embedded.pkl`
- **처리**: MongoDB `cat_library`로 비동기 일괄 upsert
- **장점**: 순수 IO 작업. 관심사 분리
