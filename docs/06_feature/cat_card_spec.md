# 고양이 카드 (Cat Card) 기능 명세

## 1. 개요
고양이 품종에 대한 상세 정보를 시각적으로 제공하는 UI 컴포넌트('고양이 카드')를 구현한다.
챗봇 대화 중 추천되거나 언급된 품종을 강조하고, 사용자 인터랙션(Hover) 시 카드를 노출하여 직관적인 정보를 전달한다.

## 2. 인터페이스 설계 (Extensibility)
향후 '사용자의 고양이' 정보도 동일한 UI 틀에서 보여줄 수 있도록, 공통 인터페이스(`CatCardSchema`)를 정의하여 구현한다.

### 2.1. 공통 스키마 (CatCard Interface)
모든 고양이 카드는 아래 데이터 구조를 따른다.
*   **Header**:
    *   `title` (이름/품종명)
    *   `subtitle` (부제/애칭/학명)
    *   `image_url` (대표 이미지)
*   **Body**:
    *   `tags` (특성 태그 리스트: 성격, 묘종 등)
    *   `description` (소개글)
    *   `stats` (시각화할 수치 데이터 Key-Value Map)
    *   `meta_info` (추가 정보: 출처, 생년월일 등)

### 2.2. 구현체 (Implementation Types)
*   **Type A: 품종 카드 (Breed Card)**
    *   **Data Source**: `cat_breeds_integrated.json`
    *   `title`: 품종명 (한글)
    *   `stats`: `adaptability`, `intelligence` 등 고정 스탯 방사형 차트.
*   **Type B: 마이 캣 카드 (User Cat Card)** *[Future]*
    *   **Data Source**: User DB (회원가입/프로필 입력 데이터)
    *   `title`: 고양이 이름 (예: "레오")
    *   `subtitle`: 품종 (예: "샴")
    *   `stats`: `health_status` (건강 상태), `age` 등 사용자 정의 수치 또는 D-Day(접종일) 시각화.

## 3. 데이터 소스 및 구현 (V3)
DB(`cat_library.care_guides`) 데이터를 매핑하며, `src/core/models/dtos.py`의 `CatCardRecommendation` 스펙을 따릅니다.

### 3.1. 매핑 상세
- **이미지 (Breed Image)**: `TheCatAPI` 고해상도 이미지 URL 전수 매칭 완료.
- **특성 (Traits)**: `personality_traits` 리스트를 해시태그(`#`) 형태로 변환하여 제공.
- **설명**: `summary` 필드 기반의 1문장 요약 제공.
- **스탯 (Stats) 시각화**: `stats` 필드의 17개 지표 중 핵심 수치를 별점(1-5)으로 시각화.

## 3. 기능 시나리오

### 3.1. 챗봇 연동 (Dual-Mode Response)
- **에이전트**: `Matchmaker Specialist`
- **응답 구성**: 
  - `text_response`: 친근한 고양이 말투의 상담 텍스트.
  - `recommendations`: `CatCardRecommendation` 객체 리스트 (1~3개).
- **UI 렌더링**: 프론트엔드에서 `state["recommendations"]`를 감지하여 HTML 템플릿에 데이터 주입 후 렌더링.

### 3.2. 카드 UI 구성 (Mock-up)
*   헤더: 품종 이름 및 대표 이미지.
*   바디:
    *   핵심 키워드 태그 (Traits).
    *   능력치 그래프 (Stats).
    *   간단한 설명.
