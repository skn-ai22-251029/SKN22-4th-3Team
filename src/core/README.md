# 🎯 Core Module (`src/core/`)

프로젝트의 중앙 집중식 설정, 데이터 모델, 프롬프트 관리, 그리고 도메인 특화 토크나이저를 관리하는 핵심 모듈입니다.

---

## 📂 Directory Structure

```
src/core/
├── config.py              # 환경 설정 및 버전 정책 관리
├── models/                # 데이터 모델 (DTOs)
│   ├── user_profile.py    # 사용자 프로필 DTO (타입 안전성)
│   └── cat_card.py        # UI 카드 렌더링 DTO
├── prompts/               # 중앙 집중식 프롬프트 관리
│   ├── prompts.yaml       # 모든 에이전트 페르소나 및 시스템 프롬프트
│   └── prompt_manager.py  # 동적 프롬프트 로딩 엔진 (Singleton)
└── tokenizer/             # 도메인 특화 형태소 분석
    ├── domain_dictionary.txt  # Kiwi용 사용자 사전 (~1,100개 용어)
    ├── extra_nouns.txt         # 추가 명사 소스
    ├── stopwords.txt           # 한국어 검색 제외어
    └── synonyms.json           # 동의어 정규화 사전
```

---

## 1. Configuration (`config.py`)

### ZipsaConfig (Singleton)
프로젝트 전역 설정을 관리하는 싱글톤 객체입니다.

```python
from src.core.config import ZipsaConfig

config = ZipsaConfig()
version = config.get_version()  # "v3"
db_name = config.get_db_name()  # "cat_library"
```

### VersionPolicy
V1/V2/V3 각 버전별 데이터베이스, 컬렉션, 파일 경로를 정의합니다.

**주요 필드**:
- `version`: 버전 식별자 ("v1", "v2", "v3")
- `db_name`: MongoDB 데이터베이스 이름
- `collection_name`: 기본 컬렉션 이름 (V3: `"care_guides"`)
- `categories`: 아티클 분류 체계
- `specialists`: 전문가 페르소나 매핑

### LLMConfig
LLM 모델 사용 전략을 중앙에서 정의합니다. 비용 최적화를 위해 **Dual-Model Strategy**를 채택했습니다.

- **`ROUTER_MODEL`**: `gpt-4.1-nano` (초경량)
  - 용도: 의도 분류, 구조화된 출력(Structured Output), 라우팅 의사결정.
- **`BASIC_MODEL`**: `gpt-4o-mini` (범용)
  - 용도: 텍스트 요약(Distillation), 일반 대화 생성, 최종 응답 합성.

---

## 2. Data Models (`models/`)

### 2.1. UserProfile (`user_profile.py`)
**목적**: 사용자 프로필 데이터의 타입 안정성 및 검증 제공

**핵심 기능**:
```python
from src.core.models.user_profile import UserProfile

# DTO 생성
profile = UserProfile(
    housing="apartment",
    activity="low",
    allergy=True,
    has_children=True
)

# LLM 컨텍스트 문자열 생성
context = profile.to_context_string()

# 안전 제약 추출 (Hard Constraints)
filters = profile.get_hard_constraints()
# → {"hypoallergenic": 1, "child_friendly": 4}

# 레거시 Dict 호환성
profile = UserProfile.from_dict(legacy_dict)
```

**제약 분류**:
- **Hard Constraints**: 알레르기, 아이 있음, 개 있음 (건강/안전)
- **Soft Preferences**: 활동량, 경험 (순위 영향)
- **Context**: 선호 성향 (검색 문맥)

### 2.2. CatCard (`cat_card.py`)
**목적**: UI 카드 렌더링을 위한 구조화된 데이터

**모델**:
- `CatCardStats`: 품종 통계 (17개 지표, 1-5 스케일)
- `CatCardRecommendation`: 카드 데이터 (이름, 이미지, 요약, 태그, 통계)

---

## 3. Prompts (`prompts/`)

### 3.1. Central Prompt Repository (`prompts.yaml`)
모든 에이전트의 **페르소나**, **시스템 프롬프트**, **Few-Shot 예제**를 중앙에서 관리합니다.

