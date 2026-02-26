# 🐾 ZIPSA 개발 로그 (FACT CHECK) - 2026-02-02

오늘 진행된 모든 코드 수정 사항과 기술적 결정 요소를 팩트 중심으로 상세히 기록한다냥.

---

## 1. 헤더 환경 정보 표시 고도화
- **[app.py](../../src/ui/app.py)**: 
    - `get_profile_summary(p)` 함수를 신설하여 기존의 단순 텍스트 나열(🏠 아파트 · 🏃 보통)을 상세 레이블 방식(🏠 거주: 아파트 · 🏃 활동량: 보통)으로 전환.
    - 경력(`🎓`), 동거인(`👥`), 알레르기(`🚨`) 정보를 모두 포함하도록 로직 확장.
    - `st.session_state.summary`에 최종 문자열을 할당하여 헤더로 전달.
- **[header_view.html](../../src/ui/components/header_view.html)**:
    - `.header-left`에 `display: flex; align-items: center; gap: 1.2rem;`을 추가하여 로고와 요약 정보 박스를 수평 정렬.
    - `.header-summary`에 은은한 외곽선(`border`)과 패딩(`6px 16px`)을 추가하여 캡슐 디자인 적용.

## 2. 국가동물보호정보시스템 API 최적화
- **[animal_protection.py](../../src/agents/tools/animal_protection.py)**:
    - **타임아웃**: `_call_api`의 `timeout`을 `10` → `30`으로 상향. `httpx.ReadTimeout` 발생 시 사용자 친화적 메시지 반환 로직 추가.
    - **데이터 확보**: `numOfRows`를 `100` → `1000`으로 상향하여 광역 검색 시 누락 방지.
    - **검색 매개변수 선명화**: `sigungu`(발견지 지자체코드)와 `shelter_keyword`(보호소 이름/주소 필터링용)의 역할 구분.
- **[prompts.yaml](../../src/core/prompts/prompts.yaml)**:
    - `liaison` 에이전트 지침에 발견 장소와 현재 보호소 위치가 다를 경우를 설명하는 가이드라인 추가.

## 3. 채팅 UI 스타일 안정화
- **[base.html](../../src/ui/components/base.html)**:
    - 사용자 메시지 영역에 파스텔 배경색을 입히는 여러 차례의 시도가 있었으나, 스트림릿 기본 테마(`default light`)의 CSS 우선순위 충돌 및 정렬 문제 확인.
    - 집사님의 결정(1안)에 따라 **사용자 정의 채팅 CSS를 모두 제거**하고 스트림릿 순정 디자인으로 복구하여 UI 안정성 및 완벽한 수평 정렬 확보.

## 4. 전역 JSON/Reasoning 노출 차단 시스템
- **[head_butler.py](../../src/agents/head_butler.py)**:
    - `router.ainvoke` 호출 시 `config={"tags": ["router_classification"]}` 추가.
- **[care_team.py](../../src/agents/care_team.py)**:
    - 건강/행동 분류기 호출 시 동일한 `router_classification` 태그 부여.
- **[matchmaker.py](../../src/agents/matchmaker.py)**:
    - 품종 선정(BreedSelection)을 위한 `selector.ainvoke`에 태그 추가.
- **[liaison.py](../../src/agents/liaison.py)**:
    - 도구 호출 여부를 판단하는 LLM 호출에 태그 추가.
- **[utils.py](../../src/ui/utils.py)**:
    - `on_chat_model_stream` 핸들러에서 `event.get("tags")`를 검사하여 `router_classification`이 포함된 경우 `continue`로 스트리밍 중단 로직 구현. (내부 JSON 로그가 사용자 화면에 노출되는 근본 원인 차단)

## 5. 그래프 아키텍처 및 시각화
- **[graph.py](../../src/agents/graph.py)**:
    - `Command` 기반의 동적 라우팅과 별개로, 시각화 명확성을 위해 정적 엣지(Static Edge) 정의를 유지하도록 주석 및 구조 보완.
- **[zipsa_graph_structure.png](../../docs/assets/zipsa_graph_structure.png)**:
    - LangGraph의 내장 Mermaid 렌더러를 활용하여 현재 코드 구조(`app.get_graph().draw_mermaid_png()`)와 100% 일치하는 최신 아키텍처 다이어그램 자동 생성 및 교체.

## 6. 리소스 정리
- **[static/](../../static/)**:
    - TheCatAPI 등 외부 CDN 이미지를 적극 활용함에 따라 로컬 불필요 리소스 폴더 삭제.

## 7. Matchmaker 검색 의도 분류 (Intent Classification)
- **[matchmaker.py](../../src/agents/matchmaker.py)**:
    - 사용자의 질문이 **단순 조회(LOOKUP)**인지 **추천 요청(RECOMMEND)**인지 먼저 판단하는 로직 추가.
    - LOOKUP: 사용자 프로필(거주환경 등)을 검색어에서 배제하여 "메인쿤" 등 특정 품종 검색 시 왜곡 방지.
    - RECOMMEND: 기존처럼 사용자 프로필을 반영하여 맞춤형 추천.
    - SEARCH: **[CASE 3] 미등록 품종 대응** 추가. Selector가 빈 리스트를 반환하면 "해당 품종이 없습니다" 시그널을 보내, Head Butler가 "모르는 고양이다냥"으로 답변하도록 유도.
- **[core/models/matchmaker.py](../../src/core/models/matchmaker.py)** (신규):
    - `SearchIntent` 및 `BreedSelection` DTO를 별도 파일로 분리하여 관리.

---
## 8. 개발 환경 개선 (Jupyter Notebook)
- **[.gitattributes](../../.gitattributes)**: `*.ipynb filter=nbstripout` 설정 추가.
- **[requirements.txt](../../requirements.txt)**: `nbstripout` 패키지 추가.
- **효과**: 주피터 노트북 실행 시 생성되는 Output Cell이나 메타데이터 변경을 git 추적에서 자동 제외하여 커밋 노이즈 제거.

---
## 9. Retriever 모듈화 및 테스트 환경 구축
- **[src/retrieval/](../../src/retrieval/)**:
    - `bm25_retriever.py`: `HybridRetriever`의 키워드 검색 로직 분리 및 단독 실행 모듈 구현.
    - `vector_retriever.py`: 벡터 검색 로직 분리 및 단독 실행 모듈 구현.
- **[src/notebooks/](../../src/notebooks/)** (신규/분리):
    - `test_bm25.ipynb`: 키워드 매칭, 토크나이저, 필터링 기능 단독 테스트.
    - `test_vector.ipynb`: 의미론적 유사도 검색 및 미등록 품종 동작 패턴 분석.
    - `analysis_retrieval_metrics.ipynb`: Ground Truth(정답셋) 기반 Hit@k 정확도 측정 및 RRF 성능 비교 분석.

---
**보고자: 수석 집사 ZIPSA** (2026-02-02)