**구조**:
```yaml
head_butler:
  persona: "당신은 ZIPSA 서비스의 수석 집사입니다..."
  system: "사용자의 의도를 파악하고..."

matchmaker:
  persona: "당신은 품종 매칭 전문가입니다..."
  system: "프로필 기반으로 최적의 품종을 추천하세요..."
```

**장점**:
- ✅ **서비스 재시작 불필요**: YAML 수정만으로 즉시 반영
- ✅ **버전 관리**: Git으로 프롬프트 변경 이력 추적
- ✅ **A/B 테스팅**: 쉬운 프롬프트 실험

### 3.2. Prompt Manager (`prompt_manager.py`)
**싱글톤 패턴**으로 YAML을 로드하고 캐싱합니다.

```python
from src.core.prompts.prompt_manager import prompt_manager

# 전체 프롬프트 가져오기
full_prompt = prompt_manager.get_prompt("matchmaker")

# 특정 필드만 가져오기
persona = prompt_manager.get_prompt("matchmaker", field="persona")
```

**핵심 기능**:
- 파일 감시 (자동 리로드)
- 템플릿 변수 지원 (`.format()` 호환)
- 에러 핸들링 (기본값 반환)

---

## 4. Tokenizer (`tokenizer/`)

### 4.1. Domain Dictionary (`domain_dictionary.txt`)
**Kiwi 형태소 분석기**용 도메인 특화 사전입니다.

**구성**:
- **Top 1000 명사**: 빈도 분석 기반
- **67개 품종명**: "메인쿤", "아비시니안" 등
- **의료 용어**: "췌장염", "비뇨기" 등

**효과**:
```
기본 토크나이저: "메인" + "쿤" (❌)
도메인 사전:     "메인쿤" (✅)
```

### 4.2. Synonyms (`synonyms.json`)
품종 명칭 및 특성어의 동의어 매핑입니다.

```json
{
  "아메리칸 쇼트헤어": ["아숏", "아메숏", "American Shorthair"],
  "활발한": ["활동적인", "에너지 넘치는", "우다다"]
}
```

### 4.3. Stopwords (`stopwords.txt`)
검색 품질 향상을 위한 제외어 리스트입니다.

---

## 🔧 Usage Examples

### 전체 워크플로우
```python
# 1. Config 로드
from src.core.config import ZipsaConfig
config = ZipsaConfig()

# 2. 사용자 프로필 생성
from src.core.models.user_profile import UserProfile
profile = UserProfile.from_dict(user_input)

# 3. 프롬프트 로드
from src.core.prompts.prompt_manager import prompt_manager
persona = prompt_manager.get_prompt("matchmaker", field="persona")

# 4. 안전 제약 추출
hard_filters = profile.get_hard_constraints()

# 5. LLM에 컨텍스트 전달
context = profile.to_context_string()
```

---

## 🎯 Design Principles

### 1. 중앙 집중화 (Centralization)
- 모든 설정, 프롬프트, 데이터 모델이 한 곳에
- 변경 시 단일 지점 수정

### 2. 타입 안정성 (Type Safety)
- Pydantic 기반 DTO로 런타임 에러 방지
- IDE 자동완성 및 타입 체크 지원

### 3. 분리 가능성 (Separation of Concerns)
- 설정(config) / 데이터(models) / 프롬프트(prompts) / 토크나이저(tokenizer) 명확히 분리
- 각 모듈이 독립적으로 테스트 가능

### 4. 확장 가능성 (Extensibility)
- 새 버전 추가: `VersionPolicy` 정의만으로 가능
- 새 DTO 추가: `models/` 디렉토리에 파일 추가
- 새 에이전트 추가: `prompts.yaml`에 섹션 추가

---

## 📝 Maintenance Notes

### Config 변경 시
- `config.py`의 `VersionPolicy` 수정
- 데이터베이스 마이그레이션 스크립트 실행

### Prompt 변경 시
- `prompts/prompts.yaml` 수정
- **서비스 재시작 불필요** (자동 리로드)

### DTO 추가 시
1. `models/` 디렉토리에 새 파일 생성
2. Pydantic BaseModel 상속
3. 필드별 `Field()` 설명 추가

### 도메인 사전 갱신 시
- `scripts/build_domain_dict.py` 실행
- `tokenizer/domain_dictionary.txt` 자동 업데이트
